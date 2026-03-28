from fastapi import APIRouter, HTTPException
from ..models import GameState, PlayCardRequest, PlayCardResponse
from ..game_manager import game_manager

router = APIRouter(prefix="/api/game", tags=["game"])

@router.post("/start")
def start_game():
    game_id = game_manager.create_game()
    state = game_manager.get_state(game_id)
    return {"game_id": game_id, "state": state}

@router.get("/{game_id}")
def get_state(game_id: str):
    state = game_manager.get_state(game_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")
    return state

@router.post("/{game_id}/play")
def play_card(game_id: str, req: PlayCardRequest):
    result = game_manager.play_card(game_id, req.card_index)
    if not result:
        raise HTTPException(status_code=404, detail="Game not found")
    return result

@router.post("/{game_id}/choose-blessing")
def choose_blessing(game_id: str, index: int):
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    result = game["run"].choose_blessing(index)
    return result

@router.post("/{game_id}/choose-curio")
def choose_curio(game_id: str, index: int):
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    result = game["run"].choose_curio(index)
    return result