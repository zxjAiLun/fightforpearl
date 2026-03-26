"""战斗配置常量"""

# 行动值常量（AV = Action Value，崩铁基准为10000）
AV_BASE = 10000.0          # 行动值基准
FIRST_ROUND_AV = 10000.0   # 第一轮行动值
SUBSEQUENT_AV = 10000.0    # 后续回合行动值

# 敌人血量常量
HEART_HP_BASE = 21997.729  # 90级标准血量（1 heart）
HP_LINEAR_VALUES = {
    0: HEART_HP_BASE,      # 默认难度
    1: 26954.786,          # 混沌难度（1.226×）
}

# 能量配置
ENERGY_CONFIG = {
    'default_limit': 120,
    'default_initial': 60,
    'basic_gain': 20,
    'special_gain': 30,
    'ult_gain': 5,
    'kill_gain': 10,
    'hit_gain': 10,
}

# 战绩点配置
BATTLE_POINTS_CONFIG = {
    'default_limit': 6,
    'default_initial': 3,
    'basic_gain': 1,       # 普攻回复
    'special_cost': 1,     # 战技消耗
}

def get_energy_config(key: str, default=None):
    return ENERGY_CONFIG.get(key, default)

def get_battle_points_config(key: str, default=None):
    return BATTLE_POINTS_CONFIG.get(key, default)
