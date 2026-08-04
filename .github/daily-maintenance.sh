#!/bin/bash
# Daily Maintenance Script
# Run this daily to check health and sync

set -e

SKILL_PATH="/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory"
WORKSPACE="/home/hermes/workspace"
TOKEN_FILE="/home/hermes/.github-credentials"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Persistent Task Memory - Daily Maintenance              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Check git status
echo "📊 Git Status:"
cd $SKILL_PATH
git status --short
echo ""

# 2. Check recent commits
echo "📝 Recent Commits:"
git log --oneline -3
echo ""

# 3. Check workspace file sizes
echo "📦 Workspace Sizes:"
if [ -d "$WORKSPACE" ]; then
    cd $WORKSPACE
    for file in WORKSPACE.md memory.md journal.md instruction.md policy.md; do
        if [ -f "$file" ]; then
            size=$(wc -c < "$file" | tr -d ' ')
            echo "  $file: $size chars"
        fi
    done
else
    echo "  ⚠️ Workspace not found at $WORKSPACE"
fi
echo ""

# 4. Test skill syntax
echo "🔍 Syntax Check:"
python3 -m py_compile $SKILL_PATH/skill.py && echo "  ✓ skill.py OK"
for script in $SKILL_PATH/scripts/*.py; do
    python3 -m py_compile "$script" 2>/dev/null && echo "  ✓ $(basename $script) OK"
done
echo ""

# 5. Check token
echo "🔐 Token Status:"
if [ -f "$TOKEN_FILE" ]; then
    token=$(grep GITHUB_TOKEN "$TOKEN_FILE" | cut -d= -f2)
    if [ -n "$token" ]; then
        last4=${token: -4}
        echo "  ✓ Token configured (ending in $last4)"
    else
        echo "  ⚠️ Token not found in $TOKEN_FILE"
    fi
else
    echo "  ⚠️ Token file not found at $TOKEN_FILE"
fi
echo ""

# 6. GitHub connectivity
echo "🌐 GitHub Status:"
export GH_TOKEN=$(grep GITHUB_TOKEN "$TOKEN_FILE" | cut -d= -f2)
if command -v gh &> /dev/null; then
    gh auth status 2>/dev/null && echo "  ✓ gh CLI authenticated" || echo "  ⚠️ gh CLI not authenticated"
else
    echo "  ⚠️ gh CLI not installed (using git directly)"
fi
echo ""

# 7. Check for workspace size issues
echo "⚠️ Size Limit Checks:"
cd $WORKSPACE
for file in WORKSPACE.md memory.md journal.md instruction.md policy.md; do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file" | tr -d ' ')
        case $file in
            WORKSPACE.md)
                if [ $size -gt 12000 ]; then
                    echo "  🔴 $file: $size chars (LIMIT: 12000) - TOO LARGE!"
                else
                    echo "  ✓ $file: $size chars (OK)"
                fi
                ;;
            memory.md)
                if [ $size -gt 4000 ]; then
                    echo "  🔴 $file: $size chars (LIMIT: 4000) - TOO LARGE!"
                else
                    echo "  ✓ $file: $size chars (OK)"
                fi
                ;;
            journal.md)
                if [ $size -gt 8000 ]; then
                    echo "  🔴 $file: $size chars (LIMIT: 8000) - TOO LARGE!"
                else
                    echo "  ✓ $file: $size chars (OK)"
                fi
                ;;
        esac
    fi
done
echo ""

# 8. Sync if changes exist
if git diff --quiet && git diff --cached --quiet; then
    echo "✓ No changes to sync"
else
    echo "🔄 Changes detected - run manual sync:"
    echo "   cd $SKILL_PATH && git add . && git commit -m 'daily check' && git push"
fi
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Daily Maintenance Complete                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
