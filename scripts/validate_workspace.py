#!/usr/bin/env python3
"""Validate workspace structure and health."""

import sys
from pathlib import Path
from datetime import datetime, timedelta


def validate_workspace(workspace_dir: Path) -> list:
    """Check workspace for issues.
    
    Returns:
        List of issues found
    """
    issues = []
    
    # Check required files
    required_files = ["policy.md", "instruction.md", "WORKSPACE.md", "memory.md", "journal.md"]
    for f in required_files:
        if not (workspace_dir / f).exists():
            issues.append(f"Missing required file: {f}")
    
    # Check file sizes
    max_sizes = {
        "WORKSPACE.md": 12000,
        "memory.md": 4000,
        "journal.md": 8000,
        "instruction.md": 2000,
        "policy.md": 2000,
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
    
    return issues


def print_report(issues: list) -> None:
    """Print validation report."""
    if not issues:
        print("✓ Workspace is healthy")
    else:
        print(f"✗ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  • {issue}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_workspace.py <workspace_dir>")
        sys.exit(1)
    
    workspace_dir = Path(sys.argv[1])
    issues = validate_workspace(workspace_dir)
    print_report(issues)
    sys.exit(1 if issues else 0)
