#!/usr/bin/env python3

import asyncio
import json
import os
import sys
import glob
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio


class FileSystemMCPServer:
    def __init__(self):
        self.server = Server("filesystem-mcp-server")
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available filesystem tools."""
            return [
                types.Tool(
                    name="read_file",
                    description="Read the contents of a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to read"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                types.Tool(
                    name="write_file",
                    description="Write content to a file (creates or overwrites)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to write"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                ),
                types.Tool(
                    name="append_file",
                    description="Append content to a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to append to"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to append to the file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                ),
                types.Tool(
                    name="list_directory",
                    description="List contents of a directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Path to the directory to list"
                            },
                            "include_hidden": {
                                "type": "boolean",
                                "description": "Include hidden files (starting with .)",
                                "default": False
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "List files recursively",
                                "default": False
                            }
                        },
                        "required": ["directory_path"]
                    }
                ),
                types.Tool(
                    name="create_directory",
                    description="Create a directory (including parent directories)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Path to the directory to create"
                            }
                        },
                        "required": ["directory_path"]
                    }
                ),
                types.Tool(
                    name="delete_file",
                    description="Delete a file or directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file or directory to delete"
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Delete directories recursively",
                                "default": False
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                types.Tool(
                    name="move_file",
                    description="Move or rename a file or directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_path": {
                                "type": "string",
                                "description": "Source path of the file or directory"
                            },
                            "destination_path": {
                                "type": "string",
                                "description": "Destination path"
                            }
                        },
                        "required": ["source_path", "destination_path"]
                    }
                ),
                types.Tool(
                    name="copy_file",
                    description="Copy a file or directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_path": {
                                "type": "string",
                                "description": "Source path of the file or directory"
                            },
                            "destination_path": {
                                "type": "string",
                                "description": "Destination path"
                            }
                        },
                        "required": ["source_path", "destination_path"]
                    }
                ),
                types.Tool(
                    name="file_info",
                    description="Get detailed information about a file or directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file or directory"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                types.Tool(
                    name="search_files",
                    description="Search for files by name pattern",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Directory to search in"
                            },
                            "pattern": {
                                "type": "string",
                                "description": "Pattern to match (supports wildcards * and ?)"
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Search recursively in subdirectories",
                                "default": True
                            }
                        },
                        "required": ["directory_path", "pattern"]
                    }
                ),
                types.Tool(
                    name="find_text",
                    description="Search for text content within files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Directory to search in"
                            },
                            "search_text": {
                                "type": "string",
                                "description": "Text to search for"
                            },
                            "file_pattern": {
                                "type": "string",
                                "description": "File pattern to limit search (e.g., '*.py')",
                                "default": "*"
                            },
                            "case_sensitive": {
                                "type": "boolean",
                                "description": "Case sensitive search",
                                "default": False
                            }
                        },
                        "required": ["directory_path", "search_text"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle tool calls."""
            try:
                if name == "read_file":
                    return await self._read_file(arguments)
                elif name == "write_file":
                    return await self._write_file(arguments)
                elif name == "append_file":
                    return await self._append_file(arguments)
                elif name == "list_directory":
                    return await self._list_directory(arguments)
                elif name == "create_directory":
                    return await self._create_directory(arguments)
                elif name == "delete_file":
                    return await self._delete_file(arguments)
                elif name == "move_file":
                    return await self._move_file(arguments)
                elif name == "copy_file":
                    return await self._copy_file(arguments)
                elif name == "file_info":
                    return await self._file_info(arguments)
                elif name == "search_files":
                    return await self._search_files(arguments)
                elif name == "find_text":
                    return await self._find_text(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _read_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Read file contents."""
        file_path = Path(args["file_path"]).resolve()
        
        if not file_path.exists():
            return [types.TextContent(type="text", text=f"Error: File does not exist: {file_path}")]
        
        if not file_path.is_file():
            return [types.TextContent(type="text", text=f"Error: Path is not a file: {file_path}")]
        
        try:
            content = file_path.read_text(encoding='utf-8')
            return [types.TextContent(
                type="text", 
                text=f"File: {file_path}\nSize: {file_path.stat().st_size} bytes\n\n{content}"
            )]
        except UnicodeDecodeError:
            # Try to read as binary and show info
            size = file_path.stat().st_size
            return [types.TextContent(
                type="text",
                text=f"File: {file_path}\nSize: {size} bytes\nNote: File appears to be binary and cannot be displayed as text."
            )]

    async def _write_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Write content to file."""
        file_path = Path(args["file_path"]).resolve()
        content = args["content"]
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_path.write_text(content, encoding='utf-8')
        return [types.TextContent(type="text", text=f"Successfully wrote {len(content)} characters to: {file_path}")]

    async def _append_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Append content to file."""
        file_path = Path(args["file_path"]).resolve()
        content = args["content"]
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        return [types.TextContent(type="text", text=f"Successfully appended {len(content)} characters to: {file_path}")]

    async def _list_directory(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """List directory contents."""
        directory_path = Path(args["directory_path"]).resolve()
        include_hidden = args.get("include_hidden", False)
        recursive = args.get("recursive", False)
        
        if not directory_path.exists():
            return [types.TextContent(type="text", text=f"Error: Directory does not exist: {directory_path}")]
        
        if not directory_path.is_dir():
            return [types.TextContent(type="text", text=f"Error: Path is not a directory: {directory_path}")]
        
        items = []
        
        def scan_directory(path: Path, depth: int = 0):
            try:
                for item in sorted(path.iterdir()):
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    
                    indent = "  " * depth
                    stat = item.stat()
                    size = stat.st_size if item.is_file() else None
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    item_type = "📁" if item.is_dir() else "📄"
                    size_str = f" ({size} bytes)" if size is not None else ""
                    
                    items.append(f"{indent}{item_type} {item.name}{size_str} - {modified}")
                    
                    if recursive and item.is_dir() and depth < 10:  # Limit recursion depth
                        scan_directory(item, depth + 1)
            except PermissionError:
                items.append(f"{indent}❌ Permission denied")
        
        scan_directory(directory_path)
        
        result = f"Directory: {directory_path}\n\n" + "\n".join(items)
        return [types.TextContent(type="text", text=result)]

    async def _create_directory(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Create directory."""
        directory_path = Path(args["directory_path"]).resolve()
        
        directory_path.mkdir(parents=True, exist_ok=True)
        return [types.TextContent(type="text", text=f"Successfully created directory: {directory_path}")]

    async def _delete_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Delete file or directory."""
        file_path = Path(args["file_path"]).resolve()
        recursive = args.get("recursive", False)
        
        if not file_path.exists():
            return [types.TextContent(type="text", text=f"Error: Path does not exist: {file_path}")]
        
        if file_path.is_file():
            file_path.unlink()
            return [types.TextContent(type="text", text=f"Successfully deleted file: {file_path}")]
        elif file_path.is_dir():
            if recursive:
                shutil.rmtree(file_path)
                return [types.TextContent(type="text", text=f"Successfully deleted directory recursively: {file_path}")]
            else:
                try:
                    file_path.rmdir()
                    return [types.TextContent(type="text", text=f"Successfully deleted empty directory: {file_path}")]
                except OSError:
                    return [types.TextContent(type="text", text=f"Error: Directory not empty. Use recursive=true to delete: {file_path}")]

    async def _move_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Move or rename file/directory."""
        source_path = Path(args["source_path"]).resolve()
        destination_path = Path(args["destination_path"]).resolve()
        
        if not source_path.exists():
            return [types.TextContent(type="text", text=f"Error: Source path does not exist: {source_path}")]
        
        # Create parent directories if they don't exist
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(source_path), str(destination_path))
        return [types.TextContent(type="text", text=f"Successfully moved {source_path} to {destination_path}")]

    async def _copy_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Copy file or directory."""
        source_path = Path(args["source_path"]).resolve()
        destination_path = Path(args["destination_path"]).resolve()
        
        if not source_path.exists():
            return [types.TextContent(type="text", text=f"Error: Source path does not exist: {source_path}")]
        
        # Create parent directories if they don't exist
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        if source_path.is_file():
            shutil.copy2(source_path, destination_path)
        else:
            shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
        
        return [types.TextContent(type="text", text=f"Successfully copied {source_path} to {destination_path}")]

    async def _file_info(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Get file information."""
        file_path = Path(args["file_path"]).resolve()
        
        if not file_path.exists():
            return [types.TextContent(type="text", text=f"Error: Path does not exist: {file_path}")]
        
        stat = file_path.stat()
        
        info = {
            "path": str(file_path),
            "name": file_path.name,
            "type": "directory" if file_path.is_dir() else "file",
            "size": stat.st_size,
            "size_human": self._human_readable_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "accessed": datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
            "permissions": oct(stat.st_mode)[-3:],
            "owner_readable": bool(stat.st_mode & 0o400),
            "owner_writable": bool(stat.st_mode & 0o200),
            "owner_executable": bool(stat.st_mode & 0o100),
        }
        
        if file_path.is_dir():
            try:
                items = list(file_path.iterdir())
                info["item_count"] = len(items)
            except PermissionError:
                info["item_count"] = "Permission denied"
        
        result = f"File Information:\n\n{json.dumps(info, indent=2)}"
        return [types.TextContent(type="text", text=result)]

    async def _search_files(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Search for files by pattern."""
        directory_path = Path(args["directory_path"]).resolve()
        pattern = args["pattern"]
        recursive = args.get("recursive", True)
        
        if not directory_path.exists():
            return [types.TextContent(type="text", text=f"Error: Directory does not exist: {directory_path}")]
        
        if not directory_path.is_dir():
            return [types.TextContent(type="text", text=f"Error: Path is not a directory: {directory_path}")]
        
        matches = []
        
        if recursive:
            search_pattern = str(directory_path / "**" / pattern)
            matches = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = str(directory_path / pattern)
            matches = glob.glob(search_pattern)
        
        if not matches:
            return [types.TextContent(type="text", text=f"No files found matching pattern '{pattern}' in {directory_path}")]
        
        # Sort and format results
        matches.sort()
        results = []
        for match in matches:
            path = Path(match)
            if path.is_file():
                size = self._human_readable_size(path.stat().st_size)
                results.append(f"📄 {match} ({size})")
            else:
                results.append(f"📁 {match}")
        
        result = f"Found {len(matches)} matches for pattern '{pattern}':\n\n" + "\n".join(results)
        return [types.TextContent(type="text", text=result)]

    async def _find_text(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Search for text within files."""
        directory_path = Path(args["directory_path"]).resolve()
        search_text = args["search_text"]
        file_pattern = args.get("file_pattern", "*")
        case_sensitive = args.get("case_sensitive", False)
        
        if not directory_path.exists():
            return [types.TextContent(type="text", text=f"Error: Directory does not exist: {directory_path}")]
        
        matches = []
        search_pattern = str(directory_path / "**" / file_pattern)
        files = glob.glob(search_pattern, recursive=True)
        
        search_term = search_text if case_sensitive else search_text.lower()
        
        for file_path in files:
            path = Path(file_path)
            if not path.is_file():
                continue
            
            try:
                content = path.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                file_matches = []
                for line_num, line in enumerate(lines, 1):
                    check_line = line if case_sensitive else line.lower()
                    if search_term in check_line:
                        file_matches.append(f"  Line {line_num}: {line.strip()}")
                
                if file_matches:
                    matches.append(f"📄 {file_path}:")
                    matches.extend(file_matches[:5])  # Limit to first 5 matches per file
                    if len(file_matches) > 5:
                        matches.append(f"  ... and {len(file_matches) - 5} more matches")
                    matches.append("")  # Empty line between files
                    
            except (UnicodeDecodeError, PermissionError):
                continue  # Skip binary files or files without permission
        
        if not matches:
            return [types.TextContent(type="text", text=f"No text matches found for '{search_text}' in {directory_path}")]
        
        result = f"Text search results for '{search_text}':\n\n" + "\n".join(matches)
        return [types.TextContent(type="text", text=result)]

    @staticmethod
    def _human_readable_size(size: int) -> str:
        """Convert bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="filesystem-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def main():
    """Main entry point."""
    server = FileSystemMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
