# 🔄 Change Default Branch to Develop

## Current Status
- **Current Default Branch**: `main`
- **Target Default Branch**: `develop`
- **Repository**: `intui/sensorapi`

## Steps to Change Default Branch (GitHub Web Interface)

### 1. Navigate to Repository Settings
1. Go to your GitHub repository: https://github.com/intui/sensorapi
2. Click on **"Settings"** tab (requires admin access)
3. Scroll down to **"General"** section

### 2. Change Default Branch
1. In the **"Default branch"** section, you'll see it's currently set to `main`
2. Click the **"Switch to another branch"** button (or the edit/pencil icon)
3. Select **`develop`** from the dropdown menu
4. Click **"Update"** 
5. Confirm the change when prompted

### 3. Verify the Change
After changing, you should see:
- Default branch is now `develop`
- New clones will automatically check out `develop`
- Pull requests will default to target `develop`

## Why This Makes Sense

Since you've merged all your public release preparation into `develop` and it contains:
- ✅ All open source documentation
- ✅ Clean codebase 
- ✅ Security enhancements
- ✅ Latest features

Making `develop` the default branch ensures:
- New contributors start with the most current code
- Pull requests target the active development branch
- The repository appears more active and up-to-date

## Alternative: Command Line Preparation

If you want to ensure `develop` has all content from `main`, you can sync them first:

```bash
# Check if main has anything develop doesn't
git checkout main
git log develop..main --oneline

# If main has commits develop needs, merge them:
# git checkout develop
# git merge main

# Otherwise, develop is ahead and ready to be the default
```

## After Changing Default Branch

1. **Update local clone commands** in documentation
2. **Notify team members** about the change
3. **Update CI/CD** if they reference the default branch
4. **Update README badges** if they reference `main`

---

**Note**: Only repository administrators can change the default branch through GitHub settings.