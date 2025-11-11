# Add-UserToAdminGroup.ps1
# Adds a user to an existing MCP Registry admin group

<#
.SYNOPSIS
    Adds a user to the MCP Registry administrators group.

.DESCRIPTION
    This script adds a user to an existing Entra ID security group for MCP Registry administrators.

.PARAMETER GroupObjectId
    The Object ID of the admin group. You can find this in the .env file as VITE_ENTRA_ADMIN_GROUP_ID

.PARAMETER UserPrincipalName
    The UPN (email) of the user to add to the admin group.

.PARAMETER UserObjectId
    The Object ID of the user (alternative to UserPrincipalName).

.EXAMPLE
    .\Add-UserToAdminGroup.ps1 -GroupObjectId "12345678-1234-1234-1234-123456789012" -UserPrincipalName "admin@contoso.com"
    
.EXAMPLE
    .\Add-UserToAdminGroup.ps1 -GroupObjectId "12345678-1234-1234-1234-123456789012" -UserObjectId "87654321-4321-4321-4321-210987654321"

.NOTES
    Prerequisites:
    - Azure CLI installed and logged in (az login)
    - Permissions to manage group membership in Entra ID
#>

[CmdletBinding(DefaultParameterSetName = 'ByUPN')]
param(
    [Parameter(Mandatory = $true)]
    [string]$GroupObjectId,
    
    [Parameter(Mandatory = $true, ParameterSetName = 'ByUPN')]
    [string]$UserPrincipalName,
    
    [Parameter(Mandatory = $true, ParameterSetName = 'ById')]
    [string]$UserObjectId
)

# Color output functions
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

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

# Check Azure CLI
Write-Info "Checking prerequisites..."
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed."
    exit 1
}

# Check if logged in
$accountInfo = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Not logged in to Azure CLI. Run 'az login' first."
    exit 1
}

Write-Success "Logged in to Azure CLI"

# Verify group exists
Write-Info "Verifying group exists..."
$groupJson = az ad group show --group $GroupObjectId 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Group not found: $GroupObjectId"
    Write-Info "Make sure you're using the correct Group Object ID from your .env file"
    exit 1
}

$group = $groupJson | ConvertFrom-Json
Write-Success "Found group: $($group.displayName)"

# Get user ID
if ($PSCmdlet.ParameterSetName -eq 'ByUPN') {
    Write-Info "Looking up user by UPN: $UserPrincipalName"
    $userJson = az ad user show --id $UserPrincipalName 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "User not found: $UserPrincipalName"
        exit 1
    }
    
    $user = $userJson | ConvertFrom-Json
    $UserObjectId = $user.id
} else {
    Write-Info "Looking up user by Object ID: $UserObjectId"
    $userJson = az ad user show --id $UserObjectId 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "User not found: $UserObjectId"
        exit 1
    }
    
    $user = $userJson | ConvertFrom-Json
}

Write-Success "Found user: $($user.displayName) ($($user.userPrincipalName))"

# Check if already a member
Write-Info "Checking current membership..."
$memberJson = az ad group member list --group $GroupObjectId --query "[?id=='$UserObjectId']" 2>$null | ConvertFrom-Json

if ($memberJson -and $memberJson.Count -gt 0) {
    Write-Warning "User is already a member of this group"
    exit 0
}

# Add user to group
Write-Info "Adding user to admin group..."
$addResult = az ad group member add --group $GroupObjectId --member-id $UserObjectId 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to add user to group: $addResult"
    exit 1
}

Write-Success "User successfully added to admin group!"
Write-Info ""
Write-Info "User '$($user.displayName)' will now have admin privileges in the MCP Registry."
Write-Info "They may need to log out and log back in for changes to take effect."
