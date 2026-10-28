# Point AWS CLI/SDK at Floci for the current PowerShell session only.
# Usage:  . .\floci\floci-env.ps1
# Fake credentials on purpose: never put real AWS keys in this session.
$env:AWS_ENDPOINT_URL      = "http://localhost:4566"
$env:AWS_DEFAULT_REGION    = "us-east-1"
$env:AWS_ACCESS_KEY_ID     = "test"
$env:AWS_SECRET_ACCESS_KEY = "test"
Remove-Item Env:AWS_PROFILE, Env:AWS_SESSION_TOKEN -ErrorAction SilentlyContinue
Write-Host "AWS CLI now targets Floci at $env:AWS_ENDPOINT_URL (this window only)."
