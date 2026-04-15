"""模拟宇宙卡牌系统（差分宇宙核心抽卡机制）"""
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .events import EventType


class CardType(Enum):
    """卡牌类型"""
    BATTLE = "battle"           # 普通战斗
    ELITE = "elite"            # 精英战斗
    BOSS = "boss"              # Boss战
    BLESSING = "blessing"      # 祝福选择
    CURIO = "curio"            # 奇物发现
    SHOP = "shop"              # 商店
    REST = "rest"              # 休息（回血）
    REWARD = "reward"          # 直接奖励
    MYSTERY = "mystery"        # 随机事件


@dataclass
class UniverseCard:
    """宇宙事件卡牌"""
    id: str
    name: str
    card_type: CardType
    description: str
    # 稀有度：1=普通, 2=稀有, 3=史诗
    rarity: int = 1
    # 战斗配置
    enemies: List[str] = field(default_factory=list)
    # 奖励配置
    credit_reward: int = 0
    blessing_pool: List[str] = field(default_factory=list)
    curios_pool: List[str] = field(default_factory=list)
    # 难度
    difficulty: int = 1

    def to_event(self) -> "UniverseEvent":
        """将卡牌转换为事件"""
        from .events import UniverseEvent
        return UniverseEvent(
            name=self.name,
            type=self._card_type_to_event_type(),
            description=self.description,
            enemies=self.enemies.copy() if self.enemies else [],
            credit_reward=self.credit_reward,
            blessing_pool=self.blessing_pool.copy() if self.blessing_pool else [],
            curios_pool=self.curios_pool.copy() if self.curios_pool else [],
            difficulty=self.difficulty,
        )

    def _card_type_to_event_type(self) -> EventType:
        """卡牌类型转换为事件类型"""
        mapping = {
            CardType.BATTLE: EventType.BATTLE,
            CardType.ELITE: EventType.ELITE,
            CardType.BOSS: EventType.BOSS,
            CardType.BLESSING: EventType.BLESSING,
            CardType.CURIO: EventType.CURIO,
            CardType.SHOP: EventType.SHOP,
            CardType.REST: EventType.REST,
            CardType.REWARD: EventType.REWARD,
            CardType.MYSTERY: EventType.MYSTERY,
        }
        return mapping.get(self.card_type, EventType.BATTLE)


# 初始卡池配置
INITIAL_CARD_POOL = {
    CardType.BATTLE: 8,     # 普通战斗
    CardType.ELITE: 3,      # 精英战斗
    CardType.BOSS: 1,       # Boss战（每局只有1张）
    CardType.BLESSING: 6,   # 祝福选择
    CardType.CURIO: 4,      # 奇物发现
    CardType.SHOP: 2,       # 商店
    CardType.REST: 3,       # 休息（回血）
    CardType.REWARD: 5,     # 直接奖励
    CardType.MYSTERY: 4,    # 随机事件
}

# 卡池权重（稀有度影响抽卡权重）
RARITY_WEIGHTS = {
    1: 10,  # 普通
    2: 5,   # 稀有
    3: 2,   # 史诗
}


