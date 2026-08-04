# Workspace Modification Rules

## Overview
These rules govern how Hermes Agent may modify workspace files in cron task workspaces.

---

## Core Principles

1. **Never modify policy.md automatically** - Policy is immutable at runtime
2. **Always propose changes to instruction.md** - Changes require approval
3. **Keep only reusable knowledge** - No temporary data or debug output
4. **Use persistent task memory skill** - Leverage built-in versioning and change tracking
5. **Respect size limits** - Automatic summarization when thresholds exceeded
6. **Prevent concurrency conflicts** - File locking ensures safe access
7. **Track all changes** - Git version control when enabled
8. **Enable evolution** - Successful patterns can become reusable skills
9. **Dry run support** - Preview changes before applying
10. **Graceful degradation** - System remains operational even if protections fail

---

## Policy.md Rules

- **Status**: IMMUTABLE
- **Modification**: NEVER by Hermes Agent
- **Content**: Task-specific rules and constraints
- **Purpose**: Enforcement boundary that cannot be self-modified

---

## Instruction.md Rules

- **Status**: PROPOSED
- **Modification**: PROPOSAL_ONLY
- **Process**:
  1. Hermes Agent identifies needed changes
  2. Creates proposal in `proposals/` directory
  3. Human reviews and approves/rejects
  4. Only approved proposals are applied
- **Backup**: Original version saved before change
- **Validation**: Must pass policy checks before approval

---

## WORKSPACE.md Rules

- **Status**: AUTO-UPDATING
- **Modification**: AUTOMATIC
- **Content**: Reusable context, key findings, next steps
- **Rules**:
  - Remove outdated information
  - Keep only reusable knowledge
  - Automatic truncation at size limit
  - Status section updated after every run

---

## Memory.md Rules

- **Status**: AUTO-UPDATING
- **Modification**: AUTOMATIC
- **Content**: Verified facts, preferences, patterns
- **Rules**:
  - Store facts, not task logs
  - Deduplicate entries
  - Automatic summarization when full
  - One fact per line
  - Verified information only

---

## Journal.md Rules

- **Status**: AUTO-LOGGING
- **Modification**: APPEND-ONLY
- **Content**: Run history, timestamps, outcomes
- **Rules**:
  - Append new entries
  - Archive old entries automatically
  - Keep last N entries (configurable)
  - Never modify previous entries

---

## Protection System

### 1. File Locking
- **Purpose**: Prevent concurrent modification conflicts
- **Implementation**: `workspace_lock.py`
- **Features**:
  - File-based locking with timeout
  - Automatic lock release on process exit
  - Lock status checking
  - Deadlock prevention

### 2. Size Management
- **Purpose**: Prevent workspace bloat
- **Implementation**: `size_manager.py`
- **Features**:
  - Automatic summarization at 90% capacity
  - Archive old entries at 80% capacity
  - Warning when approaching limits
  - Configurable size thresholds

### 3. Version Control
- **Purpose**: Track all changes
- **Implementation**: `git_manager.py`
- **Features**:
  - Automatic git initialization
  - Commit after each run
  - Rollback capability
  - Diff viewing
  - Optional (enabled per workspace)

### 4. Skill Inheritance
- **Purpose**: Evolve successful patterns into reusable skills
- **Implementation**: `skill_evolution.py`
- **Features**:
  - Detect patterns after 25+ successes
  - Create candidate skills
  - Human approval workflow
  - Retire outdated skills
  - Inheritance chain management

### 5. Dry Run Mode
- **Purpose**: Preview changes before applying
- **Implementation**: `dry_run.py`
- **Features**:
  - Show proposed changes
  - No files modified
  - Save proposals for review
  - Clear proposals after approval

---

## Safety Mechanisms

### Immutable Policy
- Policy.md is the source of truth
- Cannot be modified by the task itself
- Changes require manual intervention
- Backups maintained in `versions/policy/`

### Proposal System
- Instruction changes require approval
- Proposals stored in `proposals/` directory
- Human review before application
- Confidence scoring for automatic decisions

### Automatic Recovery
- Lock timeout prevents deadlocks
- Size limits prevent bloat
- Version control enables rollback
- Graceful degradation if protections fail

---

## Workflow

```
Run Starts
    ↓
Acquire Lock
    ↓
Read Policy & Instruction
    ↓
Execute Task
    ↓
Check Size Limits
    ↓
Update WORKSPACE.md & memory.md
    ↓
Create Proposals (if needed)
    ↓
Append to Journal
    ↓
Create CHANGELOG entry
    ↓
Commit to Git (if enabled)
    ↓
Release Lock
    ↓
Check Evolution Candidates
```

---

## Implementation Notes

- Use `--dry-run` flag to preview changes
- Use `--git-commit` to enable version control
- Size limits: WORKSPACE.md (16KB), memory.md (32KB), journal.md (100KB)
- Lock timeout: 60 seconds
- Evolution threshold: 25 consecutive successes

---

## References

- Skill: `persistent-task-memory`
- Templates: `templates/`
- Scripts: `scripts/`
- Documentation: `SKILL.md`
