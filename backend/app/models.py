from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    wallet_balance = Column(Float, default=0.0)
    total_deposited = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    total_won = Column(Float, default=0.0)
    vip_tier = Column(String(20), default="bronze")  # bronze, silver, gold, platinum
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deposits = relationship("Deposit", back_populates="user")
    entries = relationship("RoundEntry", back_populates="user")
    winners = relationship("Winner", back_populates="user")


class Round(Base):
    __tablename__ = "rounds"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    prize_pool = Column(Float, nullable=False)
    entry_fee = Column(Float, nullable=False)
    total_slots = Column(Integer, default=99)
    taken_slots = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active, upcoming, completed, cancelled
    winning_number = Column(Integer, nullable=True)  # Set by admin when draw happens
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    entries = relationship("RoundEntry", back_populates="round", cascade="all, delete-orphan")
    winners = relationship("Winner", back_populates="round", cascade="all, delete-orphan")


class RoundEntry(Base):
    __tablename__ = "round_entries"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    round_id = Column(Integer, ForeignKey("rounds.id"), nullable=False)
    selected_number = Column(Integer, nullable=False)
    entry_fee = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="entries")
    round = relationship("Round", back_populates="entries")


class Winner(Base):
    __tablename__ = "winners"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    round_id = Column(Integer, ForeignKey("rounds.id"), nullable=False)
    winning_number = Column(Integer, nullable=False)
    prize_amount = Column(Float, nullable=False)
    claimed = Column(Boolean, default=False)
    claimed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="winners")
    round = relationship("Round", back_populates="winners")


class Deposit(Base):
    __tablename__ = "deposits"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reference = Column(String(100), unique=True, nullable=False)
    status = Column(String(20), default="pending")  # pending, success, failed
    paystack_reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="deposits")
