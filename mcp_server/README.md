# US College Research Tool — MCP Server

MCP server that exposes university research capabilities as tools for Claude.

## Tools Available

### Discovery
| Tool | Purpose |
|------|---------|
| `search_university` | Find US universities by name, see data coverage |
| `list_configured_departments` | Which departments have faculty configs ready |

### Institutional Data
| Tool | Purpose |
|------|---------|
| `get_university_overview` | College Scorecard: admissions, cost, outcomes (with provenance) |
| `get_opportunities` | Incubators, research programs, clubs (curated) |
| `get_alumni_research_links` | Pre-filtered LinkedIn Alumni Tool URLs (no scraping) |
| `get_career_outcomes` | Aggregate post-graduation data from official reports |

### Faculty & Research
| Tool | Purpose |
|------|---------|
| `list_faculty` | Paginated faculty list from a configured department |
| `get_professor_research` | ORCID + Semantic Scholar lookup with confidence level |
| `match_professors_to_interests` | Rank professors by relevance to your interests |

### Consolidation
| Tool | Purpose |
|------|---------|
| `generate_full_report` | Full pipeline, saves to file |
| `compare_universities` | Side-by-side comparison table |

### Scaling
| Tool | Purpose |
|------|---------|
| `draft_faculty_config` | Auto-propose CSS selectors for a new university |
| `validate_faculty_config` | Test if a config still works |

## Installation

### Prerequisites

```bash
cd us-college-research-tool
pip install -r requirements.txt
pip install "mcp[cli]>=2.0,<3.0"
```

### Environment Variables

Create a `.env` file or pass as env vars:

```bash
# Required for College Scorecard tools
COLLEGE_SCORECARD_API_KEY=your_key_here  # Free: https://api.data.gov/signup/

# Optional (increases Semantic Scholar rate limit)
SEMANTIC_SCHOLAR_API_KEY=your_key_here  # Free: https://www.semanticscholar.org/product/api#api-key-form
```

### Register with Claude Code

```bash
# From the project directory:
claude mcp add --scope project us-college-research -- python -m mcp_server
```

Or add to `.mcp.json` in the project root:

```json
{
  "mcpServers": {
    "us-college-research": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": ".",
      "env": {
        "COLLEGE_SCORECARD_API_KEY": "${COLLEGE_SCORECARD_API_KEY}"
      }
    }
  }
}
```

### Register with Claude Desktop

Add to `%AppData%\Claude\claude_desktop_config.json` (Windows) or
`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "us-college-research": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "C:\\path\\to\\us-college-research-tool",
      "env": {
        "COLLEGE_SCORECARD_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Test with MCP Inspector

```bash
cd us-college-research-tool
python -m mcp dev mcp_server/server.py
```

## Running the Smoke Test

```bash
python scripts/smoke_test_mcp.py
```

Requires `COLLEGE_SCORECARD_API_KEY` set for full coverage.

## Design Principles

1. **Progressive disclosure**: `search_university` first (cheap), then drill down.
2. **Context budget**: responses are structured data under 10k tokens. `generate_full_report` can return just a file path.
3. **Provenance**: every data field carries its source and reference year.
4. **Error taxonomy**: `NOT_FOUND`, `NOT_CONFIGURED`, `OUT_OF_SCOPE`, `UPSTREAM_ERROR`, `RATE_LIMITED`, `AMBIGUOUS`.
5. **No invented data**: missing = missing, never filled with estimates.
6. **Confidence tracking**: `identification_confidence: high|low` on professor lookups.
7. **Cache-first**: all API calls go through SQLite cache to avoid rate limits.
8. **Stdout purity**: no `print()` in any code path — stdio transport safe.
