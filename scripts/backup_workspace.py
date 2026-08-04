#!/usr/bin/env python3
"""Create version backup before updating workspace files."""

import sys
from pathlib import Path
from datetime import datetime


def backup_workspace_file(file_type: str, workspace_dir: Path) -> None:
    """Create version backup of a workspace file.
    
    Args:
        file_type: One of 'instruction', 'workspace', 'memory'
        workspace_dir: Path to workspace directory
    """
    # Map file_type to paths
    file_map = {
        "instruction": "instruction.md",
        "workspace": "WORKSPACE.md",
        "memory": "memory.md",
    }
    
    filename = file_map.get(file_type)
    if not filename:
        print(f"Unknown file type: {file_type}")
        return
    
    # Get current file
    current_path = workspace_dir / filename
    if not current_path.exists():
        return
    
    # Count existing versions
    versions_dir = workspace_dir / "versions" / file_type
    versions_dir.mkdir(parents=True, exist_ok=True)
    
    existing = list(versions_dir.glob("v*.md"))
    next_version = len(existing) + 1
    
    # Create backup
    backup_path = versions_dir / f"v{next_version}.md"
    import shutil
    shutil.copy2(current_path, backup_path)
    
    print(f"Backed up {filename} as v{next_version}.md")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: backup_workspace.py <file_type> <workspace_dir>")
        print("  file_type: instruction, workspace, or memory")
        sys.exit(1)
    
    file_type = sys.argv[1]
    workspace_dir = Path(sys.argv[2])
    
    backup_workspace_file(file_type, workspace_dir)
