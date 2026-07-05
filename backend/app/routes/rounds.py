from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import User, Round, RoundEntry
from app.schemas import RoundResponse, RoundEntryCreate, RoundEntryResponse
from app.security import get_current_user
from datetime import datetime

router = APIRouter()


@router.get("/active", response_model=list[RoundResponse])
async def get_active_rounds(db: AsyncSession = Depends(get_db)):
    """Get all active rounds"""
    result = await db.execute(
        select(Round).where(
            (Round.status == "active") | (Round.status == "upcoming")
        ).order_by(Round.starts_at)
    )
    return result.scalars().all()


@router.get("/{round_id}", response_model=RoundResponse)
async def get_round(round_id: int, db: AsyncSession = Depends(get_db)):
    """Get round details"""
    result = await db.execute(select(Round).where(Round.id == round_id))
    round_obj = result.scalar_one_or_none()
    if not round_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    return round_obj


@router.post("/entry", response_model=RoundEntryResponse)
async def join_round(data: RoundEntryCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Join a round by selecting a number"""
    # Get round
    result = await db.execute(select(Round).where(Round.id == data.round_id))
    round_obj = result.scalar_one_or_none()
    if not round_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    
    # Check round is active
    if round_obj.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Round is not active")
    
    # Check number validity
    if not (1 <= data.selected_number <= 99):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number must be between 1 and 99")
    
    # Check number not taken
    result = await db.execute(
        select(RoundEntry).where(
            (RoundEntry.round_id == data.round_id) & (RoundEntry.selected_number == data.selected_number)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This number is already taken")
    
    # Check user has enough balance
    if user.wallet_balance < round_obj.entry_fee:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Insufficient wallet balance")
    
    # Deduct fee and create entry
    user.wallet_balance -= round_obj.entry_fee
    user.total_spent += round_obj.entry_fee
    
    entry = RoundEntry(
        user_id=user.id,
        round_id=round_obj.id,
        selected_number=data.selected_number,
        entry_fee=round_obj.entry_fee
    )
    round_obj.taken_slots += 1
    
    db.add(entry)
    db.add(user)
    db.add(round_obj)
    await db.commit()
    await db.refresh(entry)
    
    return entry


@router.get("/user/{user_id}/entries", response_model=list[RoundEntryResponse])
async def get_user_entries(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user's round entries"""
    result = await db.execute(select(RoundEntry).where(RoundEntry.user_id == user_id))
    return result.scalars().all()
