#!/usr/bin/env python3
"""GitHub Sync Manager for Persistent Task Memory Skill."""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any


class GitHubSyncManager:
    """Manages GitHub synchronization for the skill."""
    
    def __init__(self, skill_path: str, hermes_path: str = None):
        """Initialize GitHub sync manager.
        
        Args:
            skill_path: Path to the persistent-task-memory skill
            hermes_path: Path to Hermes Agent root (optional)
        """
        self.skill_path = Path(skill_path)
        self.hermes_path = Path(hermes_path) if hermes_path else self.skill_path.parent.parent.parent
        self.repo_url = None
        
    def check_git_installed(self) -> bool:
        """Check if git is installed."""
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def check_gh_cli_installed(self) -> bool:
        """Check if GitHub CLI is installed."""
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def is_git_repo(self) -> bool:
        """Check if Hermes is a git repository."""
        return (self.hermes_path / ".git").exists()
    
    def init_git_repo(self) -> bool:
        """Initialize git repository in Hermes."""
        if self.is_git_repo():
            print("✓ Git repository already exists")
            return True
        
        print("📁 Initializing git repository...")
        try:
            subprocess.run(
                ["git", "init"],
                cwd=self.hermes_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "add", "."],
                cwd=self.hermes_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit: Hermes Agent with Persistent Task Memory skill"],
                cwd=self.hermes_path,
                capture_output=True,
                check=True
            )
            print("✓ Git repository initialized")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to initialize git: {e}")
            return False
    
    def configure_git_user(self) -> bool:
        """Configure git user name and email."""
        name = subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        email = subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if not name or name == "Not set":
            print("⚠ Git user name not configured")
            name = input("Enter your name: ").strip()
            subprocess.run(
                ["git", "config", "--global", "user.name", name],
                check=True
            )
        
        if not email or email == "Not set":
            print("⚠ Git user email not configured")
            email = input("Enter your email: ").strip()
            subprocess.run(
                ["git", "config", "--global", "user.email", email],
                check=True
            )
        
        print(f"✓ Git user configured: {name} <{email}>")
        return True
    
    def create_github_repo(self, repo_name: str = "hermes-persistent-memory", public: bool = True) -> Optional[str]:
        """Create GitHub repository using gh CLI."""
        if not self.check_gh_cli_installed():
            print("❌ GitHub CLI (gh) not installed")
            print("  Install with: sudo apt install gh")
            return None
        
        print("🔄 Creating GitHub repository...")
        cmd = ["gh", "repo", "create", repo_name]
        if public:
            cmd.append("--public")
        cmd.append("--push")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✓ Repository created successfully")
            
            # Extract URL from output
            for line in result.stdout.split('\n'):
                if 'https://' in line:
                    self.repo_url = line.strip()
                    return self.repo_url
            
            return f"https://github.com/{self._get_gh_username()}/{repo_name}.git"
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create repository: {e}")
            return None
    
    def _get_gh_username(self) -> str:
        """Get GitHub username from gh CLI."""
        try:
            result = subprocess.run(
                ["gh", "api", "user", "--jq", ".login"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return "your-username"
    
    def add_remote(self, url: str, remote_name: str = "origin") -> bool:
        """Add git remote."""
        try:
            # Check if remote exists
            result = subprocess.run(
                ["git", "remote", "get-url", remote_name],
                cwd=self.hermes_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"⚠ Remote '{remote_name}' already exists")
                response = input(f"Replace existing remote? (y/N): ").strip().lower()
                if response == 'y':
                    subprocess.run(
                        ["git", "remote", "set-url", remote_name, url],
                        cwd=self.hermes_path,
                        check=True
                    )
                else:
                    subprocess.run(
                        ["git", "remote", "add", "hermes", url],
                        cwd=self.hermes_path,
                        check=True
                    )
                    remote_name = "hermes"
            else:
                subprocess.run(
                    ["git", "remote", "add", remote_name, url],
                    cwd=self.hermes_path,
                    check=True
                )
            
            print(f"✓ Remote '{remote_name}' added: {url}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to add remote: {e}")
            return False
    
    def push_to_github(self, remote: str = "origin", branch: str = "main") -> bool:
        """Push to GitHub."""
        print(f"📤 Pushing to {remote}/{branch}...")
        
        try:
            # Stage all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.hermes_path,
                capture_output=True,
                check=True
            )
            
            # Commit if there are changes
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=self.hermes_path,
                capture_output=True
            )
            
            if result.returncode != 0:  # Changes detected
                subprocess.run(
                    ["git", "commit", "-m", "feat: Add Persistent Task Memory skill v1.1.0 with GitHub sync"],
                    cwd=self.hermes_path,
                    capture_output=True,
                    check=True
                )
            
            # Push
            subprocess.run(
                ["git", "push", "-u", remote, branch],
                cwd=self.hermes_path,
                capture_output=True,
                check=True
            )
            
            print(f"✓ Pushed to {remote}/{branch}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to push: {e}")
            return False
    
    def setup_automated_sync(self) -> bool:
        """Set up automated GitHub sync using cron."""
        print("🔄 Setting up automated GitHub sync...")
        
        # Create sync script
        sync_script = self.hermes_path / ".github" / "sync-to-github.sh"
        sync_script.parent.mkdir(parents=True, exist_ok=True)
        
        script_content = """#!/bin/bash
# Automated GitHub Sync Script
cd /mnt/sdcard/shaun/hermes-agent
git add .
git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || true
git push origin main 2>/dev/null || git push origin master 2>/dev/null
"""
        
        sync_script.write_text(script_content)
        sync_script.chmod(0o755)
        
        print(f"✓ Sync script created: {sync_script}")
        print("")
        print("To schedule automatic sync, add to crontab:")
        print("  crontab -e")
        print("  # Add this line to run every 6 hours:")
        print(f"  0 */6 * * * {sync_script}")
        print("")
        
        return True
    
    def create_github_workflow(self) -> bool:
        """Create GitHub Actions workflow for CI/CD."""
        print("🔄 Creating GitHub Actions workflow...")
        
        workflow_dir = self.hermes_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_content = """name: Python CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
    
    - name: Check skill syntax
      run: |
        python -m py_compile app/skills/persistent-task-memory/skill.py
        for script in app/skills/persistent-task-memory/scripts/*.py; do
          python -m py_compile "$script"
        done
"""
        
        workflow_file = workflow_dir / "ci.yml"
        workflow_file.write_text(workflow_content)
        
        print(f"✓ Workflow created: {workflow_file}")
        print("  This will run tests on every push/PR")
        
        return True
    
    def sync_status(self) -> Dict[str, Any]:
        """Get sync status."""
        status = {
            "git_installed": self.check_git_installed(),
            "gh_cli_installed": self.check_gh_cli_installed(),
            "is_repo": self.is_git_repo(),
            "remote_url": None,
            "last_commit": None,
            "branch": None
        }
        
        if self.is_git_repo():
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=self.hermes_path,
                    capture_output=True,
                    text=True
                )
                status["remote_url"] = result.stdout.strip() if result.returncode == 0 else None
                
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%ci"],
                    cwd=self.hermes_path,
                    capture_output=True,
                    text=True
                )
                status["last_commit"] = result.stdout.strip() if result.returncode == 0 else None
                
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.hermes_path,
                    capture_output=True,
                    text=True
                )
                status["branch"] = result.stdout.strip() if result.returncode == 0 else None
            except:
                pass
        
        return status


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Sync Manager for Persistent Task Memory")
    parser.add_argument("--skill-path", default="/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory")
    parser.add_argument("--hermes-path", default="/mnt/sdcard/shaun/hermes-agent")
    parser.add_argument("--action", choices=["init", "sync", "status", "workflow", "auto-sync"], required=True)
    parser.add_argument("--repo-name", default="hermes-persistent-memory")
    
    args = parser.parse_args()
    
    manager = GitHubSyncManager(args.skill_path, args.hermes_path)
    
    if args.action == "init":
        print("🔧 Initializing GitHub sync...")
        manager.check_git_installed()
        manager.init_git_repo()
        manager.configure_git_user()
        print("\n✅ Initialization complete!")
        print("\nNext steps:")
        print("  1. Create GitHub repository:")
        print(f"     gh repo create {args.repo_name} --public --push")
        print("  2. Add remote and push:")
        print(f"     cd {args.hermes_path}")
        print("     git remote add origin https://github.com/YOUR-USERNAME/{}.git".format(args.repo_name))
        print("     git push -u origin main")
    
    elif args.action == "sync":
        url = input("Enter GitHub repository URL: ").strip()
        manager.add_remote(url)
        manager.push_to_github()
    
    elif args.action == "status":
        status = manager.sync_status()
        print("\n📊 Sync Status:")
        print(f"  Git installed: {'✓' if status['git_installed'] else '❌'}")
        print(f"  GH CLI: {'✓' if status['gh_cli_installed'] else '❌'}")
        print(f"  Is repository: {'✓' if status['is_repo'] else '❌'}")
        if status['remote_url']:
            print(f"  Remote: {status['remote_url']}")
        if status['last_commit']:
            print(f"  Last commit: {status['last_commit']}")
        if status['branch']:
            print(f"  Branch: {status['branch']}")
    
    elif args.action == "workflow":
        manager.create_github_workflow()
        print("\n✅ GitHub Actions workflow created!")
    
    elif args.action == "auto-sync":
        manager.setup_automated_sync()
        print("\n✅ Automated sync setup complete!")


if __name__ == "__main__":
    main()
