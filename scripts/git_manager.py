#!/usr/bin/env python3
"""Git Integration for Workspace Version Control."""

import os
import subprocess
from pathlib import Path
from typing import Optional


class WorkspaceGitManager:
    """Git integration for workspace version control."""
    
    def __init__(self, workspace_dir: Path):
        """Initialize git manager.
        
        Args:
            workspace_dir: Path to workspace directory
        """
        self.workspace_dir = workspace_dir
        self.git_dir = workspace_dir / ".git"
    
    def init(self) -> bool:
        """Initialize git repository in workspace.
        
        Returns:
            True if initialized successfully
        """
        if self.git_dir.exists():
            return True
        
        try:
            subprocess.run(
                ["git", "init", str(self.workspace_dir)],
                capture_output=True,
                check=True
            )
            
            # Create .gitignore
            gitignore = self.workspace_dir / ".gitignore"
            gitignore.write_text("# Workspace lock files\n.workspace.lock\n\n# Python cache\n__pycache__/\n*.pyc\n")
            
            # Configure git
            subprocess.run(
                ["git", "config", "user.name", "Hermes Agent"],
                cwd=self.workspace_dir,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "config", "user.email", "hermes@local"],
                cwd=self.workspace_dir,
                capture_output=True,
                check=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git init failed: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if git is initialized.
        
        Returns:
            True if git repository exists
        """
        return self.git_dir.exists()
    
    def add_and_commit(self, message: str, files: Optional[list] = None) -> bool:
        """Add and commit workspace changes.
        
        Args:
            message: Commit message
            files: Specific files to commit (None for all)
            
        Returns:
            True if commit successful
        """
        if not self.is_initialized():
            if not self.init():
                return False
        
        try:
            # Add files
            if files:
                for f in files:
                    subprocess.run(
                        ["git", "add", str(self.workspace_dir / f)],
                        capture_output=True,
                        check=True
                    )
            else:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=self.workspace_dir,
                    capture_output=True,
                    check=True
                )
            
            # Check if there are changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                return True  # Nothing to commit
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.workspace_dir,
                capture_output=True,
                check=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e}")
            return False
    
    def get_history(self, file: Optional[str] = None, limit: int = 10) -> list:
        """Get git history for workspace.
        
        Args:
            file: Specific file to get history for
            limit: Maximum number of commits to return
            
        Returns:
            List of commit info dicts
        """
        if not self.is_initialized():
            return []
        
        try:
            cmd = ["git", "log", f"-n{limit}", "--pretty=format:%H|%an|%ad|%s"]
            if file:
                cmd.append(str(self.workspace_dir / file))
            
            result = subprocess.run(
                cmd,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True
            )
            
            history = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|", 3)
                    if len(parts) == 4:
                        history.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
            
            return history
        except subprocess.CalledProcessError as e:
            print(f"Git history failed: {e}")
            return []
    
    def get_diff(self, file: str, commit_hash: Optional[str] = None) -> str:
        """Get diff for a file.
        
        Args:
            file: Filename to diff
            commit_hash: Specific commit hash (None for working dir)
            
        Returns:
            Diff text
        """
        if not self.is_initialized():
            return ""
        
        try:
            cmd = ["git", "diff"]
            if commit_hash:
                cmd.extend(["HEAD", commit_hash, "--", str(self.workspace_dir / file)])
            else:
                cmd.append(str(self.workspace_dir / file))
            
            result = subprocess.run(
                cmd,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True
            )
            
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Git diff failed: {e}")
            return ""
    
    def rollback(self, commit_hash: str) -> bool:
        """Rollback to a specific commit.
        
        Args:
            commit_hash: Commit hash to rollback to
            
        Returns:
            True if rollback successful
        """
        if not self.is_initialized():
            return False
        
        try:
            subprocess.run(
                ["git", "reset", "--hard", commit_hash],
                cwd=self.workspace_dir,
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git rollback failed: {e}")
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Workspace Git Manager")
    parser.add_argument("--workspace-dir", required=True, help="Path to workspace directory")
    parser.add_argument("--action", choices=["init", "commit", "history", "diff", "rollback"], required=True)
    parser.add_argument("--message", help="Commit message (for commit action)")
    parser.add_argument("--file", help="Specific file for diff/history")
    parser.add_argument("--hash", help="Commit hash for rollback/diff")
    
    args = parser.parse_args()
    
    workspace_dir = Path(args.workspace_dir)
    git_manager = WorkspaceGitManager(workspace_dir)
    
    if args.action == "init":
        if git_manager.init():
            print("✓ Git repository initialized")
        else:
            print("✗ Failed to initialize git")
    
    elif args.action == "commit":
        if git_manager.add_and_commit(args.message or "Auto-commit"):
            print("✓ Changes committed")
        else:
            print("✗ Failed to commit")
    
    elif args.action == "history":
        history = git_manager.get_history(args.file)
        for commit in history:
            print(f"{commit['date'][:10]} {commit['hash'][:8]} {commit['message']}")
    
    elif args.action == "diff":
        diff = git_manager.get_diff(args.file, args.hash)
        if diff:
            print(diff)
        else:
            print("No changes or git not initialized")
    
    elif args.action == "rollback":
        if args.hash:
            if git_manager.rollback(args.hash):
                print(f"✓ Rolled back to {args.hash[:8]}")
            else:
                print("✗ Rollback failed")
        else:
            print("Error: --hash required for rollback")
