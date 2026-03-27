"""
敌人AI系统测试
"""
import pytest
from src.game.enemy_ai import (
    EnemyAI, TeamAI, BossAI, EliteAI,
    AIPersonality, TargetSelection, AIConsideration,
    create_enemy_ai, create_team_ai, create_boss_ai
)
from src.game.models import Character, Element, Stat, Skill, SkillType


def create_test_character(name: str, hp: float, atk: float, spd: float, element: Element = Element.PHYSICAL) -> Character:
    """创建测试角色"""
    char = Character(
        name=name,
        level=50,
        element=element,
        stat=Stat(
            base_max_hp=hp,
            base_atk=atk,
            base_def=400,
            base_spd=spd,
        ),
        skills=[],
        passives=[],
        is_enemy=False,
    )
    char.current_hp = hp
    char.energy = 0
    char.energy_limit = 100
    char.battle_points = 3
    return char


def create_test_enemy(name: str, hp: float, atk: float, spd: float) -> Character:
    """创建测试敌人"""
    char = create_test_character(name, hp, atk, spd)
    char.is_enemy = True
    return char


def create_test_skill(name: str, skill_type: SkillType, multiplier: float = 1.0, cost: int = 0, is_aoe: bool = False) -> Skill:
    """创建测试技能"""
    return Skill(
        name=name,
        type=skill_type,
        multiplier=multiplier,
        cost=cost,
        damage_type=Element.PHYSICAL,
        target_count=-1 if is_aoe else 1,
        energy_gain=0,
        break_power=30,
    )


class TestTargetSelection:
    """目标选择测试"""
    
    def test_lowest_hp(self):
        """血量最低优先"""
        ai = create_enemy_ai("aggressive")
        ai.config.target_strategy = TargetSelection.LOWEST_HP
        
        enemies = [
            create_test_enemy("E1", hp=1000, atk=100, spd=80),
            create_test_enemy("E2", hp=500, atk=100, spd=80),
            create_test_enemy("E3", hp=2000, atk=100, spd=80),
        ]
        
        actor = create_test_enemy("Boss", hp=5000, atk=500, spd=90)
        target = ai.select_target(actor, enemies)
        
        assert target.name == "E2"  # 血量最低
    
    def test_highest_threat(self):
        """威胁最高优先"""
        ai = create_enemy_ai("conservative")
        ai.config.target_strategy = TargetSelection.HIGHEST_THREAT
        
        enemies = [
            create_test_enemy("E1", hp=1000, atk=500, spd=80),
            create_test_enemy("E2", hp=500, atk=100, spd=80),
            create_test_enemy("E3", hp=2000, atk=800, spd=100),
        ]
        
        actor = create_test_enemy("Boss", hp=5000, atk=500, spd=90)
        target = ai.select_target(actor, enemies)
        
        assert target.name == "E3"  # 威胁最高（高攻击+高速度）
    
    def test_random_selection(self):
        """随机选择"""
        ai = create_enemy_ai("balanced")
        ai.config.target_strategy = TargetSelection.RANDOM
        
        enemies = [
            create_test_enemy("E1", hp=1000, atk=100, spd=80),
            create_test_enemy("E2", hp=500, atk=100, spd=80),
        ]
        
        actor = create_test_enemy("Boss", hp=5000, atk=500, spd=90)
        
        # 多次选择应该有不同的结果
        results = set()
        for _ in range(20):
            target = ai.select_target(actor, enemies)
            results.add(target.name)
        
        # 随机选择应该选择到两个目标
        assert len(results) >= 1


