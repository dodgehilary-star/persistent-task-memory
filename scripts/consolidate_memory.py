#!/usr/bin/env python3
"""Consolidate memory and reflect on task improvements."""

import sys
from pathlib import Path
from datetime import datetime


def consolidate_memory(workspace_dir: Path) -> dict:
    """Review and consolidate memory file.
    
    Returns:
        dict with reflection results
    """
    memory_path = workspace_dir / "memory.md"
    journal_path = workspace_dir / "journal.md"
    instruction_path = workspace_dir / "instruction.md"
    
    results = {
        "facts_extracted": [],
        "recommendations": [],
        "should_update_instruction": False,
        "should_update_workspace": False,
    }
    
    # Read journal for recent entries
    if journal_path.exists():
        journal = journal_path.read_text()
        # Look for patterns like "Learned:" or "Noted:"
        for line in journal.split("\n"):
            line = line.strip()
            if line.startswith("Learned:") or line.startswith("Noted:"):
                fact = line.replace("Learned:", "").replace("Noted:", "").strip()
                if fact and fact not in results["facts_extracted"]:
                    results["facts_extracted"].append(fact)
    
    # Read memory for duplicates
    if memory_path.exists():
        memory = memory_path.read_text()
        for fact in results["facts_extracted"]:
            if fact in memory:
                results["recommendations"].append(f"Fact already exists: {fact[:50]}...")
            else:
                results["recommendations"].append(f"Add to memory: {fact[:50]}...")
    
    # Suggest instruction updates
    if len(results["facts_extracted"]) > 0:
        results["should_update_instruction"] = True
        results["recommendations"].append("Consider updating instruction.md with new learnings")
    
    return results


def print_report(results: dict) -> None:
    """Print reflection report."""
    print("\n=== Workspace Reflection ===\n")
    
    print("Facts Extracted:")
    for fact in results["facts_extracted"]:
        print(f"  • {fact}")
    
    print("\nRecommendations:")
    for rec in results["recommendations"]:
        print(f"  • {rec}")
    
    print(f"\nUpdate instruction.md: {results['should_update_instruction']}")
    print(f"Update WORKSPACE.md: {results['should_update_workspace']}")
    print("\n=== End Reflection ===\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: consolidate_memory.py <workspace_dir>")
        sys.exit(1)
    
    workspace_dir = Path(sys.argv[1])
    results = consolidate_memory(workspace_dir)
    print_report(results)
