#!/usr/bin/env python3
"""Create workspace directory structure for a cron job."""

import sys
from pathlib import Path

def create_workspace(job_id: str, workspace_dir: Path) -> dict:
    """Create workspace directory and template files."""
    
    # Create directory structure
    dirs = [
        workspace_dir,
        workspace_dir / "versions" / "instruction",
        workspace_dir / "versions" / "workspace",
        workspace_dir / "versions" / "memory",
        workspace_dir / "output",
        workspace_dir / "proposals",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    
    # Copy templates
    templates_dir = Path(__file__).parent.parent / "templates"
    files = {
        "policy.md": templates_dir / "policy.md",
        "instruction.md": templates_dir / "instruction.md",
        "WORKSPACE.md": templates_dir / "WORKSPACE.md",
        "memory.md": templates_dir / "memory.md",
        "journal.md": templates_dir / "journal.md",
        "CHANGELOG.md": templates_dir / "CHANGELOG.md",
    }
    
    created = {}
    for name, src in files.items():
        dst = workspace_dir / name
        if not dst.exists():
            if src.exists():
                import shutil
                shutil.copy2(src, dst)
            else:
                dst.write_text(f"# {name}\n\n", encoding="utf-8")
        created[name] = dst
    
    return created


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: create_workspace.py <job_id> <workspace_dir>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    workspace_dir = Path(sys.argv[2])
    
    files = create_workspace(job_id, workspace_dir)
    print(f"Created workspace for job {job_id}")
    for name, path in files.items():
        print(f"  {name}: {path}")
