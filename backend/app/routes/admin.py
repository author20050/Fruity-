from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import User, Round, RoundEntry, Winner, UserRole
from app.schemas import RoundCreate, RoundResponse, AdminDrawWinner, StatsResponse
from app.security import get_admin_user
from datetime import datetime

router = APIRouter()


@router.post("/rounds/create", response_model=RoundResponse)
async def create_round(data: RoundCreate, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """Admin: Create a new round"""
    round_obj = Round(
        title=data.title,
        prize_pool=data.prize_pool,
        entry_fee=data.entry_fee,
        total_slots=data.total_slots,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
        status="active"
    )
    db.add(round_obj)
    await db.commit()
    await db.refresh(round_obj)
    return round_obj


@router.post("/rounds/{round_id}/draw")
async def draw_winner(data: AdminDrawWinner, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """Admin: Draw a winning number and award prize"""
    # Get round
    result = await db.execute(select(Round).where(Round.id == data.round_id))
    round_obj = result.scalar_one_or_none()
    if not round_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    
    # Get entry with winning number
    result = await db.execute(
        select(RoundEntry).where(
            (RoundEntry.round_id == data.round_id) & (RoundEntry.selected_number == data.winning_number)
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No player selected this number")
    
    # Get winner user
    result = await db.execute(select(User).where(User.id == entry.user_id))
    winner_user = result.scalar_one_or_none()
    
    # Set winning number
    round_obj.winning_number = data.winning_number
    round_obj.status = "completed"
    
    # Award prize to user
    winner_user.wallet_balance += round_obj.prize_pool
    winner_user.total_won += round_obj.prize_pool
    
    # Create winner record
    winner = Winner(
        user_id=entry.user_id,
        round_id=data.round_id,
        winning_number=data.winning_number,
        prize_amount=round_obj.prize_pool,
        claimed=True,
        claimed_at=datetime.utcnow()
    )
    
    db.add(winner)
    db.add(round_obj)
    db.add(winner_user)
    await db.commit()
    
    return {
        "message": f"Round {data.round_id} completed. Winner: {winner_user.username}",
        "prize": round_obj.prize_pool,
        "winner": winner_user.username
    }


@router.get("/stats", response_model=StatsResponse)
async def get_admin_stats(admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """Admin: Get platform statistics"""
    # Total players
    result = await db.execute(select(func.count(User.id)).where(User.role == UserRole.USER))
    total_players = result.scalar() or 0
    
    # Total prize paid
    result = await db.execute(select(func.sum(Winner.prize_amount)))
    total_prize_paid = result.scalar() or 0.0
    
    # Active rounds
    result = await db.execute(select(func.count(Round.id)).where(Round.status == "active"))
    active_rounds = result.scalar() or 0
    
    # Total rounds played
    result = await db.execute(select(func.count(Round.id)).where(Round.status == "completed"))
    total_rounds_played = result.scalar() or 0
    
    # Total revenue (sum of all entry fees)
    result = await db.execute(select(func.sum(RoundEntry.entry_fee)))
    total_revenue = result.scalar() or 0.0
    
    return {
        "total_players": total_players,
        "total_prize_paid": total_prize_paid,
        "active_rounds": active_rounds,
        "total_rounds_played": total_rounds_played,
        "total_revenue": total_revenue
    }


@router.get("/rounds")
async def admin_get_all_rounds(admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """Admin: Get all rounds"""
    result = await db.execute(select(Round).order_by(Round.created_at.desc()))
    return result.scalars().all()


@router.put("/rounds/{round_id}/status")
async def update_round_status(round_id: int, status: str, admin: User = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """Admin: Update round status"""
    valid_statuses = ["active", "upcoming", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Status must be one of {valid_statuses}")
    
    result = await db.execute(select(Round).where(Round.id == round_id))
    round_obj = result.scalar_one_or_none()
    if not round_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    
    round_obj.status = status
    db.add(round_obj)
    await db.commit()
    
    return {"message": f"Round {round_id} status updated to {status}"}
