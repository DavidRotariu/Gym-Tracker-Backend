from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase import supabase

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verifies Supabase JWT tokens and retrieves user information."""
    access_token = credentials.credentials
    user = supabase.auth.get_user(access_token)

    if user.get("error"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user["user"]
