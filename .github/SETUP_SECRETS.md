# GitHub Secrets Setup

## Adding INIA API Key to GitHub Secrets

To make the tests pass in GitHub Actions, you need to add your INIA API key as a secret.

### Steps:

1. **Go to your repository on GitHub:**
   - Navigate to: https://github.com/reneignacio/iniamet-library

2. **Open Settings:**
   - Click on "Settings" (top menu)

3. **Navigate to Secrets:**
   - In the left sidebar, click on "Secrets and variables"
   - Then click on "Actions"

4. **Add New Secret:**
   - Click on "New repository secret" button

5. **Enter Secret Details:**
   - **Name:** `INIA_API_KEY`
   - **Value:** `c62532b6b1a1772f`
   - Click "Add secret"

### Verification:

After adding the secret:
1. Go to the "Actions" tab in your repository
2. Re-run the failed workflow or push a new commit
3. The tests should now pass with the real API key

### Security Notes:

✅ **Safe:** The API key is encrypted and only accessible to GitHub Actions
✅ **Hidden:** The key won't appear in logs or be visible to others
✅ **Secure:** Only repository collaborators with proper permissions can view/edit secrets

### Alternative: Using Environment Variables Locally

For local development, create a `.env` file (already in `.gitignore`):

```bash
INIA_API_KEY=c62532b6b1a1772f
```

Or set it in your shell:

**Windows (PowerShell):**
```powershell
$env:INIA_API_KEY = "c62532b6b1a1772f"
```

**Linux/Mac (Bash):**
```bash
export INIA_API_KEY=c62532b6b1a1772f
```

### Updating the Secret:

If you need to change the API key:
1. Go to Settings → Secrets and variables → Actions
2. Click on `INIA_API_KEY`
3. Click "Update secret"
4. Enter the new value and save

---

**Important:** Never commit the actual API key to the repository. Always use secrets or environment variables.
