#!/bin/bash
# Two-Way Sync Script for Persistent Task Memory
# Handles syncing between local and GitHub in both directions

set -e

SKILL_PATH="/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory"
REMOTE="origin"
BRANCH="main"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Two-Way Sync: Local ↔ GitHub                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd $SKILL_PATH

# Check if we're on the right branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo "⚠️  Warning: You're on branch '$CURRENT_BRANCH', expected '$BRANCH'"
    echo "   Switching to $BRANCH..."
    git checkout $BRANCH
fi

echo "📊 Current Status:"
git status --short
echo ""

# Step 1: Pull any changes from GitHub
echo "📥 Pulling from GitHub..."
git pull $REMOTE $BRANCH

if [ $? -eq 0 ]; then
    echo "✓ Pulled latest changes from GitHub"
else
    echo "⚠️  No changes to pull or merge conflict"
fi
echo ""

# Step 2: Check for local changes
LOCAL_CHANGES=$(git status --short)
if [ -z "$LOCAL_CHANGES" ]; then
    echo "✓ No local changes to push"
    echo ""
    echo "📝 Latest commits:"
    git log --oneline -3
    exit 0
fi

echo "📝 Local changes detected:"
echo "$LOCAL_CHANGES"
echo ""

# Step 3: Commit local changes
echo "💾 Committing local changes..."
git add .
git commit -m "sync: $(date '+%Y-%m-%d %H:%M:%S') - Two-way sync"

# Step 4: Push to GitHub
echo "📤 Pushing to GitHub..."
git push $REMOTE $BRANCH

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Sync completed successfully!"
    echo ""
    echo "📊 Summary:"
    echo "  • Pulled changes from GitHub"
    echo "  • Committed local changes"
    echo "  • Pushed to GitHub"
    echo ""
    echo "🔗 Repository: https://github.com/dodgehilary-star/persistent-task-memory"
else
    echo ""
    echo "❌ Push failed!"
    echo "Check your network connection and GitHub token permissions."
    exit 1
fi
