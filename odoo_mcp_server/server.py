# server.py
import asyncio
from typing import Dict, Any, List, Optional
import mcp.types as types
from mcp.server import Server, InitializationOptions, NotificationOptions
import sys

from tool_definitions import get_all_tools
from filesystem_tools import FileSystemTools
from odoo_tools import OdooTools
from odoo_connector import OdooConnector

class UnifiedServer:
    def __init__(self):
        self.server = Server("odoo")
        
        # Inicialize FileSystemTools
        self.fs_tools = FileSystemTools()
        
        # Initialize OdooTools with OdooConnector
        odoo_connector: Optional[OdooConnector] = None
        try:
            odoo_connector = OdooConnector()
            if odoo_connector and odoo_connector.uid:
                print(f"✅ Odoo connection OK. UID: {odoo_connector.uid}", file=sys.stderr)
        except FileNotFoundError:
            print("⚠️ Odoo config not found. Use 'configure_odoo' tool.", file=sys.stderr)
        
        self.odoo_tools = OdooTools(odoo_connector)
        
        # Set up the server handlers
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """Provides Claude with the list of available tools."""
            return get_all_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """
            The main router. It receives a tool call from Claude and directs it
            to the correct implementation in the appropriate module.
            """
            # --- Filesystem Tools ---
            if name == "read_file":
                return await self.fs_tools.read_file(arguments)
            elif name == "write_file":
                return await self.fs_tools.write_file(arguments)
            elif name == "append_file":
                return await self.fs_tools.append_file(arguments)
            elif name == "list_directory":
                return await self.fs_tools.list_directory(arguments)
            elif name == "create_directory":
                return await self.fs_tools.create_directory(arguments)
            elif name == "delete_file":
                return await self.fs_tools.delete_file(arguments)
            elif name == "move_file":
                return await self.fs_tools.move_file(arguments)
            elif name == "copy_file":
                return await self.fs_tools.copy_file(arguments)
            elif name == "file_info":
                return await self.fs_tools.file_info(arguments)
            elif name == "search_files":
                return await self.fs_tools.search_files(arguments)
            elif name == "find_text":
                return await self.fs_tools.find_text(arguments)
            
            # --- Odoo Tools ---
            elif name == "configure_odoo":
                return await self.odoo_tools.configure_odoo(arguments)
            elif name == "get_contact_info":
                return await self.odoo_tools.get_contact_info(arguments)
            
            # --- Fallback for unknown tools ---
            else:
                raise ValueError(f"ERROR: The tool '{name}' is not recognized by the server.")

    async def run(self, read_stream, write_stream):
        await self.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="odoo",
                server_version="1.0.0",
                capabilities=self.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )