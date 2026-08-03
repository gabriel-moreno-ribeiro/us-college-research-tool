"""Entrypoint: python -m mcp_server"""
import os

transport = os.environ.get("MCP_TRANSPORT", "stdio")

if __name__ == "__main__":
    if transport == "http":
        import uvicorn
        from .http_app import create_app
        app = create_app()
        host = "0.0.0.0"
        port = int(os.environ.get("PORT", "8000"))
        uvicorn.run(app, host=host, port=port, log_level="info")
    else:
        from .server import mcp
        mcp.run()
