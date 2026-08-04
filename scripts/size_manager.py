#!/usr/bin/env python3
"""Workspace Size Manager - Handles automatic size limits and summarization."""

import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional


class WorkspaceSizeManager:
    """Manages workspace file sizes and automatic summarization."""
    
    # Default size limits
    DEFAULT_LIMITS: Dict[str, int] = {
        "WORKSPACE.md": 16000,
        "memory.md": 32000,
        "journal.md": 100000,
        "instruction.md": 8000,
        "policy.md": 4000,
    }
    
    # Summarization thresholds (percentage of limit)
    WARN_PERCENTAGE = 0.8
    SUMMARIZE_PERCENTAGE = 0.9
    
    def __init__(self, workspace_dir: Path, limits: Optional[Dict[str, int]] = None):
        """Initialize size manager.
        
        Args:
            workspace_dir: Path to workspace directory
            limits: Custom size limits (optional)
        """
        self.workspace_dir = workspace_dir
        self.limits = limits or self.DEFAULT_LIMITS
    
    def check_sizes(self) -> Dict[str, Dict[str, Any]]:
        """Check all workspace file sizes.
        
        Returns:
            Dict of file status with size info
        """
        status = {}
        
        for file, limit in self.limits.items():
            file_path = self.workspace_dir / file
            if not file_path.exists():
                status[file] = {
                    "size": 0,
                    "limit": limit,
                    "status": "missing",
                    "action": "none"
                }
                continue
            
            size = file_path.stat().st_size
            percentage = size / limit if limit > 0 else 0
            
            if percentage >= self.SUMMARIZE_PERCENTAGE:
                action = "summarize"
            elif percentage >= self.WARN_PERCENTAGE:
                action = "warn"
            else:
                action = "none"
            
            status[file] = {
                "size": size,
                "limit": limit,
                "percentage": round(percentage * 100, 1),
                "status": "warning" if action == "warn" else ("critical" if action == "summarize" else "ok"),
                "action": action
            }
        
        return status
    
    def should_summarize(self, file: str) -> bool:
        """Check if a file needs summarization.
        
        Args:
            file: Filename to check
            
        Returns:
            True if summarization needed
        """
        file_path = self.workspace_dir / file
        if not file_path.exists():
            return False
        
        limit = self.limits.get(file, 0)
        size = file_path.stat().st_size
        
        return (size / limit) >= self.SUMMARIZE_PERCENTAGE if limit > 0 else False
    
    def get_size_summary(self) -> str:
        """Get human-readable size summary.
        
        Returns:
            Formatted size report
        """
        status = self.check_sizes()
        lines = ["# Workspace Size Report\n"]
        
        for file, info in status.items():
            size_kb = info["size"] / 1024
            limit_kb = info["limit"] / 1024
            lines.append(f"## {file}")
            lines.append(f"- Size: {size_kb:.1f} KB / {limit_kb:.1f} KB ({info['percentage']}%)")
            lines.append(f"- Status: {info['status'].upper()}")
            lines.append(f"- Action: {info['action']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def enforce_limits(self, dry_run: bool = False) -> Dict[str, bool]:
        """Enforce size limits by summarizing/archiving content.
        
        Args:
            dry_run: If True, only show what would be done
            
        Returns:
            Dict of file -> whether action was taken
        """
        results = {}
        status = self.check_sizes()
        
        for file, info in status.items():
            if info["action"] == "summarize" and file in ["WORKSPACE.md", "memory.md", "journal.md"]:
                if dry_run:
                    print(f"[DRY RUN] Would summarize {file}")
                    results[file] = False
                else:
                    self._summarize_file(file)
                    results[file] = True
        
        return results
    
    def _summarize_file(self, file: str) -> None:
        """Summarize a file to reduce size.
        
        Args:
            file: Filename to summarize
        """
        file_path = self.workspace_dir / file
        if not file_path.exists():
            return
        
        content = file_path.read_text()
        
        if file == "journal.md":
            # Archive old entries, keep recent ones
            lines = content.split("\n")
            recent_entries = []
            archived = []
            
            current_entry = []
            for line in lines:
                if line.startswith("## ") and current_entry:
                    archived.append("\n".join(current_entry))
                    current_entry = [line]
                else:
                    current_entry.append(line)
            
            if current_entry:
                archived.append("\n".join(current_entry))
            
            # Keep last 3 entries, archive the rest
            recent_entries = archived[-3:] if len(archived) > 3 else archived
            archived_entries = archived[:-3] if len(archived) > 3 else []
            
            new_content = "\n\n".join(recent_entries)
            if archived_entries:
                new_content += "\n\n---\n\n## Archived Entries\n\n"
                new_content += "\n".join(archived_entries)
            
            file_path.write_text(new_content)
        
        elif file == "WORKSPACE.md":
            # Keep first 80% of content, add truncation notice
            lines = content.split("\n")
            keep_count = int(len(lines) * 0.8)
            new_content = "\n".join(lines[:keep_count])
            new_content += "\n\n[... content truncated, " + str(len(lines) - keep_count) + " lines archived ...]"
            file_path.write_text(new_content)
        
        elif file == "memory.md":
            # Keep most recent entries, archive old ones
            lines = content.split("\n")
            entries = [l for l in lines if l.startswith("- ")]
            keep_entries = entries[-10:] if len(entries) > 10 else entries
            
            new_content = "# Memory\n\n"
            new_content += "\n".join(keep_entries)
            
            if len(entries) > 10:
                new_content += "\n\n## Archived (earlier entries)\n\n"
                new_content += "\n".join(entries[:-10])
            
            file_path.write_text(new_content)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Workspace Size Manager")
    parser.add_argument("--workspace-dir", required=True, help="Path to workspace directory")
    parser.add_argument("--action", choices=["check", "summary", "enforce"], required=True)
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    workspace_dir = Path(args.workspace_dir)
    size_manager = WorkspaceSizeManager(workspace_dir)
    
    if args.action == "check":
        status = size_manager.check_sizes()
        for file, info in status.items():
            print(f"{file}: {info['size']} bytes (limit: {info['limit']}, {info['percentage']}%) - {info['status']}")
    
    elif args.action == "summary":
        print(size_manager.get_size_summary())
    
    elif args.action == "enforce":
        results = size_manager.enforce_limits(dry_run=args.dry_run)
        for file, changed in results.items():
            if changed:
                print(f"✓ Summarized {file}")
            elif args.dry_run:
                print(f"  Would summarize {file}")
