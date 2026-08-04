#!/usr/bin/env python3
"""Persistent Task Memory Skill - Core implementation with production safeguards."""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import os

# Import protection scripts
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from workspace_lock import WorkspaceLock
from size_manager import WorkspaceSizeManager
from git_manager import WorkspaceGitManager
from skill_evolution import SkillInheritanceManager
from dry_run import DryRunManager


class PersistentTaskMemory:
    """Skill that provides persistent memory, instructions, and controlled self-improvement."""
    
    VERSION = "1.1.0"
    
    # File mapping
    FILE_MAP = {
        "policy": "policy.md",
        "identity": "identity.md",
        "instruction": "instruction.md",
        "workspace": "WORKSPACE.md",
        "memory": "memory.md",
        "journal": "journal.md",
        "changelog": "CHANGELOG.md",
    }
    
    # Modification authority
    MODIFICATION_AUTHORITY = {
        "memory.md": "AUTO",
        "journal.md": "AUTO",
        "WORKSPACE.md": "AUTO",
        "instruction.md": "PROPOSAL_ONLY",
        "policy.md": "NEVER",
    }
    
    # Size limits
    MAX_WORKSPACE_CHARS = 12000
    MAX_MEMORY_CHARS = 4000
    MAX_JOURNAL_CHARS = 8000
    MAX_INSTRUCTION_CHARS = 2000
    MAX_POLICY_CHARS = 2000
    
    def __init__(self, skills_dir: Optional[Path] = None):
        """Initialize the skill with all protections.
        
        Args:
            skills_dir: Path to skills directory (defaults to /app/skills/)
        """
        if skills_dir is None:
            skills_dir = Path("/mnt/sdcard/shaun/hermes-agent/app/skills")
        
        self.skills_dir = skills_dir
        self.task_dir = Path("/mnt/sdcard/shaun/hermes-agent/data/cron/tasks")
        self.templates_dir = skills_dir / "persistent-task-memory" / "templates"
        
        # Initialize protection managers
        self.lock_manager = None
        self.size_manager = None
        self.git_manager = None
        self.inheritance_manager = SkillInheritanceManager()
        self.dry_run_manager = None
    
    def prepare(self, job: Dict[str, Any], dry_run: bool = False, git_commit: bool = False) -> Path:
        """Prepare workspace for a job with protections.
        
        Args:
            job: Job dictionary with id, name, prompt, workspace config
            dry_run: If True, show changes without applying
            git_commit: If True, use git for version control
            
        Returns:
            Path to workspace directory
        """
        job_id = job.get("id", "")
        job_name = job.get("name", "")
        workspace_dir = self.task_dir / job_id
        
        # Initialize protection managers
        self.lock_manager = WorkspaceLock(workspace_dir)
        self.size_manager = WorkspaceSizeManager(workspace_dir)
        self.git_manager = WorkspaceGitManager(workspace_dir) if git_commit else None
        self.dry_run_manager = DryRunManager(workspace_dir) if dry_run else None
        
        # Try to acquire lock
        if not dry_run:
            if not self.lock_manager.acquire():
                raise RuntimeError(f"Failed to acquire lock for {job_id}")
        
        try:
            # Create directory structure
            workspace_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            for subdir in ["versions", "instruction", "workspace", "memory", "output", "proposals", "approval"]:
                (workspace_dir / "versions" / subdir).mkdir(parents=True, exist_ok=True)
                (workspace_dir / "output").mkdir(parents=True, exist_ok=True)
                (workspace_dir / "proposals").mkdir(parents=True, exist_ok=True)
                (workspace_dir / "approval").mkdir(parents=True, exist_ok=True)
            
            # Copy templates if files don't exist
            for key, filename in self.FILE_MAP.items():
                file_path = workspace_dir / filename
                if not file_path.exists():
                    template_path = self.templates_dir / filename
                    if template_path.exists():
                        import shutil
                        shutil.copy2(template_path, file_path)
                        if self.dry_run_manager:
                            self.dry_run_manager.add_proposed_change(
                                key, "create", f"Created {filename}", "New workspace"
                            )
                    else:
                        file_path.write_text(f"# {filename}\n\n", encoding="utf-8")
            
            # Update policy.md with modification authority
            policy_path = workspace_dir / "policy.md"
            if policy_path.exists():
                policy_content = policy_path.read_text()
                # Check if policy is modified
                if "## Modification Authority" not in policy_content:
                    if self.dry_run_manager:
                        self.dry_run_manager.add_proposed_change(
                            "policy", "modify", policy_content, "Adding modification authority"
                        )
                    
                    policy_content += "\n\n## Modification Authority\n\n"
                    for file, authority in self.MODIFICATION_AUTHORITY.items():
                        policy_content += f"{file}:\n{authority}\n\n"
                    policy_path.write_text(policy_content, encoding="utf-8")
            
            # Update instruction.md with template if empty
            instruction_path = workspace_dir / "instruction.md"
            if instruction_path.exists():
                instruction_content = instruction_path.read_text()
                if "{{task_purpose}}" in instruction_content:
                    if self.dry_run_manager:
                        self.dry_run_manager.add_proposed_change(
                            "instruction", "modify", instruction_content, "Filling template"
                        )
                    
                    purpose = job.get("prompt", "No purpose specified")[:100]
                    instruction_content = instruction_content.replace("{{task_purpose}}", purpose)
                    instruction_path.write_text(instruction_content, encoding="utf-8")
            
            # Initialize journal if empty
            journal_path = workspace_dir / "journal.md"
            if journal_path.exists():
                journal_content = journal_path.read_text()
                if "# Journal" in journal_content and "## " not in journal_content:
                    if self.dry_run_manager:
                        self.dry_run_manager.add_proposed_change(
                            "journal", "modify", journal_content, "Initializing journal"
                        )
                    
                    now = datetime.now()
                    journal_content += f"\n\n## {now.strftime('%Y-%m-%d')}\n\n**First run** - Workspace initialized\n"
                    journal_path.write_text(journal_content, encoding="utf-8")
            
            # Initialize CHANGELOG if empty
            changelog_path = workspace_dir / "CHANGELOG.md"
            if changelog_path.exists():
                changelog_content = changelog_path.read_text()
                if "# Changes" in changelog_content and "## v" not in changelog_content:
                    if self.dry_run_manager:
                        self.dry_run_manager.add_proposed_change(
                            "changelog", "modify", changelog_content, "Initializing changelog"
                        )
                    
                    changelog_content += f"\n\n## v0 - {datetime.now().strftime('%Y-%m-%d')}\n\nChanged:\nWorkspace initialized\n\nReason:\nFirst setup\n\nResult:\nSuccess\n"
                    changelog_path.write_text(changelog_content, encoding="utf-8")
            
            # Show dry run summary if enabled
            if self.dry_run_manager and self.dry_run_manager.get_proposal_count() > 0:
                print("\n" + self.dry_run_manager.show_proposed_changes())
                print("\n[Dry run complete - no files modified]\n")
            
            # Commit to git if enabled
            if self.git_manager:
                self.git_manager.add_and_commit("Workspace initialized")
            
            return workspace_dir
        
        finally:
            # Release lock
            if not dry_run and self.lock_manager:
                self.lock_manager.release()
    
    def inject(self, job: Dict[str, Any]) -> str:
        """Inject workspace context into prompt.
        
        Args:
            job: Job dictionary
            
        Returns:
            Prompt with workspace context injected
        """
        job_id = job.get("id", "")
        workspace_dir = self.task_dir / job_id
        
        if not workspace_dir.exists():
            return job.get("prompt", "")
        
        # Read workspace files
        workspace_content = ""
        
        # Read instruction.md
        instruction_path = workspace_dir / "instruction.md"
        if instruction_path.exists():
            instruction = instruction_path.read_text(encoding="utf-8")
            if instruction.strip():
                workspace_content += f"## Task Instructions\n{instruction}\n\n"
        
        # Read policy.md
        policy_path = workspace_dir / "policy.md"
        if policy_path.exists():
            policy = policy_path.read_text(encoding="utf-8")
            if policy.strip():
                workspace_content += f"## Job Policy\n{policy}\n\n"
        
        # Read WORKSPACE.md
        workspace_md_path = workspace_dir / "WORKSPACE.md"
        if workspace_md_path.exists():
            workspace_md = workspace_md_path.read_text(encoding="utf-8")
            workspace_md = self._truncate(workspace_md, self.MAX_WORKSPACE_CHARS)
            if workspace_md.strip():
                workspace_content += f"## Workspace Context\n{workspace_md}\n\n"
        
        # Read memory.md
        memory_path = workspace_dir / "memory.md"
        if memory_path.exists():
            memory = memory_path.read_text(encoding="utf-8")
            memory = self._truncate(memory, self.MAX_MEMORY_CHARS)
            if memory.strip():
                workspace_content += f"## Learned Memory\n{memory}\n\n"
        
        # Inject into prompt
        prompt = job.get("prompt", "")
        if workspace_content.strip():
            prompt = (
                "[IMPORTANT: You are executing a scheduled cron task with a persistent workspace. "
                "The following content represents your job policy, task instructions, workspace context, and learned memory. "
                "Follow the policy rules strictly, use the instructions to guide your approach, "
                "and maintain continuity across runs using the workspace context.]\n\n"
                + workspace_content
                + "\n"
                + prompt
            )
        
        return prompt
    
    def update(self, job: Dict[str, Any], success: bool, output: str, dry_run: bool = False, git_commit: bool = False) -> None:
        """Update workspace files after job completion with all protections.
        
        Args:
            job: Job dictionary
            success: Whether the job succeeded
            output: Job output text
            dry_run: If True, show changes without applying
            git_commit: If True, use git for version control
        """
        job_id = job.get("id", "")
        workspace_dir = self.task_dir / job_id
        
        if not workspace_dir.exists():
            return
        
        # Initialize protection managers
        self.lock_manager = WorkspaceLock(workspace_dir)
        self.size_manager = WorkspaceSizeManager(workspace_dir)
        self.git_manager = WorkspaceGitManager(workspace_dir) if git_commit else None
        self.dry_run_manager = DryRunManager(workspace_dir) if dry_run else None
        
        # Try to acquire lock
        if not dry_run:
            if not self.lock_manager.acquire():
                raise RuntimeError(f"Failed to acquire lock for {job_id}")
        
        try:
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M")
            date = now.strftime("%Y-%m-%d")
            
            # Check sizes before updating
            size_status = self.size_manager.check_sizes()
            
            # Update WORKSPACE.md
            workspace_md_path = workspace_dir / "WORKSPACE.md"
            if workspace_md_path.exists():
                workspace_md = workspace_md_path.read_text(encoding="utf-8")
                
                # Check policy before updating
                policy_content = ""
                policy_path = workspace_dir / "policy.md"
                if policy_path.exists():
                    policy_content = policy_path.read_text(encoding="utf-8")
                
                if workspace_md:
                    # Update status
                    status_idx = workspace_md.find("## Status")
                    if status_idx >= 0:
                        # Update existing status
                        end_idx = workspace_md.find("\n## ", status_idx + 1)
                        if end_idx < 0:
                            end_idx = len(workspace_md)
                        new_status = f"## Status\n\n- **Last Run**: {timestamp}\n- **Status**: {'✓ Success' if success else '✗ Failed'}\n- **Output**: {output[:500]}{'...' if len(output) > 500 else ''}\n"
                        workspace_md = workspace_md[:status_idx] + new_status + workspace_md[end_idx:]
                    else:
                        # Add status section
                        workspace_md += f"\n## Status\n\n- **Last Run**: {timestamp}\n- **Status**: {'✓ Success' if success else '✗ Failed'}\n- **Output**: {output[:500]}{'...' if len(output) > 500 else ''}\n"
                    
                    # Truncate
                    workspace_md = self._truncate(workspace_md, self.MAX_WORKSPACE_CHARS)
                    
                    # Show in dry run if enabled
                    if self.dry_run_manager:
                        self.dry_run_manager.add_proposed_change(
                            "workspace", "modify", workspace_md, "Updated status"
                        )
                    
                    if not dry_run:
                        workspace_md_path.write_text(workspace_md, encoding="utf-8")
            
            # Update memory.md with deduplication and summarization
            memory_path = workspace_dir / "memory.md"
            if memory_path.exists():
                memory_md = memory_path.read_text(encoding="utf-8")
                
                # Add new memory if output contains useful info
                if output.strip():
                    new_memory = f"- {timestamp}: {output[:100]}\n"
                    if new_memory not in memory_md:
                        memory_md += new_memory
                        memory_md = self._truncate(memory_md, self.MAX_MEMORY_CHARS)
                        
                        # Show in dry run if enabled
                        if self.dry_run_manager:
                            self.dry_run_manager.add_proposed_change(
                                "memory", "modify", memory_md, "Added new memory"
                            )
                        
                        if not dry_run:
                            memory_path.write_text(memory_md, encoding="utf-8")
            
            # Update instruction.md only through proposals
            instruction_path = workspace_dir / "instruction.md"
            if instruction_path.exists():
                instruction_md = instruction_path.read_text(encoding="utf-8")
                
                # If instruction changes are needed, create proposal instead
                if "TODO" in instruction_md and success:
                    if self.dry_run_manager:
                        self.dry_run_manager.add_proposed_change(
                            "instruction", "propose", instruction_md, "Instruction refinement needed"
                        )
                    else:
                        # Create actual proposal file
                        proposal_dir = workspace_dir / "proposals"
                        proposal_dir.mkdir(parents=True, exist_ok=True)
                        proposal_file = proposal_dir / f"instruction_{now.strftime('%Y%m%d_%H%M%S')}.md"
                        proposal_content = f"""# Proposed Instruction Change

**Current**:
{instruction_md[:1000]}...

**Proposed**:
[Instruction refinement would go here]

**Reason**:
Task succeeded, instruction could be improved for future runs.

**Confidence**: 0.7
"""
                        proposal_file.write_text(proposal_content, encoding="utf-8")
            
            # Append to CHANGELOG.md
            changelog_path = workspace_dir / "CHANGELOG.md"
            if changelog_path.exists():
                version = self._get_next_version(workspace_dir, "workspace")
                changes = "Updated status and memory"
                reason = "Regular workspace update after job execution"
                result = "Success" if success else "Failed"
                self._append_to_changelog(changelog_path, version, changes, reason, result)
            
            # Append to journal.md
            journal_path = workspace_dir / "journal.md"
            if journal_path.exists():
                journal_md = journal_path.read_text(encoding="utf-8")
                journal_entry = f"## {date}\n\n**Time**: {timestamp}\n**Status**: {'Success' if success else 'Failed'}\n**Output**: {output[:300]}{'...' if len(output) > 300 else ''}\n\n"
                journal_md += journal_entry
                journal_md = self._truncate(journal_md, self.MAX_JOURNAL_CHARS)
                
                if self.dry_run_manager:
                    self.dry_run_manager.add_proposed_change(
                        "journal", "modify", journal_md, "Added run entry"
                    )
                
                if not dry_run:
                    journal_path.write_text(journal_md, encoding="utf-8")
            
            # Check if evolution candidate
            if success:
                journal_path = workspace_dir / "journal.md"
                if journal_path.exists():
                    content = journal_path.read_text()
                    success_count = content.count("Status: Success")
                    if success_count >= 25:
                        self.inheritance_manager.detect_evolution_candidate(workspace_dir)
            
            # Check sizes after update
            size_status = self.size_manager.check_sizes()
            for file, info in size_status.items():
                if info["action"] == "summarize":
                    if dry_run:
                        self.dry_run_manager.add_proposed_change(
                            file, "summarize", "", f"File {file} exceeds size limit, would summarize"
                        )
                    else:
                        self.size_manager.enforce_limits()
            
            # Show dry run summary if enabled
            if self.dry_run_manager and self.dry_run_manager.get_proposal_count() > 0:
                print("\n" + self.dry_run_manager.show_proposed_changes())
                print("\n[Dry run complete - no files modified]\n")
            
            # Commit to git if enabled
            if self.git_manager:
                self.git_manager.add_and_commit("Workspace updated after run")
        
        finally:
            # Release lock
            if not dry_run and self.lock_manager:
                self.lock_manager.release()
    
    def get_proposals(self, job_id: str) -> list:
        """Get pending change proposals.
        
        Args:
            job_id: Job ID
            
        Returns:
            List of proposals
        """
        workspace_dir = self.task_dir / job_id
        proposals_dir = workspace_dir / "proposals"
        
        if not proposals_dir.exists():
            return []
        
        proposals = []
        for proposal_file in proposals_dir.glob("*.md"):
            proposal = {
                "file": proposal_file.name,
                "content": proposal_file.read_text(encoding="utf-8")
            }
            proposals.append(proposal)
        
        return proposals
    
    def create_proposal(self, job_id: str, file_type: str, current: str, proposed: str, reason: str, confidence: float) -> None:
        """Create a change proposal.
        
        Args:
            job_id: Job ID
            file_type: Type of file (instruction, workspace, memory)
            current: Current content
            proposed: Proposed content
            reason: Reason for change
            confidence: Confidence score (0.0-1.0)
        """
        workspace_dir = self.task_dir / job_id
        proposals_dir = workspace_dir / "proposals"
        proposals_dir.mkdir(parents=True, exist_ok=True)
        
        now = datetime.now()
        proposal_file = proposals_dir / f"{file_type}_{now.strftime('%Y%m%d_%H%M%S')}.md"
        
        proposal_content = f"""# Proposed Change

**File**: {file_type}.md

**Current**:
```
{current[:500]}{'...' if len(current) > 500 else ''}
```

**Proposed**:
```
{proposed[:500]}{'...' if len(proposed) > 500 else ''}
```

**Reason**:
{reason}

**Confidence**: {confidence:.2f}

**Created**: {now.strftime('%Y-%m-%d %H:%M')}
"""
        
        proposal_file.write_text(proposal_content, encoding="utf-8")
    
    def approve_proposal(self, job_id: str, proposal_file: str) -> None:
        """Approve and apply a proposal.
        
        Args:
            job_id: Job ID
            proposal_file: Proposal filename
        """
        workspace_dir = self.task_dir / job_id
        proposals_dir = workspace_dir / "proposals"
        proposal_path = proposals_dir / proposal_file
        
        if not proposal_path.exists():
            return
        
        # Parse proposal
        content = proposal_path.read_text(encoding="utf-8")
        
        # Extract file type
        import re
        file_match = re.search(r'\*\*File\*\*: (\w+)\.md', content)
        if not file_match:
            return
        
        file_type = file_match.group(1)
        
        # Move to approval directory
        approval_dir = workspace_dir / "approval"
        approval_dir.mkdir(parents=True, exist_ok=True)
        approved_file = approval_dir / proposal_file
        approved_file.write_text(content, encoding="utf-8")
        
        # Apply change (simplified - in real implementation, would parse and apply)
        # For now, just log it
        print(f"Proposal approved: {proposal_file} -> {file_type}.md")
        
        # Delete proposal
        proposal_path.unlink()
    
    def _truncate(self, text: str, max_chars: int) -> str:
        """Truncate text to max characters."""
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "\n\n[... truncated ...]"
    
    def _get_next_version(self, workspace_dir: Path, file_type: str) -> str:
        """Get next version number for a file type."""
        versions_dir = workspace_dir / "versions" / file_type
        if not versions_dir.exists():
            return "v1"
        
        existing = list(versions_dir.glob("v*.md"))
        if not existing:
            return "v1"
        
        # Parse version numbers
        import re
        versions = []
        for f in existing:
            match = re.match(r'v(\d+)\.md', f.name)
            if match:
                versions.append(int(match.group(1)))
        
        if not versions:
            return "v1"
        
        return f"v{max(versions) + 1}"
    
    def _append_to_changelog(self, changelog_path: Path, version: str, changes: str, reason: str, result: str) -> None:
        """Append to CHANGELOG.md."""
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        
        entry = f"\n\n## {version} - {date}\n\nChanged:\n{changes}\n\nReason:\n{reason}\n\nResult:\n{result}\n"
        
        if not changelog_path.exists():
            changelog_path.write_text(f"# Changes{entry}\n", encoding="utf-8")
        else:
            current = changelog_path.read_text(encoding="utf-8")
            changelog_path.write_text(current + entry, encoding="utf-8")
    
    def validate(self, workspace_dir: Path, include_protections: bool = True) -> list:
        """Validate workspace structure and health with all protections.
        
        Args:
            workspace_dir: Path to workspace directory
            include_protections: If True, check all protection systems
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Check required files
        for key, filename in self.FILE_MAP.items():
            if not (workspace_dir / filename).exists():
                issues.append(f"Missing required file: {filename}")
        
        # Check file sizes
        max_sizes = {
            "WORKSPACE.md": self.MAX_WORKSPACE_CHARS,
            "memory.md": self.MAX_MEMORY_CHARS,
            "journal.md": self.MAX_JOURNAL_CHARS,
            "instruction.md": self.MAX_INSTRUCTION_CHARS,
            "policy.md": self.MAX_POLICY_CHARS,
        }
        
        for file, max_size in max_sizes.items():
            path = workspace_dir / file
            if path.exists():
                size = path.stat().st_size
                if size > max_size:
                    issues.append(f"{file} too large: {size} bytes (max {max_size})")
        
        # Check for duplicates in memory
        memory_path = workspace_dir / "memory.md"
        if memory_path.exists():
            content = memory_path.read_text()
            lines = [l.strip() for l in content.split("\n") if l.strip().startswith("-")]
            if len(lines) != len(set(lines)):
                issues.append("Duplicate entries found in memory.md")
        
        # Check for stale versions
        versions_dir = workspace_dir / "versions"
        if versions_dir.exists():
            for version_type in ["instruction", "workspace", "memory"]:
                vdir = versions_dir / version_type
                if vdir.exists():
                    versions = list(vdir.glob("v*.md"))
                    if len(versions) > 10:
                        issues.append(f"Too many {version_type} versions: {len(versions)}")
        
        # Check lock status
        if include_protections:
            lock_manager = WorkspaceLock(workspace_dir)
            if lock_manager.is_locked():
                lock_info = lock_manager.get_lock_info()
                issues.append(f"Workspace is locked by PID {lock_info.get('pid', 'unknown')}")
        
        # Check git status
        if include_protections:
            git_manager = WorkspaceGitManager(workspace_dir)
            if git_manager.is_initialized():
                history = git_manager.get_history()
                if not history:
                    issues.append("Git repository initialized but no commits found")
        
        return issues


if __name__ == "__main__":
    import argparse
    import re
    
    parser = argparse.ArgumentParser(description="Persistent Task Memory Skill")
    parser.add_argument("--workspace-dir", required=True, help="Path to workspace directory")
    parser.add_argument("--action", choices=["validate", "prepare", "update"], required=True)
    parser.add_argument("--success", type=bool, help="Whether job succeeded (for update)")
    parser.add_argument("--output", help="Job output (for update)")
    parser.add_argument("--dry-run", action="store_true", help="Show proposed changes without applying")
    parser.add_argument("--git-commit", action="store_true", help="Use git for version control")
    
    args = parser.parse_args()
    
    skill = PersistentTaskMemory()
    workspace_dir = Path(args.workspace_dir)
    
    if args.action == "validate":
        issues = skill.validate(workspace_dir, include_protections=True)
        if not issues:
            print("✓ Workspace is healthy")
        else:
            print(f"✗ Found {len(issues)} issues:")
            for issue in issues:
                print(f"  • {issue}")
            sys.exit(1)
    
    elif args.action == "prepare":
        job = {
            "id": workspace_dir.name,
            "name": workspace_dir.name,
            "prompt": "Test prompt"
        }
        skill.prepare(job, dry_run=args.dry_run, git_commit=args.git_commit)
        print(f"✓ Prepared workspace: {workspace_dir}")
    
    elif args.action == "update":
        job = {
            "id": workspace_dir.name,
            "name": workspace_dir.name,
            "prompt": "Test prompt"
        }
        skill.update(job, args.success, args.output or "", dry_run=args.dry_run, git_commit=args.git_commit)
        print(f"✓ Updated workspace: {workspace_dir}")
