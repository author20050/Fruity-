from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Auth Schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    wallet_balance: float
    total_deposited: float
    total_spent: float
    total_won: float
    vip_tier: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


# Round Schemas
class RoundResponse(BaseModel):
    id: int
    title: str
    prize_pool: float
    entry_fee: float
    total_slots: int
    taken_slots: int
    status: str
    winning_number: Optional[int]
    starts_at: datetime
    ends_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class RoundCreate(BaseModel):
    title: str
    prize_pool: float
    entry_fee: float
    total_slots: int = 99
    starts_at: datetime
    ends_at: datetime


# Entry Schemas
class RoundEntryCreate(BaseModel):
    round_id: int
    selected_number: int


class RoundEntryResponse(BaseModel):
    id: int
    user_id: int
    round_id: int
    selected_number: int
    entry_fee: float
    created_at: datetime

    class Config:
        from_attributes = True


# Paystack Schemas
class PaystackVerifyResponse(BaseModel):
    status: str
    amount: float
    reference: str


# Admin Schemas
class AdminDrawWinner(BaseModel):
    round_id: int
    winning_number: int


class StatsResponse(BaseModel):
    total_players: int
    total_prize_paid: float
    active_rounds: int
    total_rounds_played: int
    total_revenue: float
