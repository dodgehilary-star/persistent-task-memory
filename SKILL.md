---
name: persistent-task-memory
description: Use when creating cron tasks with persistent memory. Manages policy.md, instruction.md, WORKSPACE.md, memory.md, journal.md with versioning and change control.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cron, workspace, memory, versioning, persistent]
    related_skills: [cron-job-reliability, hermes-agent-skill-authoring]
---

# Persistent Task Memory Skill

## Overview

This skill provides every cron task with persistent memory, instructions, and controlled self-improvement through a standardized workspace structure. It extracts the workspace management logic from the core scheduler into a reusable skill, making the system cleaner and more maintainable.

## Workspace Structure

Every task workspace contains:

```
task/
├── policy.md          # Rules that cannot change
├── identity.md        # Task personality/purpose
├── instruction.md     # How to do this task
├── WORKSPACE.md       # Long-term context
├── memory.md          # Learned facts
├── journal.md         # History of runs
├── CHANGELOG.md       # Change tracking
├── versions/          # Version backups
│   ├── instruction/
│   ├── workspace/
│   └── memory/
├── output/            # Task outputs
└── proposals/         # Pending changes
```

## Execution Lifecycle

### Before Execution

1. Read `policy.md` - enforce rules
2. Read `instruction.md` - follow procedure
3. Read `WORKSPACE.md` - load context
4. Read `memory.md` - recall facts

### During Execution

- Follow policy rules
- Use workspace context
- Make decisions based on instructions

### After Execution

1. Write journal entry
2. Update memory if needed
3. Update workspace only when useful
4. Never modify policy.md
5. Append to CHANGELOG.md

## Skill Methods

### `prepare(job)`

Initialize workspace for a job.

```python
skill.prepare({
    "id": "job_id",
    "name": "job_name",
    "prompt": "task prompt",
    "workspace": {
        "enabled": True,
        "instruction": "task instructions",
        "workspace": "context content",
        "policy": "safety rules"
    }
})
```

### `inject(job)`

Return prompt with workspace context injected.

```python
prompt = skill.inject(job)
# Returns: "[SYSTEM: workspace context]\n\n[prompt]"
```

### `update(job, success, output)`

Update workspace files after job completion.

```python
skill.update(job, success=True, output="result text")
# Creates version backup
# Updates WORKSPACE.md
# Appends to journal.md
# Appends to CHANGELOG.md
```

### `validate(job)`

Check workspace health.

```python
issues = skill.validate(job)
# Returns list of issues found
```

## Implementation

Copy these files to `/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/`:

- `SKILL.md` - This file
- `templates/` - Workspace file templates
- `scripts/` - Utility scripts
- `README.md` - This documentation

## Workflow Integration

### Before (embedded logic):

```
scheduler.py
├── create workspace
├── read files
├── backup
└── reflection
```

### After (skill-based):

```
scheduler.py
└── load_skill("persistent-task-memory")
    ├── workspace creation
    ├── memory loading
    ├── backup
    └── reflection
```

The scheduler only schedules. The skill manages the intelligence.

## Future: Self-Created Skills

When tasks succeed repeatedly:

```
Task succeeds repeatedly
        ↓
Reflection
        ↓
Extract workflow
        ↓
Create new skill:
skills/pdf-report-generator/
skills/news-monitor/
skills/server-maintenance/
```

This enables skill evolution from successful task patterns.

## Files

### templates/policy.md

```markdown
# Job Policy

## Never:
- Delete files without confirmation
- Expose secrets in output
- Modify system configuration
- Change this policy file

## Workspace Modification Rules

Never modify policy.md automatically.

## Modification Authority

memory.md:
AUTO

journal.md:
AUTO

WORKSPACE.md:
AUTO if confidence > 0.8
PROPOSAL if confidence <= 0.8

instruction.md:
CREATE PROPOSAL ONLY
Never auto-update

## Reflection

After each task, review:
1. Did we learn reusable information?
2. Did the workflow improve?
3. Should instruction.md change?
4. Should memory.md change?
5. Should WORKSPACE.md change?

Do not change policy.md.

## Always:
- Verify before modifying
- Keep backups
- Log changes
```

### templates/instruction.md

```markdown
# Task Instructions

## Purpose
{{task_purpose}}

## Steps
1. Read policy.md
2. Read WORKSPACE.md
3. Follow instructions
4. Update workspace when useful

## Constraints
- Never delete files
- Always verify changes
- Keep output concise
```

### templates/WORKSPACE.md

```markdown
# Workspace

## Context
{{initial_context}}

## Status
- **Last Run**: {{timestamp}}
- **Status**: {{success/failure}}
```

### templates/memory.md

```markdown
# Memory

## Facts
- {{learned_facts}}

## Preferences
- {{user_preferences}}
```

### templates/journal.md

```markdown
# Journal

## {{date}}
**Time**: {{timestamp}}
**Status**: {{success/failure}}
**Output**: {{summary}}
```

### templates/CHANGELOG.md

```markdown
# Changes

## {{version}} - {{date}}

Changed:
{{description}}

Reason:
{{reason}}

Result:
{{success/failure}}
```

## Verification Checklist

- [ ] Workspace directory created at `data/cron/tasks/<job_id>/`
- [ ] All template files present
- [ ] Policy rules enforced
- [ ] Version backups working
- [ ] Journal entries appended
- [ ] CHANGELOG updated
