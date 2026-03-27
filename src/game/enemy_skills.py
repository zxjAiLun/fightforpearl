"""
敌人技能模块 - 崩坏星穹铁道风格敌人技能定义

包含各类敌人/怪物的技能设计：
- 精英敌人（银鬃铁卫、凝滞沙影等）
-首领敌人（末日兽、布洛妮娅等）
- 普通敌人（机械士兵、异形生物等）

技能结构：
- skill_id: 技能唯一标识
- name: 技能名称
- type: BASIC/SPECIAL/ULT/TALENT/FOLLOW_UP
- multiplier: 伤害倍率
- damage_type: 元素属性
- break_power: 击破能力
- target_count: 目标数量（-1=全体）
- description: 技能描述
- effects: 附加效果描述
"""

from src.game.models import Skill, SkillType, Element, Passive, BreakEffectType


# ============================================================
# 技能ID常量 - 用于enemies.json引用
# ============================================================

# 银鬃铁卫技能组
SILVERMANE_BASIC = "silvermane_basic"
SILVERMANE_SPECIAL = "silvermane_special"
SILVERMANE_ULT = "silvermane_ult"
SILVERMANE_TALENT = "silvermane_talent"

# 凝滞沙影技能组
SANDWORM_BASIC = "sandworm_basic"
SANDWORM_SPECIAL = "sandworm_special"
SANDWORM_ULT = "sandworm_ult"

# 末日兽技能组
DOOMSDAY_BASIC = "doomsday_basic"
DOOMSDAY_SPECIAL = "doomsday_special"
DOOMSDAY_ULT = "doomsday_ult"
DOOMSDAY_TALENT = "doomsday_talent"

# 布洛妮娅技能组
BRONYA_ENEMY_BASIC = "bronya_enemy_basic"
BRONYA_ENEMY_SPECIAL = "bronya_enemy_special"
BRONYA_ENEMY_ULT = "bronya_enemy_ult"

# 银狼技能组
SILVERWOLF_BASIC = "silverwolf_basic"
SILVERWOLF_SPECIAL = "silverwolf_special"
SILVERWOLF_ULT = "silverwolf_ult"

# 史瓦罗技能组
SWARLER_BASIC = "swarler_basic"
SWARLER_SPECIAL = "swarler_special"
SWARLER_ULT = "swarler_ult"

# 可可利亚技能组
COCONIA_BASIC = "coconia_basic"
COCONIA_SPECIAL = "coconia_special"
COCONIA_ULT = "coconia_ult"
COCONIA_TALENT = "coconia_talent"

# 机械士兵技能组
MECH_SOLDIER_BASIC = "mech_soldier_basic"
MECH_SOLDIER_SPECIAL = "mech_soldier_special"

# 异形猎手技能组
ALIEN_HUNTER_BASIC = "alien_hunter_basic"
ALIEN_HUNTER_SPECIAL = "alien_hunter_special"
ALIEN_HUNTER_TALENT = "alien_hunter_talent"

# 焚烬者技能组
INFERNO_BASIC = "inferno_basic"
INFERNO_SPECIAL = "inferno_special"
INFERNO_ULT = "inferno_ult"

# 霜饥者技能组
FROST_BASIC = "frost_basic"
FROST_SPECIAL = "frost_special"
FROST_ULT = "frost_ult"

# ============================================================
# 技能注册表 - skill_id -> Skill对象
# ============================================================

_ENEMY_SKILLS: dict[str, Skill] = {}

# -----------------------
# 银鬃铁卫 (Silvermane Guard)
# 定位：物理/量子属性精英，防御型战士
# 特点：高防御、护盾、反击
# -----------------------
def _register_silvermane():
    _ENEMY_SKILLS[SILVERMANE_BASIC] = Skill(
        name="银鬃斩击",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.PHYSICAL,
        description="对单体造成50%攻击力的物理伤害",
        energy_gain=10.0,
        break_power=30,
        target_count=1,
    )
    _ENEMY_SKILLS[SILVERMANE_SPECIAL] = Skill(
        name="坚盾冲击",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.80,
        damage_type=Element.PHYSICAL,
        description="对单体造成80%攻击力的物理伤害，附加【护盾】效果",
        energy_gain=15.0,
        break_power=40,
        target_count=1,
    )
    _ENEMY_SKILLS[SILVERMANE_ULT] = Skill(
        name="银鬃风暴",
        type=SkillType.ULT,
        multiplier=0.60,
        damage_type=Element.QUANTUM,
        description="对敌方全体造成60%×3次量子属性伤害，每次命中有概率附加【纠缠】",
        energy_gain=0.0,
        break_power=30,
        target_count=-1,
        aoe_multiplier=0.8,
    )
    _ENEMY_SKILLS[SILVERMANE_TALENT] = Skill(
        name="铁卫之魂",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.PHYSICAL,
        description="生命值低于50%时，攻击力提升20%，暴击率提升10%",
        energy_gain=0.0,
        break_power=0,
    )

