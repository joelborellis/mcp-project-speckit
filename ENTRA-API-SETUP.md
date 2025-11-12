# Entra ID API Configuration

## Issue
The backend is receiving tokens for Microsoft Graph API instead of tokens for your application. You need to configure your app registration to expose an API.

## Solution Steps

### 1. Expose an API in your App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Entra ID** > **App registrations**
3. Find your app: `<your-client-id>`
4. Click **Expose an API** in the left menu

### 2. Set Application ID URI

1. Click **Add** next to "Application ID URI"
2. Accept the default value: `api://<your-client-id>`
3. Click **Save**

### 3. Add a Scope

1. Click **+ Add a scope**
2. Fill in the form:
   - **Scope name**: `access_as_user`
   - **Who can consent?**: Admins and users
   - **Admin consent display name**: Access MCP Registry API
   - **Admin consent description**: Allows the app to access the MCP Registry API on behalf of the signed-in user
   - **User consent display name**: Access MCP Registry
   - **User consent description**: Allows the app to access your MCP Registry data
   - **State**: Enabled
3. Click **Add scope**

### 4. Add Authorized Client Applications (Optional but Recommended)

If your frontend and backend use the same app registration:

1. Scroll down to **Authorized client applications**
2. Click **+ Add a client application**
3. Enter your client ID: `<your-client-id>`
4. Check the scope you just created
5. Click **Add application**

### 5. Update API Permissions (if needed)

1. Go to **API permissions** in the left menu
2. You should see:
   - Microsoft Graph: `User.Read`, `GroupMember.Read.All` (for getting user groups)
   - Your API: `access_as_user` (this will be added automatically when you use the scope)

### 6. Verify Token Configuration

1. Go to **Token configuration** in the left menu
2. Ensure these optional claims are added for **Access tokens**:
   - `email`
   - `preferred_username`
   - `name`

## After Configuration

Once you've completed these steps:

1. **Restart your frontend** (clear browser cache/session storage if needed)
2. **Log out and log back in** to get a new token with the correct scope
3. The token will now have:
   - `aud` (audience): `api://<your-client-id>` or `<your-client-id>`
   - `iss` (issuer): `https://login.microsoftonline.com/<your-tenant-id>/v2.0`
   - `scp` (scope): `access_as_user`

## Troubleshooting

If you still get 401 errors:

1. **Check the token in the browser console:**
   ```javascript
   // In browser console after logging in
   sessionStorage.getItem('msal.token.keys')
   ```

2. **Decode the token at [jwt.ms](https://jwt.ms)** to verify:
   - `aud` claim matches your client ID
   - `iss` claim is from your tenant
   - Token is not expired

3. **Check backend logs** for specific validation errors

## Alternative: Use Client ID as Audience

If you don't want to set up the API scope, you can configure your app registration to accept tokens with the client ID as the audience:

1. Go to **Manifest** in your app registration
2. Find `"accessTokenAcceptedVersion": null` or `"accessTokenAcceptedVersion": 1`
3. Change it to: `"accessTokenAcceptedVersion": 2`
4. Save the manifest

Then update the frontend to use the client ID directly as the scope:
```typescript
scopes: [`${import.meta.env.VITE_ENTRA_CLIENT_ID}/.default`]
```

Instead of:
```typescript
scopes: [`api://${import.meta.env.VITE_ENTRA_CLIENT_ID}/.default`]
```
