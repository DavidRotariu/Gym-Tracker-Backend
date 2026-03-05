from fastapi import HTTPException

from app.api.schemas.auth import UserResponse
from app.core.supabase import supabase_client
from app.repositories.auth_repository import AuthRepository


class AuthService:
    def __init__(self, repo: AuthRepository) -> None:
        self.repo = repo

    async def signup(self, email: str, password: str, name: str) -> UserResponse:
        response = supabase_client.auth.sign_up({"email": email, "password": password})
        if response.user is None:
            raise HTTPException(status_code=400, detail=response.error.message)

        existing_user = self.repo.get_by_auth_id(response.user.id)
        if existing_user:
            return UserResponse(id=existing_user.id, email=existing_user.email, name=existing_user.name)

        user = self.repo.create_user(response.user.id, email, name)
        return UserResponse(id=user.id, email=user.email, name=user.name)

    async def login(self, email: str, password: str) -> dict:
        response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        if response.user is None:
            raise HTTPException(status_code=400, detail=response.error.message)
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
        }

    async def me(self, token: str) -> UserResponse:
        user = supabase_client.auth.get_user(token)
        if user.user is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        db_user = self.repo.get_by_auth_id(user.user.id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(id=db_user.id, email=db_user.email, name=db_user.name)

    async def logout(self, token: str) -> dict:
        response = supabase_client.auth.sign_out(token)
        if response and response.error:
            raise HTTPException(status_code=500, detail="Failed to log out")
        return {"message": "User logged out successfully"}
