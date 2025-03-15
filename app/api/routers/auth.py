from fastapi import APIRouter, HTTPException, Header, Depends
from app.core.supabase import supabase_client
from app.db.database import session_scope
from app.db.models.users import User
from app.api.schemas.auth import UserSignup, UserLogin, UserResponse
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError

auth_router = APIRouter(tags=["Authentication"])

@auth_router.post("/auth/signup", response_model=UserResponse)
def signup(user_data: UserSignup):
    """Registers a new user via Supabase Auth"""
    response = supabase_client.auth.sign_up({"email": user_data.email, "password": user_data.password})

    if response.user is None:
        raise HTTPException(status_code=400, detail=response.error.message)

    supabase_user = response.user

    try:
        with session_scope() as session:
            existing_user = session.query(User).filter_by(auth_id=supabase_user.id).first()
            if existing_user:
                return UserResponse(id=existing_user.id, email=existing_user.email, name=existing_user.name)

            new_user = User(
                id=uuid4(),
                auth_id=supabase_user.id,
                email=user_data.email,
                name=user_data.name
            )
            session.add(new_user)
            session.commit()

            return UserResponse(id=new_user.id, email=new_user.email, name=new_user.name)

    except SQLAlchemyError as e:
        import traceback
        error_message = str(e.__dict__.get("orig", e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Database error: " + error_message)


@auth_router.post("/auth/login")
def login(user_data: UserLogin):
    """Logs in a user via Supabase Auth"""
    response = supabase_client.auth.sign_in_with_password({"email": user_data.email, "password": user_data.password})

    if response.user is None:
        raise HTTPException(status_code=400, detail=response.error.message)

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "token_type": "bearer"
    }


@auth_router.get("/auth/me", response_model=UserResponse)
def get_current_user(authorization: str = Header(None)):
    """Retrieves the currently authenticated user"""
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    user = supabase_client.auth.get_user(token)

    if user.user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=user.user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(id=db_user.id, email=db_user.email, name=db_user.name)


@auth_router.post("/auth/logout")
def logout(authorization: str = Header(None)):
    """Logs out the user"""
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    response = supabase_client.auth.sign_out(token)

    if response and response.error:
        raise HTTPException(status_code=500, detail="Failed to log out")

    return {"message": "User logged out successfully"}
