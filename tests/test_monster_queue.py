"""
怪物队列系统测试

测试目标：
1. 队列加载和初始生成
2. 怪物HP归零移除
3. 补位机制
4. 波次管理
"""
import pytest
from src.game.monster_queue import MonsterQueue, MonsterSpawnInfo, WaveManager, create_enemy_from_spawn_info
from src.game.models import Character, Element, Stat


class MockCharacter(Character):
    """测试用Mock角色"""
    _monster_queue_ref = None
    _instance_id = 0
    
    def __init__(self, name, hp, max_hp):
        self.name = name
        self.current_hp = hp
        self._max_hp = max_hp
        self._is_alive = hp > 0
        self._id = MockCharacter._instance_id
        MockCharacter._instance_id += 1
    
    @property
    def is_alive(self):
        return self.current_hp > 0
    
    def take_damage(self, damage):
        self.current_hp = max(0, self.current_hp - damage)
        return self.current_hp <= 0
    
    def __eq__(self, other):
        if isinstance(other, MockCharacter):
            return self._id == other._id
        return False
    
    def __hash__(self):
        return hash(self._id)


def mock_factory(info: MonsterSpawnInfo) -> Character:
    """Mock工厂函数"""
    return MockCharacter(info.name, info.max_hp, info.max_hp)


class TestMonsterQueue:
    """MonsterQueue基础测试"""
    
    def test_load_queue(self):
        """测试队列加载"""
        queue = MonsterQueue(max_front=5)
        
        monsters = [
            MonsterSpawnInfo(name="银鬃铁卫", max_hp=5000),
            MonsterSpawnInfo(name="凝滞沙影", max_hp=4000),
            MonsterSpawnInfo(name="末日兽", max_hp=10000),
        ]
        
        queue.load_queue(monsters)
        
        assert len(queue) == 3
        assert len(queue.queue_monsters) == 3
    
    def test_spawn_initial(self):
        """测试初始生成"""
        queue = MonsterQueue(max_front=5)
        
        monsters = [
            MonsterSpawnInfo(name="银鬃铁卫", max_hp=5000),
            MonsterSpawnInfo(name="凝滞沙影", max_hp=4000),
            MonsterSpawnInfo(name="末日兽", max_hp=10000),
        ]
        
        queue.load_queue(monsters)
        spawned = queue.spawn_initial(mock_factory)
        
        assert len(spawned) == 3  # 队列有3个，max_front=5，所以生成3个
        assert len(queue.front_monsters) == 3
        assert len(queue.queue_monsters) == 0
    
    def test_spawn_with_max_front(self):
        """测试前台数量限制"""
        queue = MonsterQueue(max_front=2)
        
        monsters = [
            MonsterSpawnInfo(name=f"怪物{i}", max_hp=1000)
            for i in range(5)
        ]
        
        queue.load_queue(monsters)
        spawned = queue.spawn_initial(mock_factory)
        
        assert len(spawned) == 2  # 最多2个前台
        assert len(queue.front_monsters) == 2
        assert len(queue.queue_monsters) == 3  # 剩余3个在队列
    
    def test_enemy_defeated_and_replace(self):
        """测试敌人被击败后补位"""
        queue = MonsterQueue(max_front=3)
        
        monsters = [
            MonsterSpawnInfo(name=f"怪物{i}", max_hp=1000)
            for i in range(5)
        ]
        
        queue.load_queue(monsters)
        spawned = queue.spawn_initial(mock_factory)
        
        assert len(queue.front_monsters) == 3
        assert len(queue.queue_monsters) == 2  # 5个加载，3个生成，剩2个
        
        # 击败第一个怪物（传入factory用于补位）
        defeated = spawned[0]
        queue.check_defeated_and_replace(defeated, mock_factory)
        
        assert len(queue.front_monsters) == 3  # 补位了队列中的怪物
        assert len(queue.queue_monsters) == 1  # 补位后队列剩1个
    
    def test_enemy_hp_zero_removal(self):
        """测试HP归零移除"""
        queue = MonsterQueue(max_front=5)
        
        monsters = [
            MonsterSpawnInfo(name="怪物1", max_hp=500),
            MonsterSpawnInfo(name="怪物2", max_hp=1000),
        ]
        
        queue.load_queue(monsters)
        spawned = queue.spawn_initial(mock_factory)
        
        # 模拟HP归零
        monster1 = spawned[0]
        monster1.current_hp = 0
        
        queue.check_defeated_and_replace(monster1, mock_factory)
        
        assert monster1 not in queue.front_monsters
        # 队列已空，没有补位，所以只剩怪物2
        assert len(queue.front_monsters) == 1
    
    def test_wave_clear_check(self):
        """测试波次清理检查"""
        queue = MonsterQueue(max_front=5)
        
        # 空队列
        assert queue.check_wave_clear() == True
        
        monsters = [MonsterSpawnInfo(name="怪物", max_hp=1000)]
        queue.load_queue(monsters)
        
        # 队列未生成，不算清理
        assert queue.check_wave_clear() == False
        
        queue.spawn_initial(mock_factory)
        
        # 生成了前台怪物，未清理
        assert queue.check_wave_clear() == False
    
    def test_queue_empty_state(self):
        """测试队列为空状态"""
        queue = MonsterQueue()
        
        assert queue.is_empty == True
        
        queue.load_queue([MonsterSpawnInfo(name="怪物", max_hp=1000)])
        
        assert queue.is_empty == False


