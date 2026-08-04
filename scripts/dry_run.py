#!/usr/bin/env python3
"""Dry Run Mode - Shows proposed changes without applying them."""

import sys
from pathlib import Path
from typing import Dict, Any, List


class DryRunManager:
    """Manages dry-run mode for workspace changes."""
    
    def __init__(self, workspace_dir: Path):
        """Initialize dry run manager.
        
        Args:
            workspace_dir: Path to workspace directory
        """
        self.workspace_dir = workspace_dir
        self.proposed_changes: List[Dict[str, Any]] = []
    
    def add_proposed_change(self, file_type: str, action: str, content: str, reason: str) -> None:
        """Add a proposed change to the list.
        
        Args:
            file_type: Type of file (policy, instruction, workspace, memory, journal)
            action: Action being proposed (add, modify, delete)
            content: Proposed content
            reason: Reason for the change
        """
        self.proposed_changes.append({
            "file": f"{file_type}.md",
            "action": action,
            "content": content[:500] + ("..." if len(content) > 500 else ""),
            "reason": reason
        })
    
    def show_proposed_changes(self) -> str:
        """Show all proposed changes in a formatted report.
        
        Returns:
            Formatted change report
        """
        if not self.proposed_changes:
            return "No proposed changes."
        
        lines = ["# Proposed Changes (Dry Run)\n", "**No files will be modified.**\n"]
        
        for i, change in enumerate(self.proposed_changes, 1):
            lines.append(f"## {i}. {change['file']}")
            lines.append(f"**Action**: {change['action']}")
            lines.append(f"**Reason**: {change['reason']}")
            lines.append(f"**Content**:\n```\n{change['content']}\n```")
            lines.append("")
        
        return "\n".join(lines)
    
    def clear_proposals(self) -> None:
        """Clear all proposed changes."""
        self.proposed_changes = []
    
    def save_proposals(self) -> None:
        """Save proposed changes to file for review."""
        proposal_file = self.workspace_dir / "proposals" / "dry_run_review.md"
        proposal_file.write_text(self.show_proposed_changes())
    
    def get_proposal_count(self) -> int:
        """Get number of proposed changes.
        
        Returns:
            Count of proposed changes
        """
        return len(self.proposed_changes)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Dry Run Manager")
    parser.add_argument("--workspace-dir", required=True, help="Path to workspace directory")
    parser.add_argument("--show", action="store_true", help="Show proposed changes")
    parser.add_argument("--clear", action="store_true", help="Clear proposed changes")
    parser.add_argument("--save", action="store_true", help="Save proposals to file")
    
    args = parser.parse_args()
    
    workspace_dir = Path(args.workspace_dir)
    dry_run = DryRunManager(workspace_dir)
    
    # Load existing proposals if any
    proposal_file = workspace_dir / "proposals" / "dry_run_review.md"
    if proposal_file.exists():
        # In real implementation, would parse and load
        pass
    
    if args.show:
        report = dry_run.show_proposed_changes()
        print(report)
    
    elif args.clear:
        dry_run.clear_proposals()
        print("✓ Proposals cleared")
    
    elif args.save:
        dry_run.save_proposals()
        print(f"✓ Saved {dry_run.get_proposal_count()} proposals")
