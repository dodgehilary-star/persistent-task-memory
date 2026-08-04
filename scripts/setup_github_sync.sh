#!/bin/bash
# GitHub Sync Setup for Persistent Task Memory Skill
# This script helps you sync the skill to GitHub

set -e

SKILL_PATH="/mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory"
HERMES_PATH="/mnt/sdcard/shaun/hermes-agent"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Persistent Task Memory - GitHub Sync Setup              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first:"
    echo "   sudo apt install git"
    exit 1
fi
echo "✓ Git is installed: $(git --version)"

# Check if gh CLI is installed
if command -v gh &> /dev/null; then
    echo "✓ GitHub CLI (gh) is installed"
    gh auth status 2>&1 | head -5
else
    echo "⚠ GitHub CLI (gh) is not installed"
    echo "  Install with: sudo apt install gh"
fi

# Check if in git repo
if [ -d "$HERMES_PATH/.git" ]; then
    echo "✓ Hermes Agent is a git repository"
    cd $HERMES_PATH
    echo "  Remote: $(git remote get-url origin 2>/dev/null || echo 'No remote configured')"
else
    echo "⚠ Hermes Agent is not a git repository"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  STEP 1: Initialize Git Repository (if needed)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ ! -d "$HERMES_PATH/.git" ]; then
    echo "📁 Initializing git repository in Hermes Agent..."
    cd $HERMES_PATH
    git init
    git add .
    git commit -m "Initial commit: Hermes Agent with Persistent Task Memory skill"
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  STEP 2: Configure Git User (if needed)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

USER_NAME=$(git config --global user.name)
USER_EMAIL=$(git config --global user.email)

if [ -z "$USER_NAME" ] || [ "$USER_NAME" = "Not set" ]; then
    echo "⚠ Git user name not configured"
    read -p "Enter your name: " USER_NAME
    git config --global user.name "$USER_NAME"
fi

if [ -z "$USER_EMAIL" ] || [ "$USER_EMAIL" = "Not set" ]; then
    echo "⚠ Git user email not configured"
    read -p "Enter your email: " USER_EMAIL
    git config --global user.name "$USER_EMAIL"
fi

echo "✓ Git user configured:"
echo "  Name:  $USER_NAME"
echo "  Email: $USER_EMAIL"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  STEP 3: Create GitHub Repository"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "You have two options:"
echo ""
echo "  A) Use GitHub CLI (recommended)"
echo "     gh repo create hermes-persistent-memory --public --push"
echo ""
echo "  B) Create manually on github.com"
echo "     1. Go to https://github.com/new"
echo "     2. Name: hermes-persistent-memory"
echo "     3. Public repository"
echo "     4. Click 'Create repository'"
echo ""

read -p "Which option? (A/B): " OPTION

REMOTE_URL=""

if [ "$OPTION" = "A" ] || [ "$OPTION" = "a" ]; then
    if command -v gh &> /dev/null; then
        echo ""
        echo "🔄 Creating repository with GitHub CLI..."
        gh repo create hermes-persistent-memory --public --push 2>&1 || {
            echo "❌ Failed to create repository"
            exit 1
        }
        REMOTE_URL="https://github.com/$(gh api user --jq .login)/hermes-persistent-memory.git"
        echo "✓ Repository created: $REMOTE_URL"
    else
        echo "❌ GitHub CLI not installed. Please install it:"
        echo "   sudo apt install gh"
        exit 1
    fi
elif [ "$OPTION" = "B" ] || [ "$OPTION" = "b" ]; then
    echo ""
    read -p "Enter repository URL: " REMOTE_URL
else
    echo "❌ Invalid option"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  STEP 4: Add Remote and Push"
echo "═══════════════════════════════════════════════════════════════"
echo ""

cd $HERMES_PATH

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo "⚠ Remote 'origin' already exists"
    read -p "Replace existing remote? (y/N): " REPLACE
    if [ "$REPLACE" = "y" ] || [ "$REPLACE" = "Y" ]; then
        git remote set-url origin "$REMOTE_URL"
    else
        git remote add hermes "$REMOTE_URL"
        REMOTE_NAME="hermes"
    fi
else
    git remote add origin "$REMOTE_URL"
    REMOTE_NAME="origin"
fi

echo ""
echo "📤 Pushing to GitHub..."
git add .
git commit -m "feat: Add Persistent Task Memory skill v1.1.0 with 5 protection layers" || echo "  No changes to commit"
git push -u $REMOTE_NAME main 2>&1 || git push -u $REMOTE_NAME master

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     ✅ GitHub Sync Setup Complete!                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Repository: $REMOTE_URL"
echo ""
echo "Next steps:"
echo "  1. Review the repository on GitHub"
echo "  2. Set up GitHub Actions for CI/CD (optional)"
echo "  3. Configure automatic sync (optional)"
echo ""
