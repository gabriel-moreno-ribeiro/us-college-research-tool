# Deployment Guide — BYOK Remote Connector

This MCP server now supports **Bring Your Own Key (BYOK)** architecture for deployment as a remote HTTP connector.

## Architecture

The server operates in two modes:

1. **stdio mode** (default): Local development, reads API keys from environment variables
2. **http mode**: Remote connector, accepts API keys via HTTP headers (BYOK)

## Security Features

### API Key Handling
- Keys exist **only in memory** during request processing (contextvars)
- Keys are **never logged** (redacting filter installed on all loggers)
- Keys are **never persisted** to disk or cache
- Keys are **never echoed** in error messages
- Cache keys derived from query parameters only, never from credentials

### Rate Limiting
- 60 requests per minute per IP address
- 429 response with `Retry-After` header when exceeded
- Health check endpoint exempt from rate limiting

### Source Tracking
- Records URLs consulted during research (for NotebookLM export)
- Stores: URL, title, university, category, timestamp, domain classification
- **No user identification data** is stored
- SQLite database: `data/sources.db`

## HTTP Mode Configuration

### Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `MCP_TRANSPORT` | Yes | Set to `http` for HTTP mode |
| `PORT` | No | Port to bind (default: 8000) |
| `COLLEGE_SCORECARD_API_KEY` | No* | Fallback for local testing |
| `SEMANTIC_SCHOLAR_API_KEY` | No | Fallback for local testing |

*In production HTTP mode, clients must send keys via headers. Env var fallback is for local stdio development only.

### BYOK Headers

Clients send API keys via HTTP headers:

```
X-College-Scorecard-Key: <user's College Scorecard API key>
X-Semantic-Scholar-Key: <user's Semantic Scholar API key>
```

The Scorecard key is **required** for most tools. Semantic Scholar key is optional (but recommended for higher rate limits).

### User Instructions

When a user receives a `NOT_CONFIGURED` error for missing Scorecard key, they see:

```
COLLEGE_SCORECARD_API_KEY not provided. To use this tool:
1. Get a free API key at https://api.data.gov/signup/
2. Add it as the X-College-Scorecard-Key header in your connector configuration.
For local development, set COLLEGE_SCORECARD_API_KEY in your .env file.
```

## Deployment Options

### Option 1: Render.com (PaaS)

1. Push to GitHub
2. Connect Render to your repo
3. Render auto-detects `render.yaml`:
   ```yaml
   services:
     - type: web
       name: us-college-research-mcp
       runtime: python
       buildCommand: pip install -r requirements.txt
       startCommand: python -m mcp_server
       healthCheckPath: /health
       envVars:
         - key: MCP_TRANSPORT
           value: http
         - key: PYTHON_VERSION
           value: "3.13"
       plan: free
   ```
4. Render provisions the service at `https://<your-app>.onrender.com`

**Health check**: `GET /health` returns `{"status": "ok"}`

### Option 2: Docker (self-hosted)

Build:
```bash
docker build -t us-college-research-mcp .
```

Run:
```bash
docker run -d \
  -p 8000:8000 \
  -e MCP_TRANSPORT=http \
  us-college-research-mcp
```

The server listens on `0.0.0.0:8000`.

### Option 3: Uvicorn (bare metal / VM)

```bash
pip install -r requirements.txt
export MCP_TRANSPORT=http
export PORT=8000
python -m mcp_server
```

Or with uvicorn directly:
```bash
MCP_TRANSPORT=http uvicorn mcp_server.http_app:app --host 0.0.0.0 --port 8000
```

## Testing the Deployment

### Health Check
```bash
curl https://your-deployment.com/health
# Expected: {"status":"ok"}
```

### MCP Request (with BYOK)
```bash
curl -X POST https://your-deployment.com/mcp \
  -H "Content-Type: application/json" \
  -H "X-College-Scorecard-Key: YOUR_SCORECARD_KEY" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "search_university",
      "arguments": {"query": "MIT"}
    }
  }'
```

### Rate Limit Test
Send 61+ requests from same IP within 60 seconds:
```bash
for i in {1..65}; do
  curl https://your-deployment.com/health
done
# Expected: 429 after request #61
```

## Claude.ai Custom Connector Setup

1. Go to Claude.ai → Settings → Connectors
2. Add Remote Connector
3. URL: `https://your-deployment.com`
4. Add secrets:
   - Name: `X-College-Scorecard-Key`
   - Value: (user's Scorecard key)
   - Name: `X-Semantic-Scholar-Key` (optional)
   - Value: (user's SS key)

Claude passes these secrets as HTTP headers with every MCP request.

## Local Development (stdio mode)

For local testing with Claude Desktop or MCP Inspector:

1. Create `.env`:
   ```
   COLLEGE_SCORECARD_API_KEY=your_key_here
   SEMANTIC_SCHOLAR_API_KEY=your_key_here
   ```

2. Run in stdio mode (default):
   ```bash
   python -m mcp_server
   ```

3. Or test HTTP mode locally:
   ```bash
   MCP_TRANSPORT=http PORT=8000 python -m mcp_server
   ```

## Monitoring

### Logs
- Logs go to stderr (stdout reserved for JSON-RPC in stdio mode)
- API keys are redacted by `KeyRedactingFilter`
- Log level: INFO (configurable in `mcp_server/server.py`)

### Source Tracking
Export consulted URLs for audit or NotebookLM import:

CLI:
```bash
python main.py --export-sources
```

MCP tool:
```json
{
  "method": "tools/call",
  "params": {
    "name": "export_sources",
    "arguments": {
      "university": "Northwestern University",
      "official_only": true
    }
  }
}
```

Output files (in `output/sources/`):
- `urls.txt` — plain list
- `urls-oficiais.txt` — only .edu domains
- `fontes.md` — formatted Markdown with metadata

## Troubleshooting

### "COLLEGE_SCORECARD_API_KEY not provided"
- **HTTP mode**: User must add the key as connector secret in Claude.ai
- **stdio mode**: Set in `.env` file

### Rate limit 429
- Wait `Retry-After` seconds (header provided)
- Rate limit is per-IP, not per-user

### Source tracking not recording
- Check that `data/sources.db` is writable
- Verify source_tracker is imported and `record_source()` called
- Check logs for SQLite errors

### Health check fails
- Verify `MCP_TRANSPORT=http` is set
- Check port binding (Docker/firewall)
- Review Render/deployment logs

## Migration from Environment Variables

If you have existing code that reads `COLLEGE_SCORECARD_API_KEY` from env:

1. **No breaking changes** — env var fallback is preserved for stdio mode
2. In HTTP mode, the BYOK context takes precedence
3. Clients calling via HTTP **must** send headers; env vars are ignored

## Contributing

When adding new data sources that require API keys:

1. Add key extraction in `mcp_server/key_context.py`
2. Add middleware header parsing in `mcp_server/http_app.py`
3. Update client class to check BYOK context first, env var second
4. Add `record_source()` calls for source tracking
5. Register sensitive patterns with `KeyRedactingFilter`
6. Document the new header in this guide

## License

Same as parent project (see main README.md).
