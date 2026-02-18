# 📤 How to Push to GitHub

## Step 1: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Fill in:
   - **Repository name**: `soccer-performance-analytics` (or your preferred name)
   - **Description**: "ML-powered soccer performance analytics platform for load monitoring and substitution prediction"
   - **Visibility**: Choose **Public** or **Private**
   - ⚠️ **DO NOT** check "Initialize this repository with:"
     - No README
     - No .gitignore
     - No license
3. Click **Create repository**

## Step 2: Connect Your Local Repository

Copy the commands shown on GitHub, or use these:

```bash
# Navigate to project directory (if not already there)
cd C:/Users/sorai/CascadeProjects/projeto_futebol/TESE_DOUTORAMENTO/09_IMPLEMENTACAO_TECNICA

# Add GitHub as remote (replace USERNAME and REPO_NAME)
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# Verify remote was added
git remote -v
```

## Step 3: Push Your Code

```bash
# Push all commits to GitHub
git push -u origin main
```

If you get an error about branch name:
```bash
# Rename branch to main if needed
git branch -M main
git push -u origin main
```

## Step 4: Verify on GitHub

Visit your repository URL: `https://github.com/USERNAME/REPO_NAME`

You should see:
- ✅ 151+ files
- ✅ README.md displayed on homepage
- ✅ Backend and Frontend folders
- ✅ MIT License badge

## What's Included

Your repository now contains:

### Documentation
- `README.md` - Project overview and architecture
- `SETUP.md` - Step-by-step setup guide
- `LICENSE` - MIT License
- `.gitignore` - Configured for Python, Node.js, and data files

### Backend (FastAPI)
- Complete REST API
- ML models (XGBoost + SHAP)
- Database connection
- Computer vision integration
- Pre-game prediction pipeline

### Frontend (React + Vite)
- Dark theme UI
- Dashboard with ML predictions
- Load monitoring
- Wellness tracking
- Multi-select operations
- Video analysis integration

### Configuration
- `backend/.env.example` - Database and API config
- `frontend/.env.example` - Frontend config

## Authentication (If Private Repo)

If pushing to a private repo, you may need to authenticate:

### Option 1: Personal Access Token (Recommended)

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name and select scopes: `repo`
4. Copy the token
5. When prompted for password, paste the token

### Option 2: SSH

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: Settings → SSH and GPG keys
# Then use SSH URL instead:
git remote set-url origin git@github.com:USERNAME/REPO_NAME.git
```

## Future Updates

After making changes:

```bash
# Stage changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push
```

## Repository Settings (Optional)

### Add Topics

On GitHub, add topics to make your repo discoverable:
- `soccer`
- `sports-analytics`
- `machine-learning`
- `xgboost`
- `fastapi`
- `react`
- `performance-monitoring`
- `load-management`

### Add Description

Update repository description to include:
- Purpose
- Key technologies
- Doctoral thesis mention

### Enable GitHub Pages (for pitch deck)

1. Settings → Pages
2. Source: Deploy from branch
3. Branch: `main`, folder: `/pitch_deck`
4. Your pitch deck will be live at: `https://username.github.io/repo-name/`

### Protect Main Branch

1. Settings → Branches
2. Add rule for `main`
3. Enable: Require pull request reviews

## Troubleshooting

### "Repository not found"
- Check repository URL is correct
- Verify you have access to the repository

### "Authentication failed"
- Use personal access token instead of password
- Or set up SSH authentication

### "Updates were rejected"
- Your local branch is behind: `git pull origin main`
- Then push: `git push origin main`

### Large files warning
- Video files and ML models are large
- Consider using Git LFS for files >50MB
- Or add them to `.gitignore` and store separately

## Next Steps

After pushing to GitHub:
1. ✅ Add repository description and topics
2. ✅ Create issues for future features
3. ✅ Add collaborators if needed
4. ✅ Set up CI/CD (GitHub Actions) for automated testing
5. ✅ Create project board for thesis progress tracking

---

**Need Help?** Check the [SETUP.md](SETUP.md) for local development setup.
