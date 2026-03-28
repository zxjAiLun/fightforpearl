from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class GameAction(BaseModel):
    action: str
    payload: dict = {}

class CardData(BaseModel):
    id: str
    name: str
    card_type: str
    description: str
    rarity: int

class GameState(BaseModel):
    game_id: str
    floor: int
    total_floors: int
    credits: int
    blessings: List[str]
    curios: List[str]
    equations: List[str]
    hand: List[CardData]
    discard_count: int
    deck_count: int
    player_hp: int
    player_max_hp: int

class PlayCardRequest(BaseModel):
    card_index: int

class PlayCardResponse(BaseModel):
    success: bool
    event_type: str
    event_name: str
    description: str
    options: Optional[List[dict]] = None
    battle_result: Optional[dict] = None