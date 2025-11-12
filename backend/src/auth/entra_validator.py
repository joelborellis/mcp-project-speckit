"""
Entra ID Token Validator

This module provides token validation for Microsoft Entra ID (formerly Azure AD) JWT tokens.
It validates token signatures using JWKS (JSON Web Key Set), checks issuer, audience, and
expiration claims, and extracts user information from validated tokens.

Key Features:
- Fetches JWKS from Microsoft's public endpoint for signature verification
- Validates token issuer matches expected Entra ID tenant
- Checks audience claim matches expected client ID
- Verifies token expiration (exp claim)
- Extracts user claims: entra_id (sub), email, display_name (name)
- Caches JWKS for 24 hours to minimize external requests

Example Usage:
    from auth.entra_validator import validate_token, extract_user_claims
    
    try:
        # Validate token
        claims = validate_token(token_string)
        
        # Extract user information
        user_info = extract_user_claims(claims)
        # user_info = {"entra_id": "...", "email": "...", "display_name": "..."}
    except ValueError as e:
        # Token validation failed
        print(f"Invalid token: {e}")

Token Format:
    Bearer tokens are expected in format: "Bearer <jwt_token>"
    Extract the JWT portion before passing to validate_token()

Security Notes:
- Always validate tokens on the server side (never trust client-side validation)
- JWKS caching reduces latency but requires periodic refresh (24h TTL)
- Tokens with expired claims are rejected immediately
- Invalid signatures, issuer, or audience result in ValueError exceptions
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from urllib.request import urlopen
import json

import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from config import settings

logger = logging.getLogger(__name__)

# Cache JWKS for 24 hours to reduce external requests
_jwks_client: Optional[PyJWKClient] = None
_jwks_cache_time: Optional[datetime] = None
JWKS_CACHE_DURATION = timedelta(hours=24)


def _get_jwks_client() -> PyJWKClient:
    """
    Get or create a PyJWKClient for JWKS retrieval.
    
    The client fetches public keys from Microsoft's JWKS endpoint to verify
    JWT token signatures. Keys are cached for 24 hours to minimize external requests.
    
    Returns:
        PyJWKClient: Configured client for fetching JWKS keys
        
    Example:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
    
    Notes:
        - JWKS endpoint URL is constructed from tenant ID in settings
        - Cache is automatically refreshed after 24 hours
        - Thread-safe (uses global cache variables)
    """
    global _jwks_client, _jwks_cache_time
    
    now = datetime.utcnow()
    
    # Return cached client if still valid
    if _jwks_client and _jwks_cache_time and (now - _jwks_cache_time) < JWKS_CACHE_DURATION:
        return _jwks_client
    
    # Create new client and update cache
    logger.info(f"Initializing JWKS client for endpoint: {settings.jwks_uri}")
    _jwks_client = PyJWKClient(settings.jwks_uri)
    _jwks_cache_time = now
    
    return _jwks_client


def validate_token(token: str) -> Dict[str, Any]:
    """
    Validate a JWT token from Microsoft Entra ID.
    
    Performs comprehensive validation:
    1. Fetches signing key from JWKS endpoint
    2. Verifies JWT signature using RS256 algorithm
    3. Checks token expiration (exp claim)
    4. Validates issuer matches expected Entra ID authority
    5. Validates audience matches expected client ID
    
    Args:
        token: JWT token string (without "Bearer " prefix)
        
    Returns:
        Dict[str, Any]: Decoded token claims (payload) if validation succeeds
        
    Raises:
        ValueError: If token is invalid, expired, or has wrong issuer/audience
        
    Example:
        token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
        
        try:
            claims = validate_token(token)
            user_id = claims['sub']  # Entra ID user ID
            email = claims['email']
        except ValueError as e:
            print(f"Token validation failed: {e}")
            
    Security Notes:
        - Always call this function server-side
        - Never accept unvalidated tokens
        - Expired tokens are rejected immediately
        - Invalid signatures indicate tampering or wrong tenant
    """
    try:
        # Get JWKS client (uses cache if available)
        jwks_client = _get_jwks_client()
        
        # Get signing key for this token
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # First decode without verification to see what we have (for debugging)
        unverified_claims = jwt.decode(token, options={"verify_signature": False})
        logger.info(f"Token claims (unverified): aud={unverified_claims.get('aud')}, iss={unverified_claims.get('iss')}, exp={unverified_claims.get('exp')}")
        
        # Decode and validate token
        # Note: Microsoft tokens may have issuer in two formats:
        # - v2.0: https://login.microsoftonline.com/{tenant}/v2.0
        # - v1.0: https://sts.windows.net/{tenant}/
        # Audience may be either the client ID or api://{client_id}
        valid_audiences = [
            settings.azure_client_id,
            f"api://{settings.azure_client_id}"
        ]
        
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": False,  # We'll verify audience manually to accept both formats
                "verify_iss": False,  # We'll verify issuer manually to handle both v1 and v2
            }
        )
        
        # Manually verify audience (accept both client ID and api:// format)
        audience = claims.get("aud", "")
        if audience not in valid_audiences:
            logger.warning(f"Invalid audience: {audience}. Expected one of: {valid_audiences}")
            raise ValueError(f"Audience doesn't match")
        
        # Manually verify issuer (accept both v1.0 and v2.0 formats)
        issuer = claims.get("iss", "")
        valid_issuers = [
            f"https://login.microsoftonline.com/{settings.azure_tenant_id}/v2.0",
            f"https://sts.windows.net/{settings.azure_tenant_id}/",
        ]
        
        if issuer not in valid_issuers:
            logger.warning(f"Invalid issuer: {issuer}. Expected one of: {valid_issuers}")
            raise ValueError(f"Invalid token issuer: {issuer}")
        
        logger.info(f"Token validated successfully for user: {claims.get('sub', 'unknown')}")
        return claims
        
    except ExpiredSignatureError:
        logger.warning("Token validation failed: Token has expired")
        raise ValueError("Token has expired")
    except InvalidTokenError as e:
        logger.warning(f"Token validation failed: {str(e)}")
        raise ValueError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise ValueError(f"Token validation error: {str(e)}")


def extract_user_claims(claims: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user information from validated token claims.
    
    Extracts standard user fields from the JWT payload:
    - entra_id: Unique user identifier from 'sub' claim
    - email: User's email address from 'email' or 'preferred_username' claim
    - display_name: User's display name from 'name' claim
    
    Args:
        claims: Decoded JWT claims dictionary (from validate_token())
        
    Returns:
        Dict[str, Any]: Dictionary with keys: entra_id, email, display_name
        
    Example:
        claims = validate_token(token)
        user_info = extract_user_claims(claims)
        
        # user_info = {
        #     "entra_id": "abc-123-def-456",
        #     "email": "user@example.com",
        #     "display_name": "John Doe"
        # }
        
    Notes:
        - 'sub' claim is always present in valid Entra ID tokens
        - Email may come from 'email' or 'preferred_username' claim
        - Display name may be None if 'name' claim is not present
        - All values are returned as strings or None
    """
    # Extract entra_id from 'sub' claim (always present)
    entra_id = claims.get("sub")
    
    # Extract email - try multiple claim sources in order of preference:
    # 1. email - standard email claim (v2.0 tokens with profile scope)
    # 2. preferred_username - often contains email (v2.0 tokens)
    # 3. upn - User Principal Name (v1.0 tokens, typically email format)
    # 4. unique_name - alternative name claim (v1.0 tokens)
    email = (
        claims.get("email") or 
        claims.get("preferred_username") or 
        claims.get("upn") or 
        claims.get("unique_name")
    )
    
    # Extract display name from 'name' claim (may be None)
    display_name = claims.get("name")
    
    # Debug: Log all available claims to see what we have
    logger.debug(f"All available claims: {list(claims.keys())}")
    logger.debug(f"Full claims (filtered): sub={claims.get('sub')}, email={claims.get('email')}, preferred_username={claims.get('preferred_username')}, name={claims.get('name')}, upn={claims.get('upn')}, unique_name={claims.get('unique_name')}")
    logger.debug(f"Group claims: groups={claims.get('groups')}, wids={claims.get('wids')}, roles={claims.get('roles')}")
    
    user_info = {
        "entra_id": entra_id,
        "email": email,
        "display_name": display_name
    }
    
    logger.debug(f"Extracted user claims: entra_id={entra_id}, email={email}")
    
    return user_info
