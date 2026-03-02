"""Authentication API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import CurrentUser
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.models.team import Person
from app.schemas.user import AdminLoginRequest, UserLoginRequest, TokenResponse, UserResponse
from app.schemas.common import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login/admin", response_model=APIResponse[TokenResponse])
async def admin_login(
    credentials: AdminLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Admin user login with password.
    """
    # Find user by emp_id
    result = await db.execute(select(User).where(User.emp_id == credentials.emp_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or not an admin user"
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Get person info if exists
    person_result = await db.execute(select(Person).where(Person.emp_id == credentials.emp_id))
    person = person_result.scalar_one_or_none()

    # Create access token
    access_token = create_access_token(data={"sub": user.emp_id, "is_admin": user.is_admin})

    user_response = UserResponse(
        id=user.id,
        emp_id=user.emp_id,
        is_admin=user.is_admin
    )

    return APIResponse[TokenResponse](
        code=200,
        message="Login successful",
        data=TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    )


@router.post("/login/user", response_model=APIResponse[TokenResponse])
async def user_login(
    credentials: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Regular user login with employee ID only (no password).
    """
    # Find user by emp_id
    result = await db.execute(select(User).where(User.emp_id == credentials.emp_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Get person info
    person_result = await db.execute(select(Person).where(Person.emp_id == credentials.emp_id))
    person = person_result.scalar_one_or_none()

    # Create access token
    access_token = create_access_token(data={"sub": user.emp_id, "is_admin": user.is_admin})

    user_response = UserResponse(
        id=user.id,
        emp_id=user.emp_id,
        is_admin=user.is_admin
    )

    return APIResponse[TokenResponse](
        code=200,
        message="Login successful",
        data=TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    )


@router.post("/logout", response_model=APIResponse[None])
async def logout(current_user: CurrentUser):
    """
    Logout user (client-side token removal).
    """
    return APIResponse[None](
        code=200,
        message="Logout successful",
        data=None
    )


@router.get("/me", response_model=APIResponse[dict])
async def get_current_user_info(current_user: CurrentUser):
    """
    Get current user information.
    """
    return APIResponse[dict](
        code=200,
        message="Success",
        data={
            "id": current_user.id,
            "emp_id": current_user.emp_id,
            "is_admin": current_user.is_admin
        }
    )
