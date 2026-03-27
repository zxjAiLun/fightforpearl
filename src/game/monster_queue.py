"""
怪物刷新系统 - 敌人队列管理

功能：
1. 维护一个敌人队列
2. HP归零时敌人从队列移除(pop)
3. 新怪物按顺序依次补位加入
4. 支持最多5个前台怪物同时存在
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable, TYPE_CHECKING
from enum import Enum
import logging

if TYPE_CHECKING:
    from src.game.models import Character

logger = logging.getLogger(__name__)


class MonsterRefreshTrigger(Enum):
    """怪物刷新触发类型"""
    ENEMY_DEFEATED = "enemy_defeated"      # 敌人被击败
    WAVE_CLEAR = "wave_clear"              # 波次清理
    ROUND_END = "round_end"                # 回合结束


@dataclass
class MonsterSpawnInfo:
    """怪物生成信息"""
    name: str                    # 怪物名称
    level: int = 50            # 等级
    element: str = "PHYSICAL"   # 属性
    max_hp: float = 10000      # 最大生命值
    atk: float = 1000          # 攻击力
    def_val: float = 500       # 防御力
    spd: float = 90            # 速度
    skills: list = field(default_factory=list)  # 技能列表
    

class MonsterQueue:
    """
    怪物刷新队列管理器
    
    负责：
    1. 管理怪物队列（后台待生成 + 前台战斗中）
    2. 当怪物HP归零时移除并补位
    3. 触发刷新回调
    """
    
    def __init__(
        self,
        max_front: int = 5,
        wave: int = 1,
        on_spawn_callback: Optional[Callable] = None,
        on_defeat_callback: Optional[Callable] = None,
    ):
        self._queue: list[MonsterSpawnInfo] = []
        self._front: list["Character"] = []
        self._defeated: list["Character"] = []
        self._max_front = max_front
        self._wave = wave
        self._on_spawn = on_spawn_callback
        self._on_defeat = on_defeat_callback
        self._spawn_count = 0
    
    @property
    def front_monsters(self) -> list["Character"]:
        return self._front.copy()
    
    @property
    def queue_monsters(self) -> list[MonsterSpawnInfo]:
        return self._queue.copy()
    
    @property
    def defeated_monsters(self) -> list["Character"]:
        return self._defeated.copy()
    
    @property
    def wave(self) -> int:
        return self._wave
    
    @property
    def is_empty(self) -> bool:
        return len(self._front) == 0 and len(self._queue) == 0
    
    def load_queue(self, monsters: list[MonsterSpawnInfo]) -> None:
        self._queue = monsters.copy()
        logger.info(f"Loaded {len(monsters)} monsters into queue")
    
    def spawn_initial(self, factory: Callable) -> list["Character"]:
        spawned = []
        while len(self._front) < self._max_front and self._queue:
            info = self._queue.pop(0)
            char = factory(info)
            char._monster_queue_ref = self
            self._front.append(char)
            spawned.append(char)
            self._spawn_count += 1
            logger.info(f"Spawned {info.name} (wave {self._wave}, front: {len(self._front)})")
            
            if self._on_spawn:
                self._on_spawn(char)
        
        return spawned
    
    def check_defeated_and_replace(self, defeated: "Character", factory: Optional[Callable] = None) -> bool:
        defeated_id = id(defeated)
        found = None
        for char in self._front:
            if id(char) == defeated_id:
                found = char
                break
        
        if found is None:
            return False
        
        self._front.remove(found)
        self._defeated.append(found)
        
        logger.info(f"Monster {found.name} defeated. Front now has {len(self._front)} monsters")
        
        if self._on_defeat:
            self._on_defeat(found)
        
        if factory:
            spawned = self.fill_front(factory)
            return len(spawned) > 0
        return False
    
    def fill_front(self, factory: Callable) -> list["Character"]:
        spawned = []
        while len(self._front) < self._max_front and self._queue:
            info = self._queue.pop(0)
            char = factory(info)
            char._monster_queue_ref = self
            self._front.append(char)
            spawned.append(char)
            logger.info(f"Filled front with {info.name}")
            
            if self._on_spawn:
                self._on_spawn(char)
        
        return spawned
    
    def check_wave_clear(self) -> bool:
        return len(self._front) == 0 and len(self._queue) == 0
    
    def advance_wave(self) -> None:
        self._wave += 1
        logger.info(f"Advanced to wave {self._wave}")
    
    def remaining_count(self) -> int:
        return len(self._front) + len(self._queue)
    
    def __len__(self) -> int:
        return self.remaining_count()
    
    def __repr__(self) -> str:
        return f"MonsterQueue(front={len(self._front)}, queue={len(self._queue)}, wave={self._wave})"


class WaveManager:
    """波次管理器 - 管理多波次战斗"""
    
    def __init__(self, wave_configs: list[list[MonsterSpawnInfo]]):
        self._configs = wave_configs
        self._current_wave = 0
        self._monster_queue: Optional[MonsterQueue] = None
        self._factory: Optional[Callable] = None
        self._callbacks = {
            'on_wave_start': [],
            'on_wave_clear': [],
            'on_battle_end': [],
        }
    
    @property
    def current_wave(self) -> int:
        return self._current_wave
    
    @property
    def total_waves(self) -> int:
        return len(self._configs)
    
    @property
    def monster_queue(self) -> Optional[MonsterQueue]:
        return self._monster_queue
    
    def register_callback(self, event: str, callback: Callable) -> None:
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def start_wave(self, factory: Callable) -> Optional[MonsterQueue]:
        """开始第一波（重置状态）"""
        self._current_wave = 0
        self._factory = factory
        return self._start_wave_internal()
    
    def start_next_wave(self, factory: Callable) -> Optional[MonsterQueue]:
        """开始下一波"""
        self._factory = factory
        return self._start_wave_internal()
    
    def _start_wave_internal(self) -> Optional[MonsterQueue]:
        """内部方法：开始下一波"""
        self._current_wave += 1
        
        if self._current_wave > len(self._configs):
            logger.warning(f"No more waves available. Current: {self._current_wave}")
            return self._monster_queue
        
        wave_config = self._configs[self._current_wave - 1]
        
        current_factory = self._factory
        self._monster_queue = MonsterQueue(
            max_front=5,
            wave=self._current_wave,
            on_spawn_callback=lambda c: self._trigger('on_wave_start', c),
            on_defeat_callback=lambda c: self._handle_defeat(current_factory, c),
        )
        
        self._monster_queue.load_queue(wave_config)
        self._monster_queue.spawn_initial(current_factory)
        
        logger.info(f"Wave {self._current_wave} started with {len(wave_config)} monsters")
        
        return self._monster_queue
    
    def _handle_defeat(self, factory: Callable, defeated) -> None:
        if self._monster_queue:
            self._monster_queue.check_defeated_and_replace(defeated, factory)
        self._trigger('on_wave_clear', defeated)
    
    def _trigger(self, event: str, *args) -> None:
        for cb in self._callbacks.get(event, []):
            try:
                cb(*args)
            except Exception as e:
                logger.error(f"Callback error in {event}: {e}")


def create_enemy_from_spawn_info(info: MonsterSpawnInfo) -> "Character":
    """从MonsterSpawnInfo创建敌人Character的工厂函数"""
    from src.game.models import Character, Element, Stat
    from src.game.character import create_character_from_preset
    
    char_name = info.name
    try:
        char = create_character_from_preset(char_name)
        char.current_hp = info.max_hp
        return char
    except:
        pass
    
    element = Element[info.element] if info.element in Element._member_names_ else Element.PHYSICAL
    
    char = Character(
        name=info.name,
        level=info.level,
        element=element,
        stat=Stat(
            base_max_hp=info.max_hp,
            base_atk=info.atk,
            base_def=info.def_val,
            base_spd=info.spd,
        ),
        skills=[],
        passives=[],
        is_enemy=True,
    )
    char.current_hp = info.max_hp
    
    return char
