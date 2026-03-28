"""模拟宇宙地图生成器（保留用于参考，实际使用卡牌系统）"""
import random
from dataclasses import dataclass
from typing import List, Optional

from .events import EventType, UniverseEvent


class MapNode:
    """地图节点（保留用于参考）"""
    def __init__(self, x: int, y: int, event: Optional[UniverseEvent] = None):
        self.x = x
        self.y = y
        self.event = event
        self.connections: List[MapNode] = []
        self.visited: bool = False

    def __repr__(self):
        return f"Node({self.x},{self.y}:{self.event.type.value if self.event else 'empty'})"


class UniverseMap:
    """宇宙地图生成器（保留用于参考）"""

    WIDTH = 5
    HEIGHT = 8

    def __init__(self, difficulty: int = 1):
        self.difficulty = difficulty
        self.nodes: List[List[MapNode]] = []
        self.current_node: Optional[MapNode] = None
        self.start_node: Optional[MapNode] = None
        self.end_node: Optional[MapNode] = None
        self._generate_map()

    def _generate_map(self):
        for y in range(self.HEIGHT):
            row = []
            for x in range(self.WIDTH):
                event = self._generate_event_for_position(y)
                node = MapNode(x, y, event)
                row.append(node)
            self.nodes.append(row)

        for y in range(self.HEIGHT - 1):
            for x1 in range(self.WIDTH):
                next_x_options = self._get_next_layer_x(x1)
                for x2 in next_x_options:
                    self.nodes[y][x1].connections.append(self.nodes[y + 1][x2])

        self.start_node = self.nodes[0][self.WIDTH // 2]
        self.end_node = self.nodes[self.HEIGHT - 1][self.WIDTH // 2]
        self.current_node = self.start_node

    def _get_next_layer_x(self, current_x: int) -> List[int]:
        options = []
        for dx in [-1, 0, 1]:
            nx = current_x + dx
            if 0 <= nx < self.WIDTH:
                options.append(nx)
        return options

    def _generate_event_for_position(self, y: int) -> UniverseEvent:
        if y == self.HEIGHT - 1:
            return self._create_boss_event()
        if y == 0:
            return UniverseEvent(
                name="起始区域",
                type=EventType.BLESSING,
                description="选择一份初始祝福",
                blessing_pool=["path_warrior", "path_mage", "path_thunder"],
            )
        roll = random.random()
        if y <= 2:
            if roll < 0.50:
                return self._create_battle_event()
            elif roll < 0.70:
                return self._create_elite_event()
            elif roll < 0.85:
                return self._create_blessing_event()
            elif roll < 0.95:
                return self._create_reward_event()
            else:
                return self._create_curio_event()
        elif y <= 5:
            if roll < 0.30:
                return self._create_battle_event()
            elif roll < 0.50:
                return self._create_elite_event()
            elif roll < 0.70:
                return self._create_blessing_event()
            elif roll < 0.80:
                return self._create_curio_event()
            elif roll < 0.90:
                return self._create_reward_event()
            else:
                return self._create_shop_event()
        else:
            if roll < 0.30:
                return self._create_elite_event()
            elif roll < 0.60:
                return self._create_blessing_event()
            elif roll < 0.75:
                return self._create_curio_event()
            elif roll < 0.90:
                return self._create_reward_event()
            else:
                return self._create_shop_event()

    def _create_battle_event(self) -> UniverseEvent:
        return UniverseEvent(
            name="遭遇战", type=EventType.BATTLE,
            description="前方出现了敌人！",
            enemies=["enemy_beast", "enemy_robot"],
            difficulty=self.difficulty,
        )

    def _create_elite_event(self) -> UniverseEvent:
        return UniverseEvent(
            name="精英战斗", type=EventType.ELITE,
            description="强大的精英敌人！",
            enemies=["enemy_elite_1"],
            difficulty=self.difficulty,
        )

    def _create_boss_event(self) -> UniverseEvent:
        return UniverseEvent(
            name="首领", type=EventType.BOSS,
            description="首领正在等待！",
            enemies=["enemy_boss_1"],
            difficulty=self.difficulty,
        )

    def _create_blessing_event(self) -> UniverseEvent:
        pools = ["path_warrior", "path_mage", "path_thunder",
                 "path_ice", "path_wind", "path_quantum", "path_imaginary", "path_physic", "path_fire"]
        return UniverseEvent(
            name="命运岔路口", type=EventType.BLESSING,
            description="选择一份祝福",
            blessing_pool=random.sample(pools, min(3, len(pools))),
        )

    def _create_curio_event(self) -> UniverseEvent:
        curios = ["curio_lucky_star", "curio_power_crystal", "curio_ancient_sword"]
        return UniverseEvent(
            name="奇异发现", type=EventType.CURIO,
            description="发现了一件奇物！",
            curios_pool=random.sample(curios, min(3, len(curios))),
        )

    def _create_reward_event(self) -> UniverseEvent:
        return UniverseEvent(
            name="意外之财", type=EventType.REWARD,
            description="获得了一些信用点！",
            credit_reward=random.randint(50, 200) * self.difficulty,
        )

    def _create_shop_event(self) -> UniverseEvent:
        return UniverseEvent(
            name="星际商人", type=EventType.SHOP,
            description="商人出售各种物品",
        )

    def get_available_nodes(self) -> List[MapNode]:
        if self.current_node is None:
            return []
        next_nodes = self.current_node.connections
        return [n for n in next_nodes if not n.visited]

    def select_node(self, node: MapNode) -> bool:
        if node in self.get_available_nodes():
            self.current_node = node
            node.visited = True
            return True
        return False
