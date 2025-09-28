from pydantic import BaseModel
from typing import List, Dict, Optional


class Card(BaseModel):
    id: str
    card_title: str
    name: str
    base_experience: int
    card_image: str
    rarity: str
    subtypes: List[str]
    value: float
    real_market_value: float
    discrepancy_ratio: float


class Trade(BaseModel):
    id: str
    userA: str
    cardA: Card
    userB: Optional[str] = None
    cardB: Optional[Card] = None
    confirmations: Dict[str, bool] = {}
    status: str = "pending"
    # Maybe you swap cards here???
    # -TODO-


class CreateTradeRequest(BaseModel):
    userA: str
    cardA: Card


class JoinTradeRequest(BaseModel):
    userB: str


class ConfirmRequest(BaseModel):
    user_id: str


class OfferRequest(BaseModel):
    user_id: str
    cardB: Card
