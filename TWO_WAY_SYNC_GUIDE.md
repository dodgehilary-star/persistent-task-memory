# Two-Way Sync Guide

## How It Works

You can now edit your skill from **two places**:

### 1. **Local Editing** (on your server)
```bash
# Edit files directly
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
nano skill.py
# or
code .
```

### 2. **GitHub Editing** (via web browser)
```
Go to: https://github.com/dodgehilary-star/persistent-task-memory
Click any file → Edit icon (pencil) → Commit changes
```

---

## Sync Commands

### Manual Two-Way Sync
```bash
# Pull from GitHub, then push local changes
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
.github/two-way-sync.sh
```

### Quick Sync (Local → GitHub only)
```bash
git add .
git commit -m "update"
git push origin main
```

### Quick Pull (GitHub → Local only)
```bash
git pull origin main
```

---

## Typical Workflow

### Scenario 1: Edit Locally, Then Push
```bash
# 1. Edit on server
nano /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/skill.py

# 2. Sync to GitHub
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
.github/two-way-sync.sh
```

### Scenario 2: Edit on GitHub, Then Pull
```bash
# 1. Edit on GitHub website
#    https://github.com/dodgehilary-star/persistent-task-memory

# 2. Pull changes to server
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
.github/two-way-sync.sh
```

### Scenario 3: Both Sides Changed
```bash
# The two-way-sync script handles this:
# 1. Pulls GitHub changes first
# 2. Then commits and pushes local changes
# 3. If conflicts occur, git will notify you
```

---

## Conflict Resolution

If both sides edited the same file, Git will ask you to resolve conflicts:

```bash
# After git pull, if conflicts occur:
git status  # Shows conflicted files
# Edit the files to resolve conflicts (look for <<<<<<< markers)
git add .
git commit -m "resolve conflicts"
git push origin main
```

---

## Automated Sync Options

### Option 1: Every 6 Hours (Local → GitHub)
```bash
crontab -e
# Add:
0 */6 * * * cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory && git add . && git commit -m "auto-sync" && git push origin main
```

### Option 2: Every Hour (Two-Way)
```bash
crontab -e
# Add:
0 * * * * /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/.github/two-way-sync.sh
```

### Current Setting: Weekly (Sunday 9 AM)
✅ Already configured via cron job `persistent-task-memory-weekly-sync`

---

## Best Practices

### 1. **Commit Often Locally**
```bash
# Make small, frequent commits
git add .
git commit -m "fix: updated memory consolidation logic"
```

### 2. **Pull Before Pushing**
```bash
# Always pull first to avoid conflicts
git pull origin main
git push origin main
```

### 3. **Use Meaningful Commit Messages**
```bash
# Good:
git commit -m "feat: added size limit enforcement for memory.md"

# Bad:
git commit -m "update"
```

### 4. **Check Before Editing on GitHub**
```bash
# See what changed recently
git log --oneline -5
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| View status | `git status` |
| View changes | `git diff` |
| Pull from GitHub | `git pull origin main` |
| Push to GitHub | `git push origin main` |
| Two-way sync | `.github/two-way-sync.sh` |
| View history | `git log --oneline` |
| Undo last commit | `git revert HEAD` |

---

## Repository Info

- **Local Path**: `/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory`
- **GitHub URL**: https://github.com/dodgehilary-star/persistent-task-memory
- **Branch**: main
- **Auto-sync**: Every Sunday 9:00 AM

---

**You now have full two-way sync between local and GitHub! 🎉**