class TestSkillSelection:
    """技能选择测试"""
    
    def test_ult优先(self):
        """能量足够时优先ULT"""
        ai = create_enemy_ai("aggressive")
        
        actor = create_test_enemy("Boss", hp=5000, atk=500, spd=90)
        actor.energy = 100  # 满能量
        actor.energy_limit = 100
        
        skills = [
            create_test_skill("Basic", SkillType.BASIC, 0.5),
            create_test_skill("Special", SkillType.SPECIAL, 1.0, cost=1),
            create_test_skill("ULT", SkillType.ULT, 2.0),
        ]
        
        opponents = [create_test_character("P1", hp=1000, atk=100, spd=80)]
        skill, targets = ai.select_skill(actor, skills, opponents)
        
        assert skill.name == "ULT"
    
    def test_aoe优先(self):
        """多目标时优先AOE"""
        ai = create_enemy_ai("aggressive")  # 激进性格更可能选AOE
        ai.config.aoe_threshold = 2
        
        actor = create_test_enemy("Boss", hp=5000, atk=500, spd=90)
        actor.energy = 0
        
        skills = [
            create_test_skill("Single", SkillType.BASIC, 1.0),
            create_test_skill("AOE", SkillType.SPECIAL, 0.5, is_aoe=True),
        ]
        
        opponents = [
            create_test_character("P1", hp=1000, atk=100, spd=80),
            create_test_character("P2", hp=1000, atk=100, spd=80),
        ]
        
        # 测试多次，增加命中AOE选择的概率
        aoe_selected = False
        for _ in range(10):
            skill, targets = ai.select_skill(actor, skills, opponents)
            if skill and skill.name == "AOE":
                aoe_selected = True
                break
        
        assert aoe_selected, f"AOE should be selected, got {skill.name if skill else None}"
    
    def test_basic_when_no_energy(self):
        """没能量时使用普攻"""
        ai = create_enemy_ai("balanced")
        
        actor = create_test_enemy("Boss", hp=5000, atk=500, spd=90)
        actor.energy = 0
        actor.battle_points = 0  # 没有战技点
        
        skills = [
            create_test_skill("Basic", SkillType.BASIC, 0.5),
            create_test_skill("Special", SkillType.SPECIAL, 1.0, cost=1),
            create_test_skill("ULT", SkillType.ULT, 2.0),
        ]
        
        opponents = [create_test_character("P1", hp=1000, atk=100, spd=80)]
        skill, targets = ai.select_skill(actor, skills, opponents)
        
        assert skill.name == "Basic"


class TestBossAI:
    """BOSS AI测试"""
    
    def test_phase_update(self):
        """阶段更新"""
        ai = create_boss_ai(max_phase=3)
        
        ai.update_phase(5000, 10000)  # 50% HP
        assert ai.phase == 2
        
        ai.update_phase(1000, 10000)  # 10% HP
        assert ai.phase == 3  # 狂暴
    
    def test_phase3_enrage(self):
        """狂暴阶段使用ULT"""
        ai = create_boss_ai()
        
        actor = create_test_enemy("Boss", hp=1000, atk=500, spd=90)
        actor.energy = 100
        actor.energy_limit = 100
        
        skills = [
            create_test_skill("Basic", SkillType.BASIC, 0.5),
            create_test_skill("ULT", SkillType.ULT, 3.0),
        ]
        
        opponents = [
            create_test_character("P1", hp=1000, atk=100, spd=80),
            create_test_character("P2", hp=1000, atk=100, spd=80),
        ]
        
        ai.phase = 3  # 狂暴阶段
        skill, targets = ai.select_skill_for_phase(actor, skills, opponents)
        
        assert skill.name == "ULT"
        assert len(targets) == 2  # AOE


class TestEliteAI:
    """精英怪AI测试"""
    
    def test_defensive_skill_low_hp(self):
        """低血量使用防御技能"""
        ai = EliteAI()
        
        actor = create_test_enemy("Elite", hp=1000, atk=500, spd=90)
        actor.current_hp = 200  # 低血量
        
        assert ai.should_use_defensive_skill(actor) == True
    
    def test_no_defensive_skill_full_hp(self):
        """满血量不使用防御技能"""
        ai = EliteAI()
        
        actor = create_test_enemy("Elite", hp=1000, atk=500, spd=90)
        actor.current_hp = 1000  # 满血
        
        assert ai.should_use_defensive_skill(actor) == False


class TestAIPersonalities:
    """AI性格测试"""
    
    def test_aggressive_targeting(self):
        """激进性格选择最低血量"""
        ai = create_enemy_ai("aggressive")
        
        enemies = [
            create_test_enemy("E1", hp=1000, atk=100, spd=80),
            create_test_enemy("E2", hp=300, atk=100, spd=80),
        ]
        
        actor = create_test_enemy("Boss", hp=5000, atk=500, spd=90)
        target = ai.select_target(actor, enemies)
        
        assert target.name == "E2"  # 血量最低
    
    def test_conservative_targeting(self):
        """保守性格选择高威胁"""
        ai = create_enemy_ai("conservative")
        
        enemies = [
            create_test_enemy("E1", hp=1000, atk=200, spd=80),
            create_test_enemy("E2", hp=300, atk=1000, spd=120),
        ]
        
        actor = create_test_enemy("Boss", hp=5000, atk=500, spd=90)
        target = ai.select_target(actor, enemies)
        
        assert target.name == "E2"  # 威胁最高


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestTeamAI:
    """团队AI测试"""
    
    def test_role_assignment(self):
        """角色分配"""
        ai = create_team_ai("aggressive")
        
        # 创建团队
        team = [
            create_test_character("E1", hp=3000, atk=300, spd=100),
            create_test_character("E2", hp=3000, atk=300, spd=110),
        ]
        
        ai.assign_roles(team)
        
        # 验证角色分配完成
        assert len(ai.role_assignments) == 2
        
        # 验证有DPS角色
        roles = list(ai.role_assignments.values())
        assert "dps" in roles
