#!/usr/bin/env python3
"""Skill Inheritance Manager - Support for base and child skills."""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class SkillInheritanceManager:
    """Manages skill inheritance hierarchies."""
    
    # Evolution directories
    EVOLUTION_DIR = Path("/mnt/sdcard/shaun/hermes-agent/data/skills/evolution")
    CANDIDATE_DIR = EVOLUTION_DIR / "candidate_skills"
    APPROVED_DIR = EVOLUTION_DIR / "approved_skills"
    RETIRED_DIR = EVOLUTION_DIR / "retired_skills"
    
    def __init__(self):
        """Initialize skill inheritance manager."""
        self.EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        self.CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
        self.APPROVED_DIR.mkdir(parents=True, exist_ok=True)
        self.RETIRED_DIR.mkdir(parents=True, exist_ok=True)
    
    def create_inheritance(self, parent_skill: str, child_skill: str, workspace_dir: Path) -> bool:
        """Create skill inheritance relationship.
        
        Args:
            parent_skill: Parent skill name
            child_skill: Child skill name
            workspace_dir: Workspace directory for child
            
        Returns:
            True if inheritance created successfully
        """
        try:
            # Create inheritance config
            config = {
                "parent_skill": parent_skill,
                "child_skill": child_skill,
                "inherited_files": ["policy.md", "WORKSPACE.md", "memory.md", "journal.md"],
                "created_at": __import__('datetime').datetime.now().isoformat()
            }
            
            config_path = workspace_dir / ".skill-inheritance.json"
            config_path.write_text(json.dumps(config, indent=2))
            
            # Create inherited files if they don't exist
            parent_dir = Path("/mnt/sdcard/shaun/hermes-agent/app/skills") / parent_skill
            for file in config["inherited_files"]:
                parent_file = parent_dir / file
                child_file = workspace_dir / file
                if parent_file.exists() and not child_file.exists():
                    child_file.write_text(parent_file.read_text())
            
            return True
        except Exception as e:
            print(f"Failed to create inheritance: {e}")
            return False
    
    def get_inheritance_chain(self, workspace_dir: Path) -> List[Dict[str, Any]]:
        """Get full inheritance chain for a workspace.
        
        Args:
            workspace_dir: Workspace directory
            
        Returns:
            List of inheritance info dicts
        """
        config_path = workspace_dir / ".skill-inheritance.json"
        if not config_path.exists():
            return []
        
        try:
            config = json.loads(config_path.read_text())
            chain = [config]
            
            # Walk up the chain
            current_parent = config.get("parent_skill")
            while current_parent:
                parent_dir = Path("/mnt/sdcard/shaun/hermes-agent/app/skills") / current_parent
                parent_config_path = parent_dir / ".skill-inheritance.json"
                
                if parent_config_path.exists():
                    parent_config = json.loads(parent_config_path.read_text())
                    chain.append(parent_config)
                    current_parent = parent_config.get("parent_skill")
                else:
                    break
            
            return chain
        except Exception as e:
            print(f"Failed to get inheritance chain: {e}")
            return []
    
    def add_to_evolution_candidates(self, workspace_dir: Path, metrics: Dict[str, Any]) -> bool:
        """Add a task to skill evolution candidates.
        
        Args:
            workspace_dir: Task workspace directory
            metrics: Success metrics and workflow data
            
        Returns:
            True if added successfully
        """
        try:
            # Create candidate skill directory
            skill_name = workspace_dir.name
            candidate_dir = self.CANDIDATE_DIR / skill_name
            
            candidate_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy relevant files
            import shutil
            for file in ["instruction.md", "policy.md", "memory.md", "WORKSPACE.md"]:
                src = workspace_dir / file
                dst = candidate_dir / file
                if src.exists():
                    shutil.copy2(src, dst)
            
            # Create SKILL.md
            skill_md = candidate_dir / "SKILL.md"
            skill_md.write_text(f"""# {skill_name}

## Overview
Candidate skill extracted from successful task pattern.

## Metrics
{json.dumps(metrics, indent=2)}

## Status
**Pending Approval**

## Created
{__import__('datetime').datetime.now().isoformat()}
""")
            
            return True
        except Exception as e:
            print(f"Failed to add to evolution candidates: {e}")
            return False
    
    def approve_skill(self, skill_name: str) -> bool:
        """Approve a candidate skill for production.
        
        Args:
            skill_name: Name of the skill to approve
            
        Returns:
            True if approved successfully
        """
        try:
            candidate_dir = self.CANDIDATE_DIR / skill_name
            approved_dir = self.APPROVED_DIR / skill_name
            
            if not candidate_dir.exists():
                return False
            
            import shutil
            shutil.copytree(candidate_dir, approved_dir)
            
            # Update status in SKILL.md
            skill_md = approved_dir / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text()
                content = content.replace("**Pending Approval**", "**Approved**")
                skill_md.write_text(content)
            
            return True
        except Exception as e:
            print(f"Failed to approve skill: {e}")
            return False
    
    def retire_skill(self, skill_name: str) -> bool:
        """Retire a skill (move to retired directory).
        
        Args:
            skill_name: Name of the skill to retire
            
        Returns:
            True if retired successfully
        """
        try:
            approved_dir = self.APPROVED_DIR / skill_name
            retired_dir = self.RETIRED_DIR / skill_name
            
            if not approved_dir.exists():
                return False
            
            import shutil
            shutil.copytree(approved_dir, retired_dir)
            
            # Update status in SKILL.md
            skill_md = retired_dir / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text()
                content = content.replace("**Approved**", "**Retired**")
                skill_md.write_text(content)
            
            # Remove from approved
            shutil.rmtree(approved_dir)
            
            return True
        except Exception as e:
            print(f"Failed to retire skill: {e}")
            return False
    
    def list_candidates(self) -> List[Dict[str, Any]]:
        """List all candidate skills.
        
        Returns:
            List of candidate skill info
        """
        candidates = []
        
        if self.CANDIDATE_DIR.exists():
            for candidate_dir in self.CANDIDATE_DIR.iterdir():
                if candidate_dir.is_dir():
                    skill_md = candidate_dir / "SKILL.md"
                    if skill_md.exists():
                        candidates.append({
                            "name": candidate_dir.name,
                            "path": str(candidate_dir),
                            "created": skill_md.read_text().split("Created\n")[1].strip() if "Created\n" in skill_md.read_text() else "unknown"
                        })
        
        return candidates
    
    def list_approved(self) -> List[Dict[str, Any]]:
        """List all approved skills.
        
        Returns:
            List of approved skill info
        """
        approved = []
        
        if self.APPROVED_DIR.exists():
            for approved_dir in self.APPROVED_DIR.iterdir():
                if approved_dir.is_dir():
                    skill_md = approved_dir / "SKILL.md"
                    if skill_md.exists():
                        approved.append({
                            "name": approved_dir.name,
                            "path": str(approved_dir)
                        })
        
        return approved
    
    def detect_evolution_candidate(self, workspace_dir: Path, success_count: int = 25) -> bool:
        """Detect if a task should become a skill.
        
        Args:
            workspace_dir: Task workspace directory
            success_count: Number of consecutive successes to trigger evolution
            
        Returns:
            True if evolution candidate detected
        """
        # Check journal for success count
        journal_path = workspace_dir / "journal.md"
        if not journal_path.exists():
            return False
        
        content = journal_path.read_text()
        success_lines = [l for l in content.split("\n") if "✓ Success" in l or "Status: Success" in l]
        
        if len(success_lines) >= success_count:
            # Get metrics
            metrics = {
                "success_count": len(success_lines),
                "workspace_size": workspace_dir.stat().st_size,
                "version_count": len(list((workspace_dir / "versions").glob("**/*.md"))) if (workspace_dir / "versions").exists() else 0
            }
            
            return self.add_to_evolution_candidates(workspace_dir, metrics)
        
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill Inheritance Manager")
    parser.add_argument("--action", choices=["inherit", "chain", "candidate", "approve", "retire", "detect"], required=True)
    parser.add_argument("--parent", help="Parent skill name")
    parser.add_argument("--child", help="Child skill name")
    parser.add_argument("--workspace-dir", help="Workspace directory")
    parser.add_argument("--skill-name", help="Skill name for approve/retire")
    parser.add_argument("--success-count", type=int, default=25, help="Success count threshold for evolution")
    
    args = parser.parse_args()
    
    manager = SkillInheritanceManager()
    
    if args.action == "inherit":
        if args.parent and args.child and args.workspace_dir:
            if manager.create_inheritance(args.parent, args.child, Path(args.workspace_dir)):
                print(f"✓ Inheritance created: {args.parent} -> {args.child}")
            else:
                print("✗ Failed to create inheritance")
        else:
            print("Error: --parent, --child, and --workspace-dir required")
    
    elif args.action == "chain":
        if args.workspace_dir:
            chain = manager.get_inheritance_chain(Path(args.workspace_dir))
            for i, entry in enumerate(chain):
                print(f"{i+1}. {entry['child_skill']} (from {entry['parent_skill']})")
    
    elif args.action == "candidate":
        if args.workspace_dir:
            if manager.add_to_evolution_candidates(Path(args.workspace_dir), {}):
                print(f"✓ Added to evolution candidates")
            else:
                print("✗ Failed to add")
    
    elif args.action == "approve":
        if args.skill_name:
            if manager.approve_skill(args.skill_name):
                print(f"✓ Skill approved: {args.skill_name}")
            else:
                print("✗ Failed to approve")
        else:
            print("Error: --skill-name required")
    
    elif args.action == "retire":
        if args.skill_name:
            if manager.retire_skill(args.skill_name):
                print(f"✓ Skill retired: {args.skill_name}")
            else:
                print("✗ Failed to retire")
        else:
            print("Error: --skill-name required")
    
    elif args.action == "detect":
        if args.workspace_dir:
            if manager.detect_evolution_candidate(Path(args.workspace_dir), args.success_count):
                print(f"✓ Evolution candidate detected and added")
            else:
                print("No evolution candidate detected")
    
    # List commands
    if args.action == "list-candidates":
        candidates = manager.list_candidates()
        for c in candidates:
            print(f"  {c['name']} - {c['created']}")
    
    elif args.action == "list-approved":
        approved = manager.list_approved()
        for a in approved:
            print(f"  {a['name']}")