# -----------------------
# 凝滞沙影 (Sand Worm / Stagnant Shadow)
# 定位：虚数属性首领，群体控制
# 特点：AOE攻击、禁锢减速
# -----------------------
def _register_sandworm():
    _ENEMY_SKILLS[SANDWORM_BASIC] = Skill(
        name="沙影撕咬",
        type=SkillType.BASIC,
        multiplier=0.55,
        damage_type=Element.IMAGINARY,
        description="对单体造成55%攻击力的虚数属性伤害",
        energy_gain=10.0,
        break_power=20,
        target_count=1,
    )
    _ENEMY_SKILLS[SANDWORM_SPECIAL] = Skill(
        name="流沙吞噬",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.70,
        damage_type=Element.IMAGINARY,
        description="对敌方全体造成70%攻击力的虚数属性伤害，30%概率附加【禁锢】",
        energy_gain=15.0,
        break_power=30,
        target_count=-1,
        aoe_multiplier=0.6,
    )
    _ENEMY_SKILLS[SANDWORM_ULT] = Skill(
        name="末日沉沙",
        type=SkillType.ULT,
        multiplier=1.20,
        damage_type=Element.IMAGINARY,
        description="对敌方全体造成120%攻击力的虚数属性伤害，50%概率附加【禁锢】+行动延后30%",
        energy_gain=0.0,
        break_power=50,
        target_count=-1,
        aoe_multiplier=0.8,
    )

# -----------------------
# 末日兽 (Doomsday Beast)
# 定位：雷/冰属性首领，高爆发AOE
# 特点：多段AOE、弱点攻击
# -----------------------
def _register_doomsday():
    _ENEMY_SKILLS[DOOMSDAY_BASIC] = Skill(
        name="末日之爪",
        type=SkillType.BASIC,
        multiplier=0.60,
        damage_type=Element.THUNDER,
        description="对单体造成60%攻击力的雷属性伤害",
        energy_gain=10.0,
        break_power=25,
        target_count=1,
    )
    _ENEMY_SKILLS[DOOMSDAY_SPECIAL] = Skill(
        name="雷霆之怒",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.45,
        damage_type=Element.THUNDER,
        description="对敌方全体造成45%×3次雷属性伤害，每次命中附加【触电】DOT",
        energy_gain=20.0,
        break_power=20,
        target_count=-1,
        aoe_multiplier=0.8,
    )
    _ENEMY_SKILLS[DOOMSDAY_ULT] = Skill(
        name="末日降临",
        type=SkillType.ULT,
        multiplier=1.50,
        damage_type=Element.ICE,
        description="对敌方全体造成150%攻击力的冰属性伤害，80%概率附加【冻结】2回合",
        energy_gain=0.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )
    _ENEMY_SKILLS[DOOMSDAY_TALENT] = Skill(
        name="末日咆哮",
        type=SkillType.TALENT,
        multiplier=0.80,
        damage_type=Element.THUNDER,
        description="回合开始时，对所有敌人造成80%攻击力的雷属性伤害（追击触发）",
        energy_gain=5.0,
        break_power=15,
        target_count=-1,
    )

