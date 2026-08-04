# Persistent Task Memory - Maintenance Guide

## 📊 Current Status

**Repository**: https://github.com/dodgehilary-star/persistent-task-memory
**Version**: 1.1.0
**Local Path**: `/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory`
**Last Commit**: a2942e5 (feat: Add automated sync script)

---

## 🔄 Daily Maintenance

### Quick Check
```bash
# View recent commits
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
git log --oneline -5

# Check for changes
git status

# View file stats
git diff --stat HEAD~3
```

### Workspace Health Check
```bash
# Check workspace size
cd /home/hermes/workspace
du -sh .
wc -c WORKSPACE.md memory.md journal.md instruction.md

# Verify cron jobs are working
hermes cron list | grep -E "job_id|name"

# Test skill loads correctly
python3 -c "from skills.persistent_task_memory import PersistentTaskMemory; print('✓ Skill loads OK')"
```

---

## 📤 GitHub Sync

### Manual Sync
```bash
# 1. Make changes to skill files
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
nano skill.py  # or your editor

# 2. Stage and commit
git add .
git commit -m "feat: Updated memory consolidation logic

- Fixed duplicate entry issue in memory.md
- Added size limit enforcement
- Improved journal formatting"

# 3. Push to GitHub
git push origin main
```

### Automated Sync Script
```bash
# Run the sync script
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
.github/sync-to-github.sh

# Output:
# 🔄 Syncing to GitHub...
# ✓ No changes to sync
```

### Set Up Auto-Sync (Cron)
```bash
# Edit crontab
crontab -e

# Add line to sync every 6 hours
0 */6 * * * cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory && git add . && git commit -m "Auto-sync: $(date)" && git push origin main 2>&1

# Or use the provided script
0 */6 * * * /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/.github/sync-to-github.sh
```

---

## 🛠️ Skill Updates

### Updating Skill Code
```bash
# 1. Edit the skill
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
nano skill.py

# 2. Test syntax
python3 -m py_compile skill.py

# 3. Test each script
for script in scripts/*.py; do
    python3 -m py_compile "$script"
done

# 4. Commit and push
git add .
git commit -m "fix: Corrected memory consolidation issue"
git push origin main
```

### Version Bumping
```bash
# Edit skill.json to update version
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
nano skill.json

# Update "version": "1.1.0" → "1.2.0"

# Commit with version bump
git add skill.json SKILL.md
git commit -m "chore: Bump version to 1.2.0"
git tag v1.2.0
git push origin main --tags
```

---

## 📝 Workspace Management

### Current Workspace Files
```bash
# Check workspace status
cd /home/hermes/workspace
ls -la *.md
echo ""
echo "File sizes:"
wc -c WORKSPACE.md memory.md journal.md instruction.md policy.md
```

### Size Limits (from skill.py)
| File | Max Size | Current |
|------|----------|---------|
| WORKSPACE.md | 12,000 chars | 73921 chars (exceeds!) |
| memory.md | 4,000 chars | 487 chars ✓ |
| journal.md | 8,000 chars | - |
| instruction.md | 2,000 chars | 47 chars ✓ |
| policy.md | 2,000 chars | - |

⚠️ **Issue**: WORKSPACE.md exceeds the 12,000 char limit!

### Fix WORKSPACE.md
```bash
cd /home/hermes/workspace

# Compress to under 12,000 chars
python3 << 'EOF'
with open('WORKSPACE.md', 'r') as f:
    content = f.read()

if len(content) > 12000:
    # Keep only last 10,000 chars and add note
    new_content = "# Workspace\n\n[Truncated - was too large]\n\n" + content[-10000:]
    with open('WORKSPACE.md', 'w') as f:
        f.write(new_content)
    print(f"✓ Compressed from {len(content)} to {len(new_content)} chars")
else:
    print(f"✓ WORKSPACE.md is {len(content)} chars (OK)")
EOF

# Commit the fix
git add WORKSPACE.md
git commit -m "fix: Compressed WORKSPACE.md to fit size limits"
git push origin main
```

