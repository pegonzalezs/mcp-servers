# main.py
import asyncio
import mcp.server.stdio
from server import UnifiedServer

async def main():
    server = UnifiedServer()
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())