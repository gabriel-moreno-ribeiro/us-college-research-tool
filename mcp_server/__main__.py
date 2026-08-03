"""Entrypoint: python -m mcp_server"""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
