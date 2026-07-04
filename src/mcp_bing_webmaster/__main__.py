"""Entry point: `mcp-bing-webmaster` runs the server over stdio."""

from __future__ import annotations

from .server import mcp


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
