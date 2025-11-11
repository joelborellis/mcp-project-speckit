# List-AdminGroupMembers.ps1
# Lists all members of the MCP Registry admin group

<#
.SYNOPSIS
    Lists all members of the MCP Registry administrators group.

.DESCRIPTION
    This script displays all current members of the Entra ID admin group.

.PARAMETER GroupObjectId
    The Object ID of the admin group from your .env file (VITE_ENTRA_ADMIN_GROUP_ID)

.EXAMPLE
    .\List-AdminGroupMembers.ps1 -GroupObjectId "12345678-1234-1234-1234-123456789012"

.NOTES
    Prerequisites:
    - Azure CLI installed and logged in
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GroupObjectId
)

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

# Check Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed."
    exit 1
}

# Check if logged in
az account show 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Not logged in. Run 'az login' first."
    exit 1
}

# Get group info
Write-Info "Fetching group information..."
$groupJson = az ad group show --group $GroupObjectId 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Group not found: $GroupObjectId"
    exit 1
}

$group = $groupJson | ConvertFrom-Json
Write-Success "Group: $($group.displayName)"
Write-Info "Description: $($group.description)"
Write-Info ""

# Get members
Write-Info "Fetching group members..."
$membersJson = az ad group member list --group $GroupObjectId 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to fetch members: $membersJson"
    exit 1
}

$members = $membersJson | ConvertFrom-Json

if ($members.Count -eq 0) {
    Write-Info "No members in this group yet."
} else {
    Write-Success "Found $($members.Count) member(s):"
    Write-Info ""
    
    $members | ForEach-Object {
        Write-Host "  Name: " -NoNewline
        Write-Host $_.displayName -ForegroundColor Yellow
        Write-Host "  UPN:  " -NoNewline
        Write-Host $_.userPrincipalName -ForegroundColor Cyan
        Write-Host "  ID:   " -NoNewline
        Write-Host $_.id -ForegroundColor Gray
        Write-Host ""
    }
}
