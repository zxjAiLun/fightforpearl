"""模拟宇宙祝福系统"""
from dataclasses import dataclass
from enum import Enum
import random


class PathType(Enum):
    WARRIOR = "warrior"       # 战士命途
    MAGE = "mage"             # 法师命途
    THUNDER = "thunder"       # 雷命途
    ICE = "ice"               # 冰命途
    WIND = "wind"             # 风命途
    FIRE = "fire"             # 火命途
    PHYSIC = "physic"         # 物理命途
    QUANTUM = "quantum"       # 量子命途
    IMAGINARY = "imaginary"    # 虚数命途


@dataclass
class Blessing:
    """祝福"""
    id: str
    name: str
    path: PathType
    description: str
    # 效果：战斗属性加成
    atk_pct: float = 0.0
    def_pct: float = 0.0
    hp_pct: float = 0.0
    crit_rate: float = 0.0
    crit_dmg: float = 0.0
    spd_pct: float = 0.0
    energy_recovery_rate: float = 0.0
    elemental_dmg_pct: float = 0.0  # 某元素伤害加成
    break_efficiency: float = 0.0

    def apply_to(self, character):
        """应用祝福效果到角色"""
        character.stat.atk_pct += self.atk_pct
        character.stat.def_pct += self.def_pct
        character.stat.hp_pct += self.hp_pct
        character.stat.crit_rate += self.crit_rate
        character.stat.crit_dmg += self.crit_dmg
        character.stat.spd_pct += self.spd_pct
        character.stat.energy_recovery_rate += self.energy_recovery_rate
        character.stat.dmg_pct += self.elemental_dmg_pct
        character.stat.break_efficiency += self.break_efficiency


BLESSING_POOL = {
    # 战士命途
    "path_warrior": Blessing(
        id="path_warrior",
        name="战士之道",
        path=PathType.WARRIOR,
        description="攻击力+12%",
        atk_pct=0.12,
    ),
    "path_warrior_2": Blessing(
        id="path_warrior_2",
        name="不屈",
        path=PathType.WARRIOR,
        description="HP上限+10%",
        hp_pct=0.10,
    ),
    # 法师命途
    "path_mage": Blessing(
        id="path_mage",
        name="智识之道",
        path=PathType.MAGE,
        description="暴击率+8%",
        crit_rate=0.08,
    ),
    "path_mage_2": Blessing(
        id="path_mage_2",
        name="秘法",
        path=PathType.MAGE,
        description="暴击伤害+16%",
        crit_dmg=0.16,
    ),
    # 雷命途
    "path_thunder": Blessing(
        id="path_thunder",
        name="雷鸣之道",
        path=PathType.THUNDER,
        description="雷元素伤害+15%",
        elemental_dmg_pct=0.15,
    ),
    "path_thunder_2": Blessing(
        id="path_thunder_2",
        name="放电",
        path=PathType.THUNDER,
        description="击破效率+20%",
        break_efficiency=0.20,
    ),
    # 冰命途
    "path_ice": Blessing(
        id="path_ice",
        name="寒冰之道",
        path=PathType.ICE,
        description="冰元素伤害+15%",
        elemental_dmg_pct=0.15,
    ),
    # 风命途
    "path_wind": Blessing(
        id="path_wind",
        name="风息之道",
        path=PathType.WIND,
        description="速度+8%",
        spd_pct=0.08,
    ),
    # 火命途
    "path_fire": Blessing(
        id="path_fire",
        name="烈焰之道",
        path=PathType.FIRE,
        description="火元素伤害+15%",
        elemental_dmg_pct=0.15,
    ),
    # 物理命途
    "path_physic": Blessing(
        id="path_physic",
        name="毁灭之道",
        path=PathType.PHYSIC,
        description="物理伤害+15%",
        elemental_dmg_pct=0.15,
    ),
    # 量子命途
    "path_quantum": Blessing(
        id="path_quantum",
        name="繁育之道",
        path=PathType.QUANTUM,
        description="量子伤害+15%",
        elemental_dmg_pct=0.15,
    ),
    # 虚数命途
    "path_imaginary": Blessing(
        id="path_imaginary",
        name="虚无之道",
        path=PathType.IMAGINARY,
        description="虚数伤害+15%",
        elemental_dmg_pct=0.15,
    ),
}


def get_random_blessings(count: int = 3) -> list[Blessing]:
    """获取随机祝福列表"""
    all_blessings = list(BLESSING_POOL.values())
    return random.sample(all_blessings, min(count, len(all_blessings)))
