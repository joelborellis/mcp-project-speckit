# MCP Registry - Entra ID Admin Group Setup

This directory contains PowerShell scripts to manage the Entra ID admin group for the MCP Registry application.

## Prerequisites

- **Azure CLI** installed ([Download](https://aka.ms/installazurecli))
- Logged in to Azure CLI: `az login`
- Permissions to create groups and manage members in your Entra ID tenant

## Scripts

### 1. Setup-EntraIDAdminGroup.ps1

Creates the admin security group and optionally adds a user.

**Usage:**

```powershell
# Create group and add a user
.\Setup-EntraIDAdminGroup.ps1 -UserPrincipalName "admin@contoso.com"

# Create group only (no user)
.\Setup-EntraIDAdminGroup.ps1

# Custom group name
.\Setup-EntraIDAdminGroup.ps1 -GroupName "MyApp-Admins" -UserPrincipalName "user@domain.com"
```

**Output:** Group Object ID to add to your `.env` file

---

### 2. Add-UserToAdminGroup.ps1

Adds a user to an existing admin group.

**Usage:**

```powershell
# Add user by email
.\Add-UserToAdminGroup.ps1 -GroupObjectId "12345678-1234-1234-1234-123456789012" -UserPrincipalName "admin@contoso.com"

# Add user by Object ID
.\Add-UserToAdminGroup.ps1 -GroupObjectId "12345678-1234-1234-1234-123456789012" -UserObjectId "87654321-4321-4321-4321-210987654321"
```

---

### 3. List-AdminGroupMembers.ps1

Lists all members of the admin group.

**Usage:**

```powershell
.\List-AdminGroupMembers.ps1 -GroupObjectId "12345678-1234-1234-1234-123456789012"
```

---

## Quick Start Guide

### Step 1: Create Admin Group

```powershell
.\Setup-EntraIDAdminGroup.ps1 -UserPrincipalName "your-email@company.com"
```

The script will output:
```
Group Object ID: 12345678-1234-1234-1234-123456789012
```

### Step 2: Update Environment Variables

Add the Group Object ID to `frontend/.env`:

```bash
VITE_ENTRA_ADMIN_GROUP_ID=12345678-1234-1234-1234-123456789012
```

### Step 3: Restart Application

Restart the Vite dev server for changes to take effect:

```powershell
cd frontend
npm run dev
```

### Step 4: Test Admin Access

1. Log in to the application with the admin user
2. You should see the "Approvals" link in the navigation
3. The admin user can now approve/reject endpoint registrations

---

## Adding More Admins

To add additional administrators:

```powershell
.\Add-UserToAdminGroup.ps1 -GroupObjectId "YOUR-GROUP-ID" -UserPrincipalName "new-admin@company.com"
```

---

## Viewing Current Admins

To see who is currently an admin:

```powershell
.\List-AdminGroupMembers.ps1 -GroupObjectId "YOUR-GROUP-ID"
```

---

## Removing Admin Access

To remove a user from the admin group:

```powershell
az ad group member remove --group "YOUR-GROUP-ID" --member-id "USER-OBJECT-ID"
```

---

## Troubleshooting

### "Not logged in to Azure CLI"

Run: `az login`

### "Failed to find user"

- Verify the email address is correct
- Check the user exists in your Entra ID tenant
- Try using the User Object ID instead

### "Failed to create group"

- Verify you have Group Administrator or higher permissions
- Check if a group with the same name already exists

### Admin privileges not working

- Verify the Group Object ID in `.env` matches the actual group
- Ensure the user is a member of the group (use List-AdminGroupMembers.ps1)
- User must log out and log back in after being added to the group
- Clear browser cache/session storage

---

## Manual Alternative (Azure Portal)

If you prefer using the Azure Portal:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Entra ID** > **Groups**
3. Click **New Group**
4. Create a security group (e.g., "MCP-Registry-Admins")
5. Add members to the group
6. Copy the **Object ID** from the group's Overview page
7. Add to `frontend/.env`:
   ```
   VITE_ENTRA_ADMIN_GROUP_ID=<object-id>
   ```

---

## Security Notes

- The admin group grants full approval/rejection privileges
- Only add trusted users to this group
- Regularly audit group membership
- Consider implementing Just-In-Time (JIT) access for temporary admin needs
- The Group Object ID is not sensitive but should not be public
