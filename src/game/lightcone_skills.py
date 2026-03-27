"""
光锥技能池 - 将光锥效果解析为技能

基于61个光锥数据的效果解析
"""
import re
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class LightconeEffectType(Enum):
    """光锥效果类型"""
    # 属性加成类
    HP_BOOST = "hp_boost"           # 生命值提升
    ATK_BOOST = "atk_boost"         # 攻击力提升
    DEF_BOOST = "def_boost"         # 防御力提升
    SPD_BOOST = "spd_boost"          # 速度提升
    CRIT_RATE = "crit_rate"          # 暴击率
    CRIT_DMG = "crit_dmg"           # 暴击伤害
    
    # 增伤类
    DMG_BOOST = "dmg_boost"          # 伤害提升
    ELEMENT_DMG = "element_dmg"      # 属性伤害提升
    BREAK_DMG = "break_dmg"          # 击破伤害提升
    
    # 特殊效果
    SHIELD = "shield"                # 护盾
    HEAL = "heal"                   # 治疗
    ENERGY = "energy"                # 能量
    ACTION_FORWARD = "action_forward" # 行动提前
    
    # 触发类
    FOLLOW_UP = "follow_up"          # 追加攻击
    DOT = "dot"                      # 持续伤害
    DEBUFF = "debuff"               # 减益效果


@dataclass
class LightconeEffect:
    """光锥效果"""
    name: str
    effect_type: LightconeEffectType
    value: float  # 效果值
    duration: int = 2  # 持续回合
    condition: str = ""  # 触发条件
    description: str = ""


# 光锥效果池
LIGHTCONE_SKILLS = {
    # === 23000系列 ===
    
    # 存护
    "命运从未公平": [
        LightconeEffect("护盾时暴伤", LightconeEffectType.CRIT_DMG, 0.40, 2, "提供护盾时"),
        LightconeEffect("追加攻击增伤", LightconeEffectType.DMG_BOOST, 0.10, 2, "追加攻击命中"),
    ],
    
    # 巡猎
    "于夜色中": [
        LightconeEffect("暴击率", LightconeEffectType.CRIT_RATE, 0.18, 0, "被动"),
        LightconeEffect("速度增伤", LightconeEffectType.DMG_BOOST, 0.06, 0, "速度>100时每超10点"),
        LightconeEffect("终结技暴伤", LightconeEffectType.CRIT_DMG, 0.12, 0, "速度>100时每超10点"),
    ],
    
    # === 24000系列 ===
    
    "星海巡航": [
        LightconeEffect("暴击率", LightconeEffectType.CRIT_RATE, 0.08, 0, "被动"),
        LightconeEffect("低血增伤", LightconeEffectType.CRIT_RATE, 0.08, 0, "敌人HP<=50%"),
        LightconeEffect("击杀攻击", LightconeEffectType.ATK_BOOST, 0.20, 200, "消灭敌人后"),
    ],
}


def get_lightcone_effects(lightcone_name: str) -> list[LightconeEffect]:
    """获取光锥的效果列表"""
    return LIGHTCONE_SKILLS.get(lightcone_name, [])


def parse_all_lightcones():
    """解析所有光锥数据并创建技能池"""
    import json
    from pathlib import Path
    
    lightcones_dir = Path("data/lightcones")
    all_effects = {}
    
    for lc_file in lightcones_dir.glob("*.json"):
        if lc_file.stem == "summary":
            continue
        
        with open(lc_file, encoding='utf-8') as f:
            data = json.load(f)
        
        name = data.get('name', '')
        effect_text = data.get('effect', '')
        
        if not name or not effect_text:
            continue
        
        # 解析效果文本
        effects = parse_effect_text(effect_text, name)
        if effects:
            all_effects[name] = effects
    
    return all_effects


def parse_effect_text(effect_text: str, lightcone_name: str) -> list[LightconeEffect]:
    """解析效果描述文本"""
    effects = []
    
    # 防御力提高
    if '防御力提高' in effect_text:
        match = re.search(r'防御力提高(\d+\.?\d*)%', effect_text)
        if match:
            effects.append(LightconeEffect(
                name=f"{lightcone_name}-防御",
                effect_type=LightconeEffectType.DEF_BOOST,
                value=float(match.group(1)) / 100,
                description=f"防御力提高{match.group(1)}%"
            ))
    
    # 暴击率
    if '暴击率提高' in effect_text:
        match = re.search(r'暴击率提高(\d+\.?\d*)%', effect_text)
        if match:
            effects.append(LightconeEffect(
                name=f"{lightcone_name}-暴击率",
                effect_type=LightconeEffectType.CRIT_RATE,
                value=float(match.group(1)) / 100,
                description=f"暴击率提高{match.group(1)}%"
            ))
    
    # 暴击伤害
    if '暴击伤害提高' in effect_text:
        match = re.search(r'暴击伤害提高(\d+\.?\d*)%', effect_text)
        if match:
            effects.append(LightconeEffect(
                name=f"{lightcone_name}-暴击伤害",
                effect_type=LightconeEffectType.CRIT_DMG,
                value=float(match.group(1)) / 100,
                description=f"暴击伤害提高{match.group(1)}%"
            ))
    
    # 伤害提高
    if '伤害提高' in effect_text and '受到伤害' not in effect_text:
        match = re.search(r'伤害提高(\d+\.?\d*)%', effect_text)
        if match:
            effects.append(LightconeEffect(
                name=f"{lightcone_name}-增伤",
                effect_type=LightconeEffectType.DMG_BOOST,
                value=float(match.group(1)) / 100,
                description=f"伤害提高{match.group(1)}%"
            ))
    
    # 攻击力提高
    if '攻击力提高' in effect_text:
        match = re.search(r'攻击力提高(\d+\.?\d*)%', effect_text)
        if match:
            effects.append(LightconeEffect(
                name=f"{lightcone_name}-攻击",
                effect_type=LightconeEffectType.ATK_BOOST,
                value=float(match.group(1)) / 100,
                description=f"攻击力提高{match.group(1)}%"
            ))
    
    # 护盾
    if '护盾' in effect_text:
        effects.append(LightconeEffect(
            name=f"{lightcone_name}-护盾",
            effect_type=LightconeEffectType.SHIELD,
            value=0.0,
            description="提供护盾"
        ))
    
    # 追加攻击
    if '追加攻击' in effect_text:
        match = re.search(r'追加攻击.*?(\d+\.?\d*)%', effect_text)
        value = float(match.group(1)) / 100 if match else 0.0
        effects.append(LightconeEffect(
            name=f"{lightcone_name}-追加",
            effect_type=LightconeEffectType.FOLLOW_UP,
            value=value,
            description="触发追加攻击"
        ))
    
    # 持续伤害
    if '持续' in effect_text and '伤害' in effect_text:
        effects.append(LightconeEffect(
            name=f"{lightcone_name}-灼烧",
            effect_type=LightconeEffectType.DOT,
            value=0.0,
            description="造成持续伤害"
        ))
    
    return effects


if __name__ == "__main__":
    # 测试解析
    effects = parse_all_lightcones()
    print(f"解析到 {len(effects)} 个光锥效果")
    for name, effs in list(effects.items())[:3]:
        print(f"\n{name}:")
        for e in effs:
            print(f"  - {e.effect_type.value}: {e.value}")
