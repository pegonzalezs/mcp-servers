# tool_definitions.py
import mcp.types as types
from typing import List

def get_all_tools() -> List[types.Tool]:
    # Tools of Filesystem
    filesystem_tools = [
        types.Tool(name="read_file", description="Read the contents of a file", inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
        types.Tool(name="write_file", description="Write content to a file", inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path", "content"]}),
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
    
    # Tools of Odoo
    odoo_tools = [
        types.Tool(
            name="configure_odoo",
            description="Configures the connection to Odoo using a connection string: URL|DB|USER|PASS.",
            inputSchema={"type": "object", "properties": {"connection_string": {"type": "string"}}, "required": ["connection_string"]}
        ),
        types.Tool(
            name="get_contact_info",
            description="Gets specific Odoo contact info (e.g., address, phone, job) using a VAT/Tax ID.",
            inputSchema={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}
        ),
    ]

    return filesystem_tools + odoo_tools