---

## 🔒 Security & Backups

### Token Security
```bash
# Check token file permissions
ls -la ~/.github-credentials
# Should be: -rw------- (600)

# Verify token content (redacted)
cat ~/.github-credentials | grep TOKEN
# Shows: GITHUB_TOKEN=ghp_x7FkY...J0f6aeC (last 4 visible)
```

### Backup Skill
```bash
# Create backup
cd /mnt/sdcard/shaun/hermes-agent/app/skills
tar -czf persistent-task-memory-backup-$(date +%Y%m%d).tar.gz persistent-task-memory/

# Or use git archive
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
git archive -o persistent-task-memory-backup.zip HEAD
```

### Restore from GitHub
```bash
# If local files are lost
cd /mnt/sdcard/shaun/hermes-agent/app/skills
rm -rf persistent-task-memory
git clone https://github.com/dodgehilary-star/persistent-task-memory.git
cd persistent-task-memory
chmod +x .github/sync-to-github.sh
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Git Push Fails
```bash
# Check remote URL
git remote -v

# Should show:
# origin  https://dodgehilary-star:ghp_x7F...@github.com/dodgehilary-star/persistent-task-memory.git

# Fix if needed
git remote set-url origin https://dodgehilary-star:$(cat ~/.github-credentials | grep GITHUB_TOKEN | cut -d= -f2)@github.com/dodgehilary-star/persistent-task-memory.git
```

#### 2. Skill Not Loading
```bash
# Check for syntax errors
python3 -m py_compile /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/skill.py

# Check imports
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
python3 -c "from scripts.workspace_lock import WorkspaceLock; print('✓ Lock OK')"
python3 -c "from scripts.size_manager import WorkspaceSizeManager; print('✓ Size OK')"
```

#### 3. GitHub API Issues
```bash
# Test token
export GH_TOKEN=$(cat ~/.github-credentials | grep GITHUB_TOKEN | cut -d= -f2)
gh api user --jq '.login'

# Should return: dodgehilary-star
```

---

## 📊 Maintenance Checklist

### Daily
- [ ] Check git status: `git status`
- [ ] Verify workspace files exist
- [ ] Check cron job status

### Weekly
- [ ] Review commit history: `git log --oneline -10`
- [ ] Check file sizes against limits
- [ ] Test skill loads correctly

### Monthly
- [ ] Update version in skill.json
- [ ] Review and compress WORKSPACE.md
- [ ] Create backup
- [ ] Check for GitHub security advisories

### As Needed
- [ ] Add new safeguards to skill.py
- [ ] Update templates in templates/
- [ ] Add new scripts to scripts/
- [ ] Update documentation

---

## 🚀 Advanced: Adding New Safeguards

```bash
# 1. Create new script
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/scripts
nano new_safeguard.py

# 2. Add to skill.py imports
# In skill.py, add:
# from new_safeguard import NewSafeguard

# 3. Add to MODIFICATION_AUTHORITY
# In skill.py, add new rule to MODIFICATION_AUTHORITY dict

# 4. Test
python3 -m py_compile scripts/new_safeguard.py
python3 -c "from scripts.new_safeguard import NewSafeguard; print('✓ New safeguard OK')"

# 5. Commit and push
git add .
git commit -m "feat: Add new safeguard for X"
git push origin main
```

---

## 📞 Quick Reference

### Essential Commands
```bash
# View skill status
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
git log --oneline -3
git status

# Check workspace
cd /home/hermes/workspace
wc -c *.md

# Sync to GitHub
.github/sync-to-github.sh

# View on GitHub
open https://github.com/dodgehilary-star/persistent-task-memory
```

### File Locations
| Purpose | Path |
|---------|------|
| Skill code | `/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/skill.py` |
| Templates | `/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/templates/` |
| Scripts | `/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/scripts/` |
| Workspace | `/home/hermes/workspace/` |
| Token | `/home/hermes/.github-credentials` |

---

**Last Updated**: 2026-08-05
**Version**: 1.1.0
