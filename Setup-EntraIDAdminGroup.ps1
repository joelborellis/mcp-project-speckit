# Setup-EntraIDAdminGroup.ps1
# Creates an Entra ID security group for MCP Registry admins and assigns a user

<#
.SYNOPSIS
    Creates an Entra ID security group for MCP Registry administrators and optionally adds a user.

.DESCRIPTION
    This script creates a security group in Microsoft Entra ID (Azure AD) for MCP Registry admins
    and optionally adds a user to the group. It outputs the Group Object ID needed for the .env file.

.PARAMETER GroupName
    The name of the security group to create. Default: "MCP-Registry-Admins"

.PARAMETER GroupDescription
    Description for the security group. Default: "Administrators for the MCP Registry application"

.PARAMETER UserPrincipalName
    The UPN (email) of the user to add to the admin group. Optional.

.EXAMPLE
    .\Setup-EntraIDAdminGroup.ps1 -UserPrincipalName "admin@contoso.com"
    
.EXAMPLE
    .\Setup-EntraIDAdminGroup.ps1 -GroupName "MyApp-Admins" -UserPrincipalName "user@domain.com"

.NOTES
    Prerequisites:
    - Azure CLI installed (https://aka.ms/installazurecli)
    - User must have permissions to create groups and add members in Entra ID
    - User must be logged in to Azure CLI (az login)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$GroupName = "MCP-Registry-Admins",
    
    [Parameter(Mandatory = $false)]
    [string]$GroupDescription = "Administrators for the MCP Registry application",
    
    [Parameter(Mandatory = $false)]
    [string]$UserPrincipalName
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

# Check if Azure CLI is installed
Write-Info "Checking prerequisites..."
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed. Please install from: https://aka.ms/installazurecli"
    exit 1
}

# Check if logged in
$accountInfo = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "You are not logged in to Azure CLI. Please run 'az login' first."
    exit 1
}

$account = $accountInfo | ConvertFrom-Json
Write-Success "Logged in as: $($account.user.name)"
Write-Info "Tenant ID: $($account.tenantId)"

# Check if group already exists
Write-Info "Checking if group '$GroupName' already exists..."
$existingGroup = az ad group list --filter "displayName eq '$GroupName'" 2>$null | ConvertFrom-Json

if ($existingGroup -and $existingGroup.Count -gt 0) {
    $groupId = $existingGroup[0].id
    Write-Warning "Group '$GroupName' already exists with Object ID: $groupId"
    $useExisting = Read-Host "Do you want to use this existing group? (Y/N)"
    
    if ($useExisting -ne 'Y' -and $useExisting -ne 'y') {
        Write-Info "Operation cancelled by user."
        exit 0
    }
} else {
    # Create the security group
    Write-Info "Creating security group '$GroupName'..."
    
    $groupJson = az ad group create `
        --display-name $GroupName `
        --mail-nickname $($GroupName -replace '[^a-zA-Z0-9]', '') `
        --description $GroupDescription `
        2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create group. Error: $groupJson"
        exit 1
    }
    
    $group = $groupJson | ConvertFrom-Json
    $groupId = $group.id
    Write-Success "Security group created successfully!"
}

Write-Info ""
Write-Info "═══════════════════════════════════════════════════════════"
Write-Success "Group Object ID: $groupId"
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info ""
Write-Info "Add this to your frontend/.env file:"
Write-Host "VITE_ENTRA_ADMIN_GROUP_ID=$groupId" -ForegroundColor Yellow
Write-Info ""

# Add user to group if specified
if ($UserPrincipalName) {
    Write-Info "Looking up user '$UserPrincipalName'..."
    
    $userJson = az ad user show --id $UserPrincipalName 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to find user '$UserPrincipalName'. Error: $userJson"
        Write-Warning "Group created but user not added. You can add users manually later."
        exit 0
    }
    
    $user = $userJson | ConvertFrom-Json
    $userId = $user.id
    Write-Success "Found user: $($user.displayName) ($($user.userPrincipalName))"
    
    # Check if user is already a member
    Write-Info "Checking if user is already a member..."
    $memberJson = az ad group member list --group $groupId --query "[?id=='$userId']" 2>$null | ConvertFrom-Json
    
    if ($memberJson -and $memberJson.Count -gt 0) {
        Write-Warning "User is already a member of the group."
    } else {
        Write-Info "Adding user to admin group..."
        
        $addResult = az ad group member add --group $groupId --member-id $userId 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to add user to group. Error: $addResult"
            Write-Warning "Group created but user not added. You can add the user manually."
            exit 0
        }
        
        Write-Success "User added to admin group successfully!"
    }
}

# Summary
Write-Info ""
Write-Info "═══════════════════════════════════════════════════════════"
Write-Success "Setup Complete!"
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info ""
Write-Info "Next steps:"
Write-Info "1. Update your frontend/.env file with:"
Write-Host "   VITE_ENTRA_ADMIN_GROUP_ID=$groupId" -ForegroundColor Yellow
Write-Info ""
Write-Info "2. To add more users to the admin group, run:"
Write-Host "   az ad group member add --group $groupId --member-id <user-object-id>" -ForegroundColor Cyan
Write-Info ""
Write-Info "3. To list all admin group members:"
Write-Host "   az ad group member list --group $groupId" -ForegroundColor Cyan
Write-Info ""
Write-Info "4. To remove a user from the admin group:"
Write-Host "   az ad group member remove --group $groupId --member-id <user-object-id>" -ForegroundColor Cyan
Write-Info ""
