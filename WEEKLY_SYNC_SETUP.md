# Weekly Sync - Setup Complete! ✅

## Cron Job Created

**Job ID**: `persistent-task-memory-weekly-sync`
**Schedule**: Every Sunday at 9:00 AM
**Status**: Active

---

## What It Does

Every Sunday at 9:00 AM, the system will:

1. ✅ Check for changes in the skill repository
2. ✅ Stage all modifications
3. ✅ Commit with timestamp
4. ✅ Push to GitHub automatically

---

## Script Location

```
/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/.github/weekly-sync.sh
```

---

## Manual Test

You can test the sync anytime by running:

```bash
cd /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory
.github/weekly-sync.sh
```

---

## Manage Cron Jobs

### View all jobs
```bash
hermes cron list
```

### Pause weekly sync
```bash
hermes cron pause persistent-task-memory-weekly-sync
```

### Resume weekly sync
```bash
hermes cron resume persistent-task-memory-weekly-sync
```

### Delete weekly sync
```bash
hermes cron delete persistent-task-memory-weekly-sync
```

### Run immediately
```bash
hermes cron run persistent-task-memory-weekly-sync
```

---

## Repository Info

- **URL**: https://github.com/dodgehilary-star/persistent-task-memory
- **Branch**: main
- **Last commit**: Will update every Sunday at 9 AM
- **Token**: Stored in ~/.github-credentials (chmod 600)

---

## Next Weekly Sync

**When**: This Sunday at 9:00 AM
**What**: Will check for changes and push any updates

---

You're all set! Your Persistent Task Memory skill will now sync automatically every week. 🎉
