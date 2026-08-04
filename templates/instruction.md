# Workspace Update Rules

Because Hermes can now update WORKSPACE.md and memory.md, add these rules to policy.md:

---

## Core Rules

### 1. Never Modify policy.md Automatically
- Policy is the immutable source of truth
- Any changes require manual human intervention
- Backups are maintained automatically

### 2. Propose Changes to instruction.md
- Hermes can identify needed changes
- Changes must go through proposal system
- Human must approve before application
- Original version backed up before change

### 3. Update WORKSPACE.md with Reusable Knowledge
- Remove outdated information
- Keep only reusable knowledge
- Summarize when approaching size limits
- Never include temporary data or debug output

### 4. Store Facts in memory.md
- Store verified facts, not task logs
- One fact per line
- Deduplicate entries
- Remove outdated facts
- Summarize when full

---

## Automation Rules

### When to Update Automatically
✓ WORKSPACE.md: After every run, update status and key context
✓ memory.md: When new verified facts are learned
✓ journal.md: Append new run entries
✓ CHANGELOG.md: Record all changes

### When to Propose
⚠ instruction.md: When improvements identified
⚠ policy.md: NEVER (requires manual intervention)
⚠ WORKSPACE.md: When major restructuring needed
⚠ memory.md: When fact consolidation needed

### Size Management
- WORKSPACE.md: Limit 16,000 chars, auto-truncate
- memory.md: Limit 32,000 chars, auto-summarize
- journal.md: Limit 100,000 chars, auto-archive
- instruction.md: Limit 8,000 chars
- policy.md: Limit 4,000 chars (read-only)

---

## Workspace Structure

```
task/
├── policy.md              ← NEVER modify
├── instruction.md         ← PROPOSAL_ONLY
├── WORKSPACE.md           ← AUTO_UPDATE
├── memory.md              ← AUTO_UPDATE
├── journal.md             ← APPEND_ONLY
├── CHANGELOG.md           ← APPEND_ONLY
├── versions/              ← Automatic backups
│   ├── policy/
│   ├── instruction/
│   ├── workspace/
│   └── memory/
├── proposals/             ← Pending change proposals
├── approval/              ← Approved changes
└── output/                ← Run output
```

---

## Safety Mechanisms

### 1. File Locking
- Prevents concurrent modification conflicts
- 60-second timeout
- Automatic release on process exit

### 2. Size Management
- Automatic summarization at 90% capacity
- Warning at 80% capacity
- Graceful degradation if limit exceeded

### 3. Version Control (Optional)
- Git integration for change tracking
- Rollback capability
- Diff viewing

### 4. Skill Evolution
- Detect successful patterns after 25+ runs
- Create candidate skills
- Human approval workflow

---

## Implementation

All protection systems are implemented in:
- `scripts/workspace_lock.py` - Concurrency control
- `scripts/size_manager.py` - Automatic size management
- `scripts/git_manager.py` - Version control
- `scripts/skill_evolution.py` - Pattern evolution
- `scripts/dry_run.py` - Change preview

---

## Testing

Run validation:
```bash
python3 /app/skills/persistent-task-memory/skill.py \
  --workspace-dir /path/to/workspace \
  --action validate
```

Test dry run:
```bash
python3 /app/skills/persistent-task-memory/skill.py \
  --workspace-dir /path/to/workspace \
  --action update \
  --dry-run \
  --success true \
  --output "Test output"
```

Test with git:
```bash
python3 /app/skills/persistent-task-memory/skill.py \
  --workspace-dir /path/to/workspace \
  --action prepare \
  --git-commit
```
