# GitHub Secrets Configuration

## Required Secret for CI/CD

This project requires the `INIA_API_KEY` secret to be configured in GitHub Actions for tests to pass.

## Setup Instructions

### 1. Add Secret to GitHub Repository

1. Go to your repository settings:
   - Navigate to: `https://github.com/reneignacio/iniamet-library/settings/secrets/actions`
   - Or: Settings → Secrets and variables → Actions

2. Add new repository secret:
   - Click **"New repository secret"**
   - **Name:** `INIA_API_KEY`
   - **Value:** `<your-inia-api-key-here>`
   - Click **"Add secret"**

### 2. Verify Configuration

After adding the secret:
1. Push changes to GitHub
2. Go to Actions tab
3. Check that tests pass with the real API key

## Security Best Practices

✅ **DO:**
- Store API keys in GitHub Secrets
- Use environment variables for local development
- Keep `.env` files in `.gitignore`

❌ **DON'T:**
- Commit API keys to the repository
- Share API keys in public files
- Hardcode secrets in source code

## Local Development

For local development, use a `.env` file (already gitignored):

```bash
INIA_API_KEY=your-api-key-here
```

Or set environment variable:

**Windows (PowerShell):**
```powershell
$env:INIA_API_KEY = "your-api-key-here"
```

**Linux/Mac (Bash):**
```bash
export INIA_API_KEY=your-api-key-here
```

## Read the Docs Integration

Once GitHub Actions tests pass:
1. Import project at: https://readthedocs.org/dashboard/
2. Select repository: `reneignacio/iniamet-library`
3. Documentation will build automatically using `.readthedocs.yaml`

---

**Note:** Never commit actual API keys. This file contains only instructions, not secrets.
