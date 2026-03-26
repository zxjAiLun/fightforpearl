"""战斗配置常量"""

FIRST_ROUND_AV = 150.0
SUBSEQUENT_AV = 100.0

HEART_HP_BASE = 21997.729

HP_LINEAR_VALUES = {
    0: HEART_HP_BASE,
    1: 26954.786,
}

ENERGY_CONFIG = {
    'default_limit': 120,
    'default_initial': 60,
    'basic_gain': 20,
    'special_gain': 30,
    'ult_gain': 5,
    'kill_gain': 10,
    'hit_gain': 10,
}

def get_energy_config(key: str, default=None):
    return ENERGY_CONFIG.get(key, default)
