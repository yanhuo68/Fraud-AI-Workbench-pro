# 🚀 Personal Git & GitHub Reference Guide

This is your personal cheat sheet for managing the Fraud Investigation Workbench Pro codebase locally and syncing it with GitHub.

## 1. Initial Setup (Adding a Local Project to GitHub)

If you have a local project and want to push it to a new GitHub repository for the first time:

```bash
# 1. Initialize git in the root folder
git init

# 2. Add the GitHub repository URL as your "remote" connection
git remote add origin https://github.com/yanhuo68/Fraud-AI-Workbench-pro.git

# 3. Stage all your files to be tracked
git add .

# 4. Save (commit) these changes locally
git commit -m "Initial commit: Added project files"

# 5. Rename your default branch to 'main'
git branch -M main
```

### 🚨 Troubleshooting: Remote Contains Existing Work
If your GitHub repository was created with a `README.md`, `.gitignore`, or `LICENSE`, GitHub will reject your first push because the remote has files you don't have locally.
**Fix it by rebasing:**
```bash
# Pull the GitHub changes and apply your local commits on top of them
git pull --rebase origin main

# If Git complains about unrelated histories, force it:
git pull origin main --rebase --allow-unrelated-histories

# Now you can push safely!
git push -u origin main
```

### 🚨 Troubleshooting: Large File Error (GitHub 100MB Limit)
If your push fails with an error about exceeding GitHub's 100.00 MB limit (e.g., a large CSV or `.pkl` file):
```bash
# 1. Remove the large file/folder from Git's tracking index (keeps it on your disk)
git rm -r --cached path/to/large/folder/

# 2. Add that path to your .gitignore file so it isn't tracked again
echo "path/to/large/folder/" >> .gitignore
git add .gitignore

# 3. Amend your previous commit to rewrite history without the large file
git commit --amend --no-edit

# 4. Push again
git push -u origin main
```

---

## 2. Daily Routine (Fixing Bugs & Checking In Code)

This is the standard, everyday process you will follow after you write code, fix a bug, or add a feature.

### A. Check your current status
Always see what branch you are on and what files have changed before committing.
```bash
git status
# Shows modified files (red) and staged files (green)
```

### B. "Stage" the changes (Prepare them for saving)
```bash
# To add all changed/new/deleted files (respects .gitignore)
git add .

# Or, to add specific files only (good for targeted bug fixes):
git add src/api/main.py README.md
```

### C. "Commit" the changes (Save them locally)
A commit is a snapshot of your code. Make the message describe *why* or *what* you fixed.
```bash
git commit -m "Fix: Resolved null pointer exception in data ingestion pipeline"
# Or: "Feat: Added new sidebar Demo button"
```

### D. "Push" the changes (Upload to GitHub)
```bash
# Sends your local commits to the 'main' branch on GitHub
git push origin main
```

*(Tip: If you are the only one working on the project, this 4-step process `status -> add -> commit -> push` is all you need for your daily routine!)*

---

## 3. Working with Branches

Branches allow you to work on an experimental feature without breaking the stable (`main`) code.

### A. Create a new branch and switch to it
```bash
# Create a branch called 'feature/new-ui' and switch immediately
git checkout -b feature/new-ui
```

### B. Switch between existing branches
```bash
git checkout main
# ...or...
git checkout feature/new-ui
```

### C. Push a brand new local branch to GitHub
The first time you push a new branch, you must tell GitHub to track it:
```bash
git push -u origin feature/new-ui
```

---

## 4. Merging & Updating Code

When you want to combine work from one branch to another, or pull the latest changes from GitHub.

### A. Pulling changes from GitHub
If someone else (or you from another computer) pushed code to GitHub, download it:
```bash
# Make sure you are on the branch you want to update (e.g., main)
git checkout main
git pull origin main
```

### B. Standard Merge (Combine Branch A into Branch B)
Let's say you finished `feature/new-ui` and want to merge it into `main`.
```bash
# 1. Switch to the target branch
git checkout main

# 2. Merge the feature branch INTO your current branch (main)
git merge feature/new-ui

# 3. Don't forget to push the merged code to GitHub!
git push origin main
```

### C. Rebasing (Advanced - Keeping a linear history)
Instead of merging, `rebase` rewrites your branch's history to look like you *just* created it off the absolute latest `main` branch. This is great for keeping history clean, but **never rebase a branch that other people are actively using.**

```bash
# You are on feature/new-ui and you want to catch up with updates made to 'main'
git checkout main
git pull origin main           # Get latest main code
git checkout feature/new-ui    # Go back to your feature
git rebase main                # "Replay" your feature commits on top of the new main
```
If there are conflicts, Git will pause. You must edit the files to fix conflicts, then run `git add .`, followed by `git rebase --continue`.

---

## 5. Comparing Code (Diffs)

### A. See unsaved changes
```bash
# What have I changed since my last commit?
git diff
```

### B. See staged changes
```bash
# What changes are 'git add'-ed and ready to be committed?
git diff --staged
```

### C. Compare two branches
```bash
# See the differences between the current branch and main
git diff main
```

### D. See history log
```bash
# View recent commits (press 'q' to exit)
git log --oneline
```

---

## 6. Fixing Mistakes

### A. Undo changes to a file (Before committing)
```bash
# Throw away all unsaved edits to a specific file, reverting it to the last commit
git checkout -- src/api/main.py
```

### B. Unstage a file (Un-`git add` it)
```bash
# If you accidentally typed `git add .` and want to remove a file from staging
git reset HEAD secret_keys.txt
```

### C. Undo the very last commit (Keep the code changes!)
```bash
# Removes the commit from history, but leaves your files exactly as they are so you can fix the message or add more files.
git reset --soft HEAD~1
```

### D. Nuke everything (DANGER)
```bash
# Destroys all unsaved work and resets your local code exactly to the last commit
git reset --hard HEAD
```
