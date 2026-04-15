"""模拟宇宙单次运行状态"""
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from .cards import CardDeck, CardType, UniverseCard
from .events import UniverseEvent
from .blessings import Blessing, PathType
from .curios import Curio
from .equations import Equation, get_available_equations

if TYPE_CHECKING:
    from . import DifficultyLevel


@dataclass
class UniverseRun:
    """模拟宇宙单次运行"""
    # 难度
    difficulty_level: "DifficultyLevel" = None  # type: ignore[assignment]
    # 进度
    current_floor: int = 1
    total_floors: int = 8  # 总层数

    # 卡牌系统
    card_deck: Optional[CardDeck] = None

    # 资源
    credits: int = 0  # 信用点

    # 祝福
    blessings: List[Blessing] = field(default_factory=list)
    active_blessing_ids: List[str] = field(default_factory=list)

    # 奇物
    curios: List[Curio] = field(default_factory=list)

    # 方程
    active_equations: List[Equation] = field(default_factory=list)

    # 状态
    is_complete: bool = False
    is_failed: bool = False
    final_floor: int = 0

    # 当前打出的卡牌
    current_card: Optional[UniverseCard] = None

    def init_deck(self, difficulty: int = 1, difficulty_level = None):
        """初始化卡牌堆"""
        self.card_deck = CardDeck(difficulty=difficulty)
        if difficulty_level is not None:
            self.difficulty_level = difficulty_level
            self.total_floors = difficulty_level.total_floors

    def draw_hand(self, count: int = 3) -> List[UniverseCard]:
        """抽 count 张手牌"""
        return self.card_deck.draw_cards(count)

    def play_card(self, card_index: int) -> Optional[UniverseCard]:
        """打出第 index 张手牌"""
        hand = self.card_deck.hand
        if 0 <= card_index < len(hand):
            card = hand[card_index]
            played = self.card_deck.play_card(card)
            if played:
                self.current_card = played
            return played
        return None

    def discard_current_hand(self):
        """弃掉当前手牌"""
        self.card_deck.discard_hand()

    def add_blessing(self, blessing: Blessing):
        """添加祝福"""
        self.blessings.append(blessing)
        self.active_blessing_ids.append(blessing.id)

    def add_curio(self, curio: Curio):
        """添加奇物"""
        self.curios.append(curio)

    def add_credits(self, amount: int):
        """添加信用点（考虑奇物加成）"""
        bonus = 1.0
        for c in self.curios:
            bonus += c.credit_bonus
        self.credits += int(amount * bonus)

    def get_blessing_counts(self) -> dict:
        """统计各命途祝福数量"""
        counts = {}
        for b in self.blessings:
            counts[b.path] = counts.get(b.path, 0) + 1
        return counts

    def check_and_activate_equations(self) -> List[Equation]:
        """检查并激活满足条件的方程"""
        blessing_counts = self.get_blessing_counts()
        available = get_available_equations(blessing_counts)

        newly_activated = []
        for eq in available:
            if eq not in self.active_equations:
                self.active_equations.append(eq)
                newly_activated.append(eq)

        return newly_activated

    def apply_all_buffs_to_character(self, character):
        """将所有祝福/奇物/方程效果应用到角色"""
        for b in self.blessings:
            b.apply_to(character)
        for c in self.curios:
            c.apply_to(character)
        for e in self.active_equations:
            e.apply_to(character)

    def advance_floor(self):
        """进入下一层"""
        self.current_floor += 1
        self.current_card = None
        # 到达Boss层后，重置卡池（Boss只能打一次）
        if self.current_floor == self.total_floors:
            # 提前洗牌确保Boss卡可以再被抽到
            self.card_deck.reshuffle_discard()
            self.card_deck.boss_card_used = False

    def is_boss_floor(self) -> bool:
        """是否Boss层"""
        return self.current_floor == self.total_floors

    def get_current_event(self) -> Optional[UniverseEvent]:
        """获取当前卡牌对应的事件"""
        if self.current_card:
            return self.current_card.to_event()
        return None