class TestWaveManager:
    """波次管理器测试"""
    
    def test_wave_config(self):
        """测试波次配置"""
        wave1 = [MonsterSpawnInfo(name="怪物1", max_hp=1000)]
        wave2 = [MonsterSpawnInfo(name="怪物2", max_hp=2000)]
        
        wm = WaveManager([wave1, wave2])
        
        assert wm.total_waves == 2
        assert wm.current_wave == 0
    
    def test_start_wave(self):
        """测试开始波次"""
        wave1 = [
            MonsterSpawnInfo(name="怪物1", max_hp=1000),
            MonsterSpawnInfo(name="怪物2", max_hp=1000),
        ]
        
        wm = WaveManager([wave1])
        mq = wm.start_wave(mock_factory)
        
        assert wm.current_wave == 1
        assert mq is not None
        assert len(mq.front_monsters) == 2
    
    def test_advance_wave(self):
        """测试波次推进"""
        waves = [
            [MonsterSpawnInfo(name="波次1怪物", max_hp=1000)],
            [MonsterSpawnInfo(name="波次2怪物", max_hp=2000)],
        ]
        
        wm = WaveManager(waves)
        mq = wm.start_wave(mock_factory)
        
        # 清空当前波次
        for monster in mq.front_monsters[:]:
            mq.check_defeated_and_replace(monster, mock_factory)
        
        assert mq.check_wave_clear() == True
        
        # 推进到下一波次（使用内部方法）
        mq2 = wm._start_wave_internal()
        
        assert wm.current_wave == 2
        assert len(mq2.front_monsters) == 1


class TestMonsterQueueIntegration:
    """怪物队列集成测试 - 模拟真实战斗场景"""
    
    def test_battle_with_queue(self):
        """模拟战斗流程：4角色 vs 怪物队列"""
        # 怪物队列配置
        enemy_waves = [
            # 第一波：2个精英怪
            [
                MonsterSpawnInfo(name="银鬃铁卫", max_hp=5000, atk=500),
                MonsterSpawnInfo(name="凝滞沙影", max_hp=4000, atk=400),
            ],
            # 第二波：3个怪物
            [
                MonsterSpawnInfo(name="异形猎手", max_hp=3000, atk=600),
                MonsterSpawnInfo(name="焚烬者", max_hp=3500, atk=550),
                MonsterSpawnInfo(name="霜饥者", max_hp=3200, atk=520),
            ],
        ]
        
        wm = WaveManager(enemy_waves)
        
        # 开始第一波
        mq = wm.start_wave(mock_factory)
        
        # 验证第一波状态
        assert len(mq.front_monsters) == 2
        assert wm.current_wave == 1
        assert mq.wave == 1
        
        # 模拟战斗：逐个击败怪物
        while mq.front_monsters:
            monster = mq.front_monsters[0]
            mq.check_defeated_and_replace(monster, mock_factory)
        
        # 第一波清理完成
        assert mq.check_wave_clear() == True
        
        # 开始第二波
        mq2 = wm.start_next_wave(mock_factory)
        
        assert wm.current_wave == 2
        assert mq2.wave == 2
        assert len(mq2.front_monsters) == 3
    
    def test_five_monster_max_front(self):
        """测试最大5个前台怪物"""
        # 6个怪物配置
        monsters = [
            MonsterSpawnInfo(name=f"怪物{i}", max_hp=1000)
            for i in range(6)
        ]
        
        wm = WaveManager([monsters])
        mq = wm.start_wave(mock_factory)
        
        # max_front=5，所以只有5个在前台
        assert len(mq.front_monsters) == 5
        assert len(mq.queue_monsters) == 1
        
        # 击败一个后，队列补位
        defeated = mq.front_monsters[0]
        mq.check_defeated_and_replace(defeated, mock_factory)
        
        assert len(mq.front_monsters) == 5
        assert len(mq.queue_monsters) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