class CardDeck:
    """卡牌堆叠管理器"""

    def __init__(self, difficulty: int = 1):
        self.difficulty = difficulty
        self.draw_pile: List[UniverseCard] = []      # 抽牌堆
        self.discard_pile: List[UniverseCard] = []   # 弃牌堆
        self.hand: List[UniverseCard] = []           # 手牌
        self.total_drawn: int = 0                    # 总抽卡数
        self.boss_card_used: bool = False             # Boss卡是否已使用
        self._build_deck()

    def _build_deck(self):
        """构建初始卡池"""
        self.draw_pile.clear()
        self.discard_pile.clear()
        self.hand.clear()
        self.boss_card_used = False

        pools = [
            "path_warrior", "path_mage", "path_thunder",
            "path_ice", "path_wind", "path_quantum", "path_imaginary",
            "path_physic", "path_fire",
        ]
        curios = ["curio_lucky_star", "curio_power_crystal", "curio_ancient_sword"]

        for card_type, count in INITIAL_CARD_POOL.items():
            for i in range(count):
                card = self._create_card(card_type, i, pools, curios)
                self.draw_pile.append(card)

        random.shuffle(self.draw_pile)

    def _create_card(
        self,
        card_type: CardType,
        index: int,
        pools: List[str],
        curios: List[str],
    ) -> UniverseCard:
        """根据类型创建卡牌"""
        cid = f"{card_type.value}_{index}"

        if card_type == CardType.BATTLE:
            return UniverseCard(
                id=cid,
                name="遭遇战",
                card_type=card_type,
                description=f"前方出现了敌人！（敌人强化+{(self.difficulty - 1) * 20}%）",
                enemies=["enemy_beast", "enemy_robot"],
                rarity=1,
                difficulty=self.difficulty,
            )
        elif card_type == CardType.ELITE:
            return UniverseCard(
                id=cid,
                name="精英战斗",
                card_type=card_type,
                description=f"强大的精英敌人！（敌人强化+{(self.difficulty - 1) * 20}%）",
                enemies=["enemy_elite_1"],
                rarity=2,
                difficulty=self.difficulty,
            )
        elif card_type == CardType.BOSS:
            return UniverseCard(
                id=cid,
                name="首领",
                card_type=card_type,
                description=f"首领正在等待！（敌人强化+{(self.difficulty - 1) * 20}%）",
                enemies=["enemy_boss_1"],
                rarity=3,
                difficulty=self.difficulty,
            )
        elif card_type == CardType.BLESSING:
            return UniverseCard(
                id=cid,
                name="命运岔路口",
                card_type=card_type,
                description="选择一份祝福",
                blessing_pool=random.sample(pools, min(3, len(pools))),
                rarity=2,
            )
        elif card_type == CardType.CURIO:
            return UniverseCard(
                id=cid,
                name="奇异发现",
                card_type=card_type,
                description="发现了一件奇物！",
                curios_pool=random.sample(curios, min(3, len(curios))),
                rarity=2,
            )
        elif card_type == CardType.SHOP:
            return UniverseCard(
                id=cid,
                name="星际商人",
                card_type=card_type,
                description="商人出售各种物品",
                rarity=2,
            )
        elif card_type == CardType.REST:
            return UniverseCard(
                id=cid,
                name="休息站点",
                card_type=card_type,
                description="恢复30%最大HP",
                rarity=1,
            )
        elif card_type == CardType.REWARD:
            return UniverseCard(
                id=cid,
                name="意外之财",
                card_type=card_type,
                description="获得了一些信用点！",
                credit_reward=random.randint(50, 200) * self.difficulty,
                rarity=1,
            )
        elif card_type == CardType.MYSTERY:
            return UniverseCard(
                id=cid,
                name="随机事件",
                card_type=card_type,
                description="命运的馈赠...",
                rarity=1,
            )
        else:
            return UniverseCard(
                id=cid,
                name="未知事件",
                card_type=card_type,
                description="？？？",
                rarity=1,
            )

    def draw_cards(self, count: int) -> List[UniverseCard]:
        """抽 count 张牌"""
        drawn = []
        for _ in range(count):
            card = self._draw_single()
            if card:
                drawn.append(card)
        self.hand.extend(drawn)
        self.total_drawn += len(drawn)
        return drawn

    def _draw_single(self) -> Optional[UniverseCard]:
        """抽一张牌"""
        # 如果抽牌堆为空，洗混弃牌堆
        if not self.draw_pile:
            if not self.discard_pile:
                return None
            self.draw_pile = self.discard_pile.copy()
            random.shuffle(self.draw_pile)
            self.discard_pile.clear()

        # 如果抽牌堆只剩下已使用的Boss卡，洗牌
        if len(self.draw_pile) == 1:
            top_card = self.draw_pile[0]
            if top_card.card_type == CardType.BOSS and self.boss_card_used:
                # 只有Boss卡且已使用，需要洗牌
                if not self.discard_pile:
                    return None  # 没有其他卡可抽
                self.draw_pile = self.discard_pile.copy()
                random.shuffle(self.draw_pile)
                self.discard_pile.clear()

        if not self.draw_pile:
            return None

        # Boss卡只能抽一次
        card = self.draw_pile.pop()
        if card.card_type == CardType.BOSS and self.boss_card_used:
            # Boss卡已使用，尝试继续抽
            if self.draw_pile:
                return self._draw_single()
            elif self.discard_pile:
                self.draw_pile = self.discard_pile.copy()
                random.shuffle(self.draw_pile)
                self.discard_pile.clear()
                return self._draw_single()
            else:
                return None

        if card.card_type == CardType.BOSS:
            self.boss_card_used = True

        return card

    def play_card(self, card: UniverseCard) -> Optional[UniverseCard]:
        """打出卡牌，选中的保留，其余进入弃牌堆"""
        if card not in self.hand:
            return None

        self.hand.remove(card)
        # 剩余手牌全部弃掉
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        return card

    def discard_hand(self):
        """弃掉所有手牌"""
        self.discard_pile.extend(self.hand)
        self.hand.clear()

    def reshuffle_discard(self):
        """洗牌：弃牌堆混入抽牌堆"""
        self.draw_pile.extend(self.discard_pile)
        random.shuffle(self.draw_pile)
        self.discard_pile.clear()

    def get_deck_status(self) -> dict:
        """获取牌堆状态"""
        return {
            "draw_pile": len(self.draw_pile),
            "discard_pile": len(self.discard_pile),
            "hand": len(self.hand),
            "total_cards": len(self.draw_pile) + len(self.discard_pile) + len(self.hand),
        }

    def get_hand_info(self) -> List[dict]:
        """获取手牌信息"""
        return [
            {
                "index": i,
                "id": card.id,
                "name": card.name,
                "type": card.card_type.value,
                "description": card.description,
                "rarity": card.rarity,
            }
            for i, card in enumerate(self.hand)
        ]
