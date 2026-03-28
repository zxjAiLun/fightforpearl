"""模拟宇宙核心类"""
import random

from .run import UniverseRun
from .cards import CardDeck, CardType, UniverseCard
from .events import EventType
from .blessings import Blessing, get_random_blessings
from .curios import CURIO_POOL


class SimulatedUniverse:
    """模拟宇宙主类"""

    def __init__(self, difficulty: int = 1):
        self.difficulty = difficulty
        self.current_run: UniverseRun | None = None

    def start_new_run(self) -> UniverseRun:
        """开始新的运行"""
        self.current_run = UniverseRun()
        self.current_run.init_deck(difficulty=self.difficulty)
        return self.current_run

    def get_current_state(self) -> dict:
        """获取当前状态"""
        if not self.current_run:
            return {}

        run = self.current_run
        deck_status = run.card_deck.get_deck_status()
        return {
            "floor": run.current_floor,
            "total_floors": run.total_floors,
            "credits": run.credits,
            "blessings": [b.name for b in run.blessings],
            "curios": [c.name for c in run.curios],
            "equations": [e.name for e in run.active_equations],
            "is_complete": run.is_complete,
            "is_failed": run.is_failed,
            "map_progress": f"{run.current_floor}/{run.total_floors}",
            "deck_status": deck_status,
        }

    def draw_hand(self) -> dict:
        """抽3张手牌"""
        if not self.current_run:
            return {"error": "No active run"}

        run = self.current_run
        cards = run.draw_hand(3)

        if not cards:
            return {"error": "No cards to draw"}

        return {
            "cards": run.card_deck.get_hand_info(),
            "deck_status": run.card_deck.get_deck_status(),
        }

    def get_hand(self) -> dict:
        """获取当前手牌信息"""
        if not self.current_run:
            return {"error": "No active run"}

        run = self.current_run
        return {
            "cards": run.card_deck.get_hand_info(),
            "deck_status": run.card_deck.get_deck_status(),
        }

    def play_card(self, card_index: int) -> dict:
        """打出第index张手牌"""
        if not self.current_run:
            return {"error": "No active run"}

        run = self.current_run
        card = run.play_card(card_index)

        if not card:
            return {"error": "Invalid card index"}

        event = card.to_event()
        run.advance_floor()

        result = {
            "card_played": card.name,
            "card_type": card.card_type.value,
            "event": event.name,
            "type": event.type.value,
            "description": event.description,
        }

        if event.type == EventType.BATTLE:
            result["action"] = "battle"
            result["enemies"] = event.enemies
        elif event.type == EventType.ELITE:
            result["action"] = "battle"
            result["enemies"] = event.enemies
            result["note"] = "精英战斗，难度较高"
        elif event.type == EventType.BOSS:
            result["action"] = "boss_battle"
            result["enemies"] = event.enemies
        elif event.type == EventType.BLESSING:
            result["action"] = "choose_blessing"
            blessings = get_random_blessings(3)
            result["options"] = [
                {
                    "index": i,
                    "name": b.name,
                    "description": b.description,
                    "path": b.path.value,
                }
                for i, b in enumerate(blessings)
            ]
            self._pending_blessings = blessings
        elif event.type == EventType.CURIO:
            result["action"] = "choose_curio"
            curios = list(CURIO_POOL.values())[:3]
            result["options"] = [
                {
                    "index": i,
                    "name": c.name,
                    "description": c.description,
                }
                for i, c in enumerate(curios)
            ]
            self._pending_curios = curios
        elif event.type == EventType.REWARD:
            result["action"] = "reward"
            result["credits"] = event.credit_reward
            run.add_credits(event.credit_reward)
        elif event.type == EventType.SHOP:
            result["action"] = "shop"
        elif event.type == EventType.MYSTERY:
            result["action"] = "mystery"
            roll = random.random()
            if roll < 0.3:
                run.add_credits(100)
                result["result"] = "获得100信用点"
            elif roll < 0.6:
                blessings = get_random_blessings(1)
                run.add_blessing(blessings[0])
                result["result"] = f"获得祝福：{blessings[0].name}"
            else:
                result["result"] = "无事发生"
        elif event.type == EventType.REST:
            result["action"] = "rest"
            result["heal"] = "恢复30%最大HP"

        return result

    def choose_blessing(self, index: int) -> dict:
        """选择祝福"""
        if not hasattr(self, "_pending_blessings"):
            return {"error": "No blessing to choose"}

        blessings = self._pending_blessings
        if not (0 <= index < len(blessings)):
            return {"error": "Invalid blessing index"}

        blessing = blessings[index]
        self.current_run.add_blessing(blessing)

        new_equations = self.current_run.check_and_activate_equations()

        result = {
            "chosen": blessing.name,
            "description": blessing.description,
        }

        if new_equations:
            result["new_equations"] = [e.name for e in new_equations]

        del self._pending_blessings
        return result

    def choose_curio(self, index: int) -> dict:
        """选择奇物"""
        if not hasattr(self, "_pending_curios"):
            return {"error": "No curio to choose"}

        curios = self._pending_curios
        if not (0 <= index < len(curios)):
            return {"error": "Invalid curio index"}

        curio = curios[index]
        self.current_run.add_curio(curio)
        result = {
            "chosen": curio.name,
            "description": curio.description,
        }

        del self._pending_curios
        return result

    def complete_battle(self, victory: bool):
        """完成战斗"""
        if not self.current_run:
            return

        if not victory:
            self.current_run.is_failed = True

    def complete_run(self, victory: bool):
        """完成运行"""
        if self.current_run:
            self.current_run.is_complete = True
            if not victory:
                self.current_run.is_failed = True
            self.current_run.final_floor = self.current_run.current_floor