# -----------------------
# 布洛妮娅（敌方版）
# 定位：风/虚数属性辅助
# 特点：拉条、护盾、群体增益
# -----------------------
def _register_bronya_enemy():
    _ENEMY_SKILLS[BRONYA_ENEMY_BASIC] = Skill(
        name="风弹",
        type=SkillType.BASIC,
        multiplier=0.45,
        damage_type=Element.WIND,
        description="对单体造成45%攻击力的风属性伤害",
        energy_gain=10.0,
        break_power=20,
        target_count=1,
    )
    _ENEMY_SKILLS[BRONYA_ENEMY_SPECIAL] = Skill(
        name="指令·敌方",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.30,
        damage_type=Element.IMAGINARY,
        description="对一个敌人造成30%攻击力伤害，并使其行动延后30%",
        energy_gain=15.0,
        break_power=15,
        target_count=1,
    )
    _ENEMY_SKILLS[BRONYA_ENEMY_ULT] = Skill(
        name="战争天使",
        type=SkillType.ULT,
        multiplier=0.80,
        damage_type=Element.WIND,
        description="对敌方全体造成80%攻击力的风属性伤害，为我方全体提供【加速】效果",
        energy_gain=0.0,
        break_power=30,
        target_count=-1,
        aoe_multiplier=0.8,
    )

# -----------------------
# 银狼（敌方版）
# 定位：雷/量子属性输出
# 特点：量子DOT、弱点标记、群体降防
# -----------------------
def _register_silverwolf_enemy():
    _ENEMY_SKILLS[SILVERWOLF_BASIC] = Skill(
        name="代码侵蚀",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.THUNDER,
        description="对单体造成50%攻击力的雷属性伤害",
        energy_gain=10.0,
        break_power=25,
        target_count=1,
    )
    _ENEMY_SKILLS[SILVERWOLF_SPECIAL] = Skill(
        name="量子标记",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.60,
        damage_type=Element.QUANTUM,
        description="对单体造成60%攻击力的量子属性伤害，附加【弱点标记】：受到伤害+15%",
        energy_gain=15.0,
        break_power=30,
        target_count=1,
    )
    _ENEMY_SKILLS[SILVERWOLF_ULT] = Skill(
        name="系统沦陷",
        type=SkillType.ULT,
        multiplier=0.50,
        damage_type=Element.QUANTUM,
        description="对敌方全体造成50%×3次量子属性伤害，每次命中附加【纠缠】效果",
        energy_gain=0.0,
        break_power=40,
        target_count=-1,
        aoe_multiplier=0.8,
    )

# -----------------------
# 史瓦罗（Svarog）
# 定位：火/物理属性首领
# 特点：召唤机械、群体火伤
# -----------------------
def _register_swarler():
    _ENEMY_SKILLS[SWARLER_BASIC] = Skill(
        name="机械重拳",
        type=SkillType.BASIC,
        multiplier=0.55,
        damage_type=Element.PHYSICAL,
        description="对单体造成55%攻击力的物理属性伤害",
        energy_gain=10.0,
        break_power=30,
        target_count=1,
    )
    _ENEMY_SKILLS[SWARLER_SPECIAL] = Skill(
        name="烈焰发射",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.70,
        damage_type=Element.FIRE,
        description="对敌方全体造成70%攻击力的火属性伤害，30%概率附加【灼烧】DOT",
        energy_gain=15.0,
        break_power=35,
        target_count=-1,
        aoe_multiplier=0.6,
    )
    _ENEMY_SKILLS[SWARLER_ULT] = Skill(
        name="史瓦罗降临",
        type=SkillType.ULT,
        multiplier=1.30,
        damage_type=Element.FIRE,
        description="对敌方全体造成130%攻击力的火属性伤害，100%概率附加【灼烧】DOT 3层",
        energy_gain=0.0,
        break_power=50,
        target_count=-1,
        aoe_multiplier=0.8,
    )

# -----------------------
# 可可利亚（Cocolia）
# 定位：雷/冰属性首领
# 特点：冰冻控制、群体雷伤
# -----------------------
def _register_coconia():
    _ENEMY_SKILLS[COCONIA_BASIC] = Skill(
        name="冰霜之矛",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.ICE,
        description="对单体造成50%攻击力的冰属性伤害",
        energy_gain=10.0,
        break_power=30,
        target_count=1,
    )
    _ENEMY_SKILLS[COCONIA_SPECIAL] = Skill(
        name="冰棘阵",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.60,
        damage_type=Element.ICE,
        description="对敌方全体造成60%攻击力的冰属性伤害，40%概率附加【冻结】1回合",
        energy_gain=15.0,
        break_power=40,
        target_count=-1,
        aoe_multiplier=0.6,
    )
    _ENEMY_SKILLS[COCONIA_ULT] = Skill(
        name="极寒新星",
        type=SkillType.ULT,
        multiplier=1.20,
        damage_type=Element.THUNDER,
        description="对敌方全体造成120%攻击力的雷属性伤害，80%概率附加【冻结】2回合",
        energy_gain=0.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )
    _ENEMY_SKILLS[COCONIA_TALENT] = Skill(
        name="冰霜之魂",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.ICE,
        description="生命值低于50%时，冰属性伤害提升30%，冻结概率+20%",
        energy_gain=0.0,
        break_power=0,
    )

