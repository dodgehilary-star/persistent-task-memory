#!/bin/bash
# Automated GitHub Sync Script
# Run this script periodically to sync changes to GitHub

set -e

REPO_PATH="/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory"
REMOTE="origin"
BRANCH="main"

echo "🔄 Syncing to GitHub..."
echo ""

cd $REPO_PATH

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not a git repository"
    exit 1
fi

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    echo "✓ No changes to sync"
    exit 0
fi

# Stage all changes
git add .

# Commit with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
git commit -m "Auto-sync: $TIMESTAMP" || echo "  No changes to commit"

# Push to GitHub
git push $REMOTE $BRANCH

echo "✓ Synced to GitHub: https://github.com/dodgehilary-star/persistent-task-memory"
