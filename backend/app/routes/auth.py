from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from app.security import hash_password, verify_password, create_access_token
from datetime import timedelta

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    result = await db.execute(select(User).where((User.username == data.username) | (User.email == data.email)))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
    
    # Create new user
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        wallet_balance=0.0,
        vip_tier="bronze"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    return {
        "token": access_token,
        "user": UserResponse.model_validate(user)
    }


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user"""
    # Find user
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    return {
        "token": access_token,
        "user": UserResponse.model_validate(user)
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse.model_validate(user)


from app.security import get_current_user
