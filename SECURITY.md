# Security Policy

## API Key Security

### ⚠️ IMPORTANT: Never commit your API key to version control

This project requires users to configure their own API key. The API key should **NEVER** be committed to Git or shared publicly.

### Protected Files

The following files/directories are automatically excluded from Git (via `.gitignore`):

- `.iniamet/` - User configuration directory
- `config.ini` - Any configuration files
- `secrets.yaml` - Secret files
- `.env` and `.env.local` - Environment variable files
- `*.key` - Any key files

### How to Keep Your API Key Safe

✅ **DO:**
- Use environment variables: `export INIA_API_KEY='your-key'`
- Use the config file: `python -m iniamet.config set-key your-key`
- Pass the key programmatically: `INIAClient(api_key=os.environ['INIA_API_KEY'])`
- Store in password managers
- Use `.env` files (already in `.gitignore`)

❌ **DON'T:**
- Hardcode API keys in source code
- Commit API keys to Git
- Share API keys in public forums or documentation
- Include API keys in screenshots or logs

### For Developers

If you're contributing to this project:

1. **Never commit real API keys** - Use placeholder values in examples
2. **Check before committing**: Run `git diff` to review changes
3. **Use pre-commit hooks** (optional):
   ```bash
   pip install pre-commit
   pre-commit install
   ```
4. **If you accidentally commit a key**:
   - Revoke the key immediately
   - Remove it from Git history: `git filter-branch` or BFG Repo-Cleaner
   - Generate a new key

### Reporting Security Issues

If you discover a security vulnerability, please email:
- **Email**: climate-data@inia.cl
- **Subject**: [SECURITY] INIAMET Vulnerability Report

Please do NOT create public GitHub issues for security vulnerabilities.

## Dependencies Security

We regularly update dependencies to patch security vulnerabilities. To check for outdated packages:

```bash
pip list --outdated
pip-audit  # Install with: pip install pip-audit
```

## License

This security policy is part of the INIAMET project and is covered under the MIT License.