# -----------------------
# 机械士兵（Elite Mech Soldier）
# 定位：物理属性精英
# 特点：连续攻击、护盾
# -----------------------
def _register_mech_soldier():
    _ENEMY_SKILLS[MECH_SOLDIER_BASIC] = Skill(
        name="机械突刺",
        type=SkillType.BASIC,
        multiplier=0.45,
        damage_type=Element.PHYSICAL,
        description="对单体造成45%攻击力的物理属性伤害",
        energy_gain=10.0,
        break_power=20,
        target_count=1,
    )
    _ENEMY_SKILLS[MECH_SOLDIER_SPECIAL] = Skill(
        name="能量护盾",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.60,
        damage_type=Element.PHYSICAL,
        description="对单体造成60%攻击力的物理属性伤害，同时为自身附加【护盾】",
        energy_gain=15.0,
        break_power=25,
        target_count=1,
    )

# -----------------------
# 异形猎手（Alien Hunter）
# 定位：风属性精英
# 特点：追击、多段攻击
# -----------------------
def _register_alien_hunter():
    _ENEMY_SKILLS[ALIEN_HUNTER_BASIC] = Skill(
        name="利爪撕裂",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.WIND,
        description="对单体造成50%攻击力的风属性伤害",
        energy_gain=10.0,
        break_power=25,
        target_count=1,
    )
    _ENEMY_SKILLS[ALIEN_HUNTER_SPECIAL] = Skill(
        name="疾风连击",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.35,
        damage_type=Element.WIND,
        description="对单体造成35%×3次风属性伤害",
        energy_gain=20.0,
        break_power=20,
        target_count=1,
    )
    _ENEMY_SKILLS[ALIEN_HUNTER_TALENT] = Skill(
        name="猎手本能",
        type=SkillType.TALENT,
        multiplier=0.40,
        damage_type=Element.WIND,
        description="对生命值最低的敌人造成40%攻击力的追加风属性伤害（追击）",
        energy_gain=5.0,
        break_power=15,
        target_count=1,
    )

# -----------------------
# 焚烬者（Inferno）
# 定位：火属性精英
# 特点：群体火伤、灼烧叠加
# -----------------------
def _register_inferno():
    _ENEMY_SKILLS[INFERNO_BASIC] = Skill(
        name="火焰冲击",
        type=SkillType.BASIC,
        multiplier=0.55,
        damage_type=Element.FIRE,
        description="对单体造成55%攻击力的火属性伤害",
        energy_gain=10.0,
        break_power=30,
        target_count=1,
    )
    _ENEMY_SKILLS[INFERNO_SPECIAL] = Skill(
        name="烈焰风暴",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.65,
        damage_type=Element.FIRE,
        description="对敌方全体造成65%攻击力的火属性伤害，50%概率附加【灼烧】",
        energy_gain=15.0,
        break_power=40,
        target_count=-1,
        aoe_multiplier=0.6,
    )
    _ENEMY_SKILLS[INFERNO_ULT] = Skill(
        name="焚尽一切",
        type=SkillType.ULT,
        multiplier=1.10,
        damage_type=Element.FIRE,
        description="对敌方全体造成110%×2次火属性伤害，每次100%附加【灼烧】DOT 2层",
        energy_gain=0.0,
        break_power=50,
        target_count=-1,
        aoe_multiplier=0.8,
    )

# -----------------------
# 霜饥者（Frost）
# 定位：冰属性精英
# 特点：冻结控制、冰刺AOE
# -----------------------
def _register_frost():
    _ENEMY_SKILLS[FROST_BASIC] = Skill(
        name="冰霜之触",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.ICE,
        description="对单体造成50%攻击力的冰属性伤害，20%概率附加【冻结】1回合",
        energy_gain=10.0,
        break_power=30,
        target_count=1,
    )
    _ENEMY_SKILLS[FROST_SPECIAL] = Skill(
        name="冰刺阵",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.55,
        damage_type=Element.ICE,
        description="对敌方全体造成55%攻击力的冰属性伤害，40%概率附加【冻结】1回合",
        energy_gain=15.0,
        break_power=45,
        target_count=-1,
        aoe_multiplier=0.6,
    )
    _ENEMY_SKILLS[FROST_ULT] = Skill(
        name="绝对零度",
        type=SkillType.ULT,
        multiplier=1.30,
        damage_type=Element.ICE,
        description="对敌方全体造成130%攻击力的冰属性伤害，80%概率附加【冻结】2回合",
        energy_gain=0.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )


