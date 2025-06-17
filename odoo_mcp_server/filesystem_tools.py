# filesystem_tools.py
import asyncio
import json
import os
import sys
import glob
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import mcp.types as types
import docx


class FileSystemTools:
    async def read_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """
        Reads the content of a file. Supports .txt, .json, .py, etc., and .docx.
        """
        file_path = Path(args["file_path"]).resolve()

        if not file_path.exists() or not file_path.is_file():
            return [types.TextContent(type="text", text=f"Error: File not found at {file_path}")]

        content = ""
        try:
            # Logic .docx
            if file_path.suffix == '.docx':
                doc = docx.Document(file_path)
                # Une el texto de todos los párrafos del documento
                content = "\n".join([para.text for para in doc.paragraphs])
            # Logic .txt, .json, .py, etc.
            else:
                content = file_path.read_text(encoding='utf-8')
            
            return [types.TextContent(type="text", text=content)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error reading file {file_path}: {e}")]


    async def write_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Write content to file."""
        file_path = Path(args["file_path"]).resolve()
        content = args["content"]
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_path.write_text(content, encoding='utf-8')
        return [types.TextContent(type="text", text=f"Successfully wrote {len(content)} characters to: {file_path}")]


    async def append_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Append content to file."""
        file_path = Path(args["file_path"]).resolve()
        content = args["content"]
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        return [types.TextContent(type="text", text=f"Successfully appended {len(content)} characters to: {file_path}")]

    async def list_directory(self, args: Dict[str, Any]) -> List[types.TextContent]:
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

    async def create_directory(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Create directory."""
        directory_path = Path(args["directory_path"]).resolve()
        
        directory_path.mkdir(parents=True, exist_ok=True)
        return [types.TextContent(type="text", text=f"Successfully created directory: {directory_path}")]

    async def delete_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
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

    async def move_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Move or rename file/directory."""
        source_path = Path(args["source_path"]).resolve()
        destination_path = Path(args["destination_path"]).resolve()
        
        if not source_path.exists():
            return [types.TextContent(type="text", text=f"Error: Source path does not exist: {source_path}")]
        
        # Create parent directories if they don't exist
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(source_path), str(destination_path))
        return [types.TextContent(type="text", text=f"Successfully moved {source_path} to {destination_path}")]

    async def copy_file(self, args: Dict[str, Any]) -> List[types.TextContent]:
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

    async def file_info(self, args: Dict[str, Any]) -> List[types.TextContent]:
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

    async def search_files(self, args: Dict[str, Any]) -> List[types.TextContent]:
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

    async def find_text(self, args: Dict[str, Any]) -> List[types.TextContent]:
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