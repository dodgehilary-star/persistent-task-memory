# GitHub Sync Guide

This guide explains how to synchronize the Persistent Task Memory skill with GitHub.

---

## Quick Start

### Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
bash /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/scripts/setup_github_sync.sh
```

This will:
1. Initialize a git repository (if needed)
2. Configure your git user
3. Guide you through creating a GitHub repository
4. Push your code

### Option 2: Manual Setup

#### Step 1: Initialize Git Repository

```bash
cd /mnt/sdcard/shaun/hermes-agent
git init
git add .
git commit -m "Initial commit: Hermes Agent with Persistent Task Memory skill"
```

#### Step 2: Configure Git User

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### Step 3: Create GitHub Repository

**Option A: Using GitHub CLI (Recommended)**

```bash
# Install gh CLI if needed
sudo apt install gh

# Authenticate
gh auth login

# Create repository
gh repo create hermes-persistent-memory --public --push
```

**Option B: Manual Creation**

1. Go to https://github.com/new
2. Repository name: `hermes-persistent-memory`
3. Set to Public
4. Click "Create repository"
5. Copy the repository URL

#### Step 4: Add Remote and Push

```bash
cd /mnt/sdcard/shaun/hermes-agent
git remote add origin https://github.com/YOUR-USERNAME/hermes-persistent-memory.git
git push -u origin main
```

---

## Automated GitHub Sync

### Setup Automated Sync with Cron

To automatically sync your skill to GitHub every 6 hours:

```bash
# Edit crontab
crontab -e

# Add this line:
0 */6 * * * /mnt/sdcard/shaun/hermes-agent/.github/sync-to-github.sh
```

### GitHub Actions Workflow

A CI/CD workflow is automatically created at `.github/workflows/ci.yml`:

```yaml
name: Python CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m pip install --upgrade pip
      - run: python -m py_compile app/skills/persistent-task-memory/skill.py
```

---

## Using the GitHub Sync Script

### Python Script

```bash
# Initialize sync
python3 /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/scripts/github_sync.py --action init

# Sync manually
python3 /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/scripts/github_sync.py --action sync

# Check status
python3 /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/scripts/github_sync.py --action status

# Create CI workflow
python3 /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/scripts/github_sync.py --action workflow

# Setup automated sync
python3 /mnt/sdcard/shaun/hermes-agent/app/skills/persistent-task-memory/scripts/github_sync.py --action auto-sync
```

---

## Repository Structure

After setup, your repository will contain:

```
hermes-persistent-memory/
├── .github/
│   ├── workflows/
│   │   └── ci.yml              # CI/CD pipeline
│   └── sync-to-github.sh       # Automated sync script
├── app/
│   └── skills/
│       └── persistent-task-memory/
│           ├── SKILL.md
│           ├── skill.json
│           ├── skill.py
│           ├── README.md
│           ├── scripts/
│           │   ├── workspace_lock.py
│           │   ├── size_manager.py
│           │   ├── git_manager.py
│           │   ├── skill_evolution.py
│           │   ├── dry_run.py
│           │   ├── github_sync.py
│           │   └── setup_github_sync.sh
│           └── templates/
│               ├── policy.md
│               ├── instruction.md
│               ├── WORKSPACE.md
│               ├── memory.md
│               ├── journal.md
│               ├── identity.md
│               └── CHANGELOG.md
└── data/
    └── cron/
        └── tasks/              # Workspace examples
```

---

## Best Practices

### 1. Commit Messages

Use conventional commits:

```bash
git commit -m "feat: Add workspace lock protection"
git commit -m "fix: Resolve concurrent modification issue"
git commit -m "docs: Update README with GitHub sync guide"
git commit -m "chore: Update skill version to 1.1.0"
```

### 2. Branching Strategy

```bash
# Create feature branch
git checkout -b feature/skill-evolution

# Merge to main
git checkout main
git merge feature/skill-evolution
git push origin main
```

### 3. Releases

Tag releases for versioning:

```bash
git tag -a v1.1.0 -m "Release v1.1.0 with GitHub sync"
git push origin v1.1.0
```

---

## Troubleshooting

### "gh: command not found"

Install GitHub CLI:

```bash
sudo apt install gh
gh auth login
```

### "Permission denied (publickey)"

Generate SSH key:

```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
ssh-add ~/.ssh/id_ed25519
```

Add to GitHub:

```bash
cat ~/.ssh/id_ed25519.pub
# Copy output and add to GitHub: Settings → SSH Keys
```

### "Everything up-to-date"

Check status:

```bash
git status
git log --oneline -5
```

### Remote Already Exists

```bash
git remote remove origin
git remote add origin https://github.com/YOUR-USERNAME/hermes-persistent-memory.git
```

---

## Next Steps

1. ✅ Set up GitHub repository
2. ✅ Push your code
3. ⏳ Configure GitHub Actions (optional)
4. ⏳ Set up automated sync (optional)
5. ⏳ Share with others (optional)

---

**Happy Coding! 🚀**
