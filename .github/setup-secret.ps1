# Setup GitHub Secret for INIA API Key
# This script helps you add the INIA_API_KEY secret to your GitHub repository

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub Secret Setup for INIA API Key" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is installed
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if (-not $ghInstalled) {
    Write-Host "⚠️  GitHub CLI (gh) is not installed." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You have two options:" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 1: Install GitHub CLI" -ForegroundColor Green
    Write-Host "  1. Visit: https://cli.github.com/" -ForegroundColor White
    Write-Host "  2. Download and install" -ForegroundColor White
    Write-Host "  3. Run: gh auth login" -ForegroundColor White
    Write-Host "  4. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2: Manual Setup (Recommended)" -ForegroundColor Green
    Write-Host "  1. Go to: https://github.com/reneignacio/iniamet-library/settings/secrets/actions" -ForegroundColor White
    Write-Host "  2. Click 'New repository secret'" -ForegroundColor White
    Write-Host "  3. Name: INIA_API_KEY" -ForegroundColor White
    Write-Host "  4. Value: c62532b6b1a1772f" -ForegroundColor White
    Write-Host "  5. Click 'Add secret'" -ForegroundColor White
    Write-Host ""
    Write-Host "See .github/SETUP_SECRETS.md for detailed instructions" -ForegroundColor Cyan
    exit
}

Write-Host "✓ GitHub CLI is installed" -ForegroundColor Green
Write-Host ""

# Check if user is authenticated
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  You are not logged in to GitHub CLI" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please run: gh auth login" -ForegroundColor White
    Write-Host "Then run this script again" -ForegroundColor White
    exit
}

Write-Host "✓ Authenticated with GitHub" -ForegroundColor Green
Write-Host ""

# Set the secret
Write-Host "Setting INIA_API_KEY secret..." -ForegroundColor Cyan
$apiKey = "c62532b6b1a1772f"

try {
    echo $apiKey | gh secret set INIA_API_KEY --repo reneignacio/iniamet-library
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Secret successfully added!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "  1. Push your changes to GitHub" -ForegroundColor White
        Write-Host "  2. GitHub Actions will use the secret automatically" -ForegroundColor White
        Write-Host "  3. Tests should now pass with real API data" -ForegroundColor White
        Write-Host ""
    } else {
        throw "Failed to set secret"
    }
} catch {
    Write-Host ""
    Write-Host "❌ Failed to set secret automatically" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set it manually:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://github.com/reneignacio/iniamet-library/settings/secrets/actions" -ForegroundColor White
    Write-Host "  2. Click 'New repository secret'" -ForegroundColor White
    Write-Host "  3. Name: INIA_API_KEY" -ForegroundColor White
    Write-Host "  4. Value: c62532b6b1a1772f" -ForegroundColor White
    Write-Host "  5. Click 'Add secret'" -ForegroundColor White
    Write-Host ""
}

Write-Host "For more information, see .github/SETUP_SECRETS.md" -ForegroundColor Cyan
