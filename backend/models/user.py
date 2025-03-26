from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    initial_balance: float = 500.0  # Default $500
    name: str = None
    phone_number: str = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    initial_balance: float = 500.0  # Default $500 if not provided

class User(BaseModel):
    id: str
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    portfolio: Dict = {}  # Empty portfolio
    transactions: List = []  # Empty transaction history
    created_at: datetime = datetime.now()
    last_login: datetime = None  # New field

    class Config:
        from_attributes = True 