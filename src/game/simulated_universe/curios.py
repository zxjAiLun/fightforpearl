"""模拟宇宙奇物系统"""
from dataclasses import dataclass


@dataclass
class Curio:
    """奇物"""
    id: str
    name: str
    description: str
    # 效果
    atk_pct: float = 0.0
    def_pct: float = 0.0
    hp_pct: float = 0.0
    crit_rate: float = 0.0
    crit_dmg: float = 0.0
    spd_pct: float = 0.0
    energy_recovery_rate: float = 0.0
    dmg_pct: float = 0.0
    # 特殊效果（战斗外）
    credit_bonus: float = 0.0                  # 信用点获得加成
    blessing_quality_bonus: float = 0.0        # 祝福品质加成

    def apply_to(self, character):
        """应用奇物效果到角色"""
        character.stat.atk_pct += self.atk_pct
        character.stat.def_pct += self.def_pct
        character.stat.hp_pct += self.hp_pct
        character.stat.crit_rate += self.crit_rate
        character.stat.crit_dmg += self.crit_dmg
        character.stat.spd_pct += self.spd_pct
        character.stat.energy_recovery_rate += self.energy_recovery_rate
        character.stat.dmg_pct += self.dmg_pct


CURIO_POOL = {
    "curio_lucky_star": Curio(
        id="curio_lucky_star",
        name="幸运星",
        description="所有伤害+5%",
        dmg_pct=0.05,
    ),
    "curio_power_crystal": Curio(
        id="curio_power_crystal",
        name="力量水晶",
        description="攻击力+10%",
        atk_pct=0.10,
    ),
    "curio_ancient_sword": Curio(
        id="curio_ancient_sword",
        name="断者之刃",
        description="暴击率+6%，暴击伤害+12%",
        crit_rate=0.06,
        crit_dmg=0.12,
    ),
    "curio_speed_boots": Curio(
        id="curio_speed_boots",
        name="急速靴",
        description="速度+10%",
        spd_pct=0.10,
    ),
    "curio_treasure_box": Curio(
        id="curio_treasure_box",
        name="宝藏盒",
        description="信用点获得+20%",
        credit_bonus=0.20,
    ),
}
