"""
游戏会话管理器
管理多个并发的游戏实例
"""
from typing import Optional, Dict
from ..game.simulated_universe import SimulatedUniverse, UniverseRun
import uuid

class GameManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.games = {}
        return cls._instance
    
    def create_game(self) -> str:
        game_id = str(uuid.uuid4())[:8]
        su = SimulatedUniverse(difficulty=1)
        run = su.start_new_run()
        # 抽初始手牌
        run.draw_initial_hand()
        self.games[game_id] = {
            "su": su,
            "run": run,
        }
        return game_id
    
    def get_game(self, game_id: str) -> Optional[dict]:
        return self.games.get(game_id)
    
    def get_state(self, game_id: str) -> Optional[GameState]:
        game = self.get_game(game_id)
        if not game:
            return None
        run = game["run"]
        deck = run.card_deck
        return GameState(
            game_id=game_id,
            floor=run.current_floor,
            total_floors=run.map.HEIGHT,
            credits=run.credits,
            blessings=[b.name for b in run.blessings],
            curios=[c.name for c in run.curios],
            equations=[e.name for e in run.active_equations],
            hand=deck.hand,
            discard_count=len(deck.discard_pile),
            deck_count=len(deck.draw_pile),
            player_hp=run.player.current_hp if hasattr(run, 'player') and run.player else 100,
            player_max_hp=run.player.stat.total_max_hp() if hasattr(run, 'player') and run.player else 100,
        )
    
    def play_card(self, game_id: str, card_index: int) -> Optional[dict]:
        game = self.get_game(game_id)
        if not game:
            return None
        run = game["run"]
        result = run.play_card(card_index)
        return result

game_manager = GameManager()