# ============================================================
# 初始化所有敌人技能
# ============================================================

def _init_enemy_skills():
    _register_silvermane()
    _register_sandworm()
    _register_doomsday()
    _register_bronya_enemy()
    _register_silverwolf_enemy()
    _register_swarler()
    _register_coconia()
    _register_mech_soldier()
    _register_alien_hunter()
    _register_inferno()
    _register_frost()


# 启动时自动注册
_init_enemy_skills()


# ============================================================
# 公共API
# ============================================================

def get_enemy_skill(skill_id: str) -> Skill | None:
    """根据技能ID获取技能对象"""
    return _ENEMY_SKILLS.get(skill_id)


def get_enemy_skills_by_ids(skill_ids: list[str]) -> list[Skill]:
    """根据技能ID列表获取技能对象列表"""
    return [s for s in (_ENEMY_SKILLS.get(sid) for sid in skill_ids) if s is not None]


def list_all_enemy_skills() -> dict[str, Skill]:
    """返回所有敌人技能的字典副本"""
    return dict(_ENEMY_SKILLS)


def get_skill_count() -> int:
    """返回敌人技能总数"""
    return len(_ENEMY_SKILLS)


def get_skills_by_prefix(prefix: str) -> list[Skill]:
    """返回所有以指定前缀开头的技能（如 'silvermane_' 返回银鬃铁卫所有技能）"""
    return [s for sid, s in _ENEMY_SKILLS.items() if sid.startswith(prefix)]


# ============================================================
# 敌人技能组配置 - 用于enemies.json引用
# ============================================================

# 敌人ID -> 技能ID列表
ENEMY_SKILL_GROUPS: dict[str, list[str]] = {
    # 精英敌人
    "silvermane_guard": [SILVERMANE_BASIC, SILVERMANE_SPECIAL, SILVERMANE_ULT, SILVERMANE_TALENT],
    "sandworm": [SANDWORM_BASIC, SANDWORM_SPECIAL, SANDWORM_ULT],
    "mech_soldier": [MECH_SOLDIER_BASIC, MECH_SOLDIER_SPECIAL],
    "alien_hunter": [ALIEN_HUNTER_BASIC, ALIEN_HUNTER_SPECIAL, ALIEN_HUNTER_TALENT],
    "inferno": [INFERNO_BASIC, INFERNO_SPECIAL, INFERNO_ULT],
    "frost": [FROST_BASIC, FROST_SPECIAL, FROST_ULT],
    # 首领敌人
    "doomsday_beast": [DOOMSDAY_BASIC, DOOMSDAY_SPECIAL, DOOMSDAY_ULT, DOOMSDAY_TALENT],
    "bronya_enemy": [BRONYA_ENEMY_BASIC, BRONYA_ENEMY_SPECIAL, BRONYA_ENEMY_ULT],
    "silverwolf_enemy": [SILVERWOLF_BASIC, SILVERWOLF_SPECIAL, SILVERWOLF_ULT],
    "swarler": [SWARLER_BASIC, SWARLER_SPECIAL, SWARLER_ULT],
    "coconia": [COCONIA_BASIC, COCONIA_SPECIAL, COCONIA_ULT, COCONIA_TALENT],
}


def assign_skills_to_enemy(enemy_name: str, skill_ids: list[str]) -> list[Skill]:
    """
    根据敌人名称分配技能。
    优先从 ENEMY_SKILL_GROUPS 查找，否则从 skill_ids 直接获取。
    """
    # 先查找预定义技能组
    name_key = enemy_name.lower().replace(" ", "_").replace("　", "_")
    if name_key in ENEMY_SKILL_GROUPS:
        group_ids = ENEMY_SKILL_GROUPS[name_key]
        return get_enemy_skills_by_ids(group_ids)

    # 直接从skill_ids获取
    return get_enemy_skills_by_ids(skill_ids)
