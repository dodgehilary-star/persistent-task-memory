#!/bin/bash
# Weekly Sync Script for Persistent Task Memory
# This script is called by the cron job every Sunday at 9:00 AM

set -e

SKILL_PATH="/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
BRANCH="main"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Weekly Sync: Persistent Task Memory                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📅 Date: $TIMESTAMP"
echo ""

# Navigate to skill directory
cd $SKILL_PATH

# Check git status
echo "📊 Checking for changes..."
CHANGES=$(git status --short)

if [ -z "$CHANGES" ]; then
    echo "✓ No changes detected - nothing to sync"
    echo ""
    echo "📝 Recent commits:"
    git log --oneline -3
    exit 0
fi

echo "📝 Changes detected:"
echo "$CHANGES"
echo ""

# Stage all changes
echo "📦 Staging changes..."
git add .

# Create commit message
COMMIT_MSG="weekly sync: $TIMESTAMP

Auto-synced changes to Persistent Task Memory skill."

# Commit changes
echo "💾 Committing..."
git commit -m "$COMMIT_MSG"

# Get commit hash
COMMIT_HASH=$(git rev-parse --short HEAD)
echo "✓ Committed: $COMMIT_HASH"
echo ""

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin $BRANCH

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Sync completed successfully!"
    echo ""
    echo "📊 Repository: https://github.com/dodgehilary-star/persistent-task-memory"
    echo "📝 Latest commit: $COMMIT_HASH"
    echo ""
    echo "📝 Recent commits:"
    git log --oneline -5
else
    echo ""
    echo "❌ Push failed!"
    echo "Check your GitHub token permissions and network connection."
    exit 1
fi
