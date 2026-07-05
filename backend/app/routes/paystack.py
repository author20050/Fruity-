from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Deposit
from app.schemas import PaystackVerifyResponse
from app.security import get_current_user
from app.config import settings
import httpx

router = APIRouter()


@router.get("/verify", response_model=PaystackVerifyResponse)
async def verify_payment(reference: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Verify Paystack payment and credit wallet"""
    
    # Verify with Paystack API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.paystack_api_url}/transaction/verify/{reference}",
            headers={"Authorization": f"Bearer {settings.paystack_secret_key}"}
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment verification failed")
    
    data = response.json()
    if not data.get("status"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment not successful")
    
    payment_data = data.get("data", {})
    if payment_data.get("status") != "success":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment not completed")
    
    amount = payment_data.get("amount", 0) / 100  # Convert kobo to naira
    
    # Check if deposit already processed
    result = await db.execute(select(Deposit).where(Deposit.paystack_reference == reference))
    existing_deposit = result.scalar_one_or_none()
    
    if existing_deposit:
        if existing_deposit.status == "success":
            return {
                "status": "success",
                "amount": existing_deposit.amount,
                "reference": reference
            }
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment already processed or failed")
    
    # Create deposit record
    deposit = Deposit(
        user_id=user.id,
        amount=amount,
        reference=reference,
        paystack_reference=reference,
        status="success"
    )
    
    # Credit wallet
    user.wallet_balance += amount
    user.total_deposited += amount
    
    db.add(deposit)
    db.add(user)
    await db.commit()
    
    return {
        "status": "success",
        "amount": amount,
        "reference": reference
    }
