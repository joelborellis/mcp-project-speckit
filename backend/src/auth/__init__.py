"""
Authentication Module

This package provides authentication and authorization functionality for the
MCP Registry Backend using Microsoft Entra ID (formerly Azure AD) tokens.

Modules:
    entra_validator: JWT token validation and user claim extraction

Functions exported from this package:
    - validate_token: Validate Entra ID JWT tokens
    - extract_user_claims: Extract user information from validated tokens

Example Usage:
    from auth import validate_token, extract_user_claims
    
    claims = validate_token(token_string)
    user_info = extract_user_claims(claims)
"""

from auth.entra_validator import validate_token, extract_user_claims

__all__ = ["validate_token", "extract_user_claims"]
