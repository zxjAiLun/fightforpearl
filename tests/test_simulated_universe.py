"""模拟宇宙测试"""
import pytest

from src.game.simulated_universe import (
    SimulatedUniverse,
    UniverseRun,
    UniverseMap,
    MapNode,
    EventType,
    UniverseEvent,
    Blessing,
    BLESSING_POOL,
    PathType,
    Curio,
    CURIO_POOL,
    Equation,
    EQUATION_POOL,
    CardDeck,
    CardType,
    UniverseCard,
    INITIAL_CARD_POOL,
)
from src.game.simulated_universe.blessings import get_random_blessings


class TestCardDeck:
    """卡牌堆叠测试"""

    def test_deck_creation(self):
        """测试卡牌堆创建"""
        deck = CardDeck(difficulty=1)
        total = sum(INITIAL_CARD_POOL.values())
        assert len(deck.draw_pile) == total
        assert len(deck.discard_pile) == 0
        assert len(deck.hand) == 0

    def test_draw_cards(self):
        """测试抽卡"""
        deck = CardDeck()
        drawn = deck.draw_cards(3)
        assert len(drawn) == 3
        assert len(deck.hand) == 3
        assert len(deck.draw_pile) == sum(INITIAL_CARD_POOL.values()) - 3

    def test_play_card(self):
        """测试打出卡牌"""
        deck = CardDeck()
        deck.draw_cards(3)
        card_to_play = deck.hand[0]
        played = deck.play_card(card_to_play)
        assert played is not None
        assert len(deck.hand) == 0  # 手牌已清空
        # 未选的两张进入弃牌堆，打出的卡进入 current_card（在 run 中处理）
        assert len(deck.discard_pile) == 2

    def test_reshuffle(self):
        """测试洗牌"""
        deck = CardDeck()
        deck.draw_cards(3)
        deck.discard_hand()  # 先弃掉手牌
        assert len(deck.discard_pile) == 3
        assert len(deck.draw_pile) == sum(INITIAL_CARD_POOL.values()) - 3  # 33
        deck.reshuffle_discard()
        # 洗牌后所有卡回到抽牌堆
        assert len(deck.draw_pile) == sum(INITIAL_CARD_POOL.values())
        assert len(deck.discard_pile) == 0

    def test_boss_card_limited(self):
        """测试Boss卡只能抽一次"""
        deck = CardDeck()
        # 找到Boss卡并抽出
        boss_count = INITIAL_CARD_POOL[CardType.BOSS]
        assert boss_count == 1
        # 抽很多次确保Boss被抽到
        for _ in range(50):
            deck.draw_cards(3)
            deck.discard_hand()
        # Boss卡应该已使用
        assert deck.boss_card_used is True

    def test_get_hand_info(self):
        """测试获取手牌信息"""
        deck = CardDeck()
        deck.draw_cards(3)
        info = deck.get_hand_info()
        assert len(info) == 3
        assert "name" in info[0]
        assert "type" in info[0]
        assert "rarity" in info[0]


class TestUniverseCard:
    """卡牌测试"""

    def test_card_to_event(self):
        """测试卡牌转事件"""
        card = UniverseCard(
            id="test_1",
            name="测试战斗",
            card_type=CardType.BATTLE,
            description="测试",
            enemies=["enemy_1"],
            rarity=1,
        )
        event = card.to_event()
        assert event.name == "测试战斗"
        assert event.type == EventType.BATTLE
        assert event.enemies == ["enemy_1"]


class TestUniverseMap:
    """地图生成测试"""

    def test_map_generation(self):
        """测试地图生成"""
        m = UniverseMap(difficulty=1)
        assert m.WIDTH == 5
        assert m.HEIGHT == 8
        assert len(m.nodes) == 8
        assert len(m.nodes[0]) == 5

    def test_map_connections(self):
        """测试地图节点连接"""
        m = UniverseMap()
        assert m.start_node.y == 0
        assert m.end_node.y == 7
        assert len(m.start_node.connections) >= 1


class TestUniverseEvent:
    """事件测试"""

    def test_event_types(self):
        """测试事件类型枚举"""
        assert EventType.BATTLE.value == "battle"
        assert EventType.BOSS.value == "boss"
        assert EventType.BLESSING.value == "blessing"

    def test_universe_event_creation(self):
        """测试事件创建"""
        e = UniverseEvent(
            name="测试战斗",
            type=EventType.BATTLE,
            description="测试描述",
            enemies=["enemy_1"],
            difficulty=2,
        )
        assert e.name == "测试战斗"
        assert e.type == EventType.BATTLE


class TestBlessings:
    """祝福系统测试"""

    def test_blessing_pool_not_empty(self):
        """测试祝福池非空"""
        assert len(BLESSING_POOL) > 0

    def test_get_random_blessings(self):
        """测试获取随机祝福"""
        blessings = get_random_blessings(3)
        assert len(blessings) == 3
        assert all(isinstance(b, Blessing) for b in blessings)

    def test_path_types(self):
        """测试命途类型"""
        assert PathType.WARRIOR.value == "warrior"
        assert PathType.QUANTUM.value == "quantum"


class TestCurios:
    """奇物系统测试"""

    def test_curio_pool_not_empty(self):
        """测试奇物池非空"""
        assert len(CURIO_POOL) > 0

    def test_curio_credit_bonus(self):
        """测试奇物信用点加成"""
        treasure_box = CURIO_POOL["curio_treasure_box"]
        assert treasure_box.credit_bonus == 0.20


class TestEquations:
    """方程系统测试"""

    def test_equation_pool_not_empty(self):
        """测试方程池非空"""
        assert len(EQUATION_POOL) > 0

    def test_equation_can_activate(self):
        """测试方程激活条件检查"""
        eq = EQUATION_POOL["eq_warrior"]
        assert eq.required_blessings == {PathType.WARRIOR: 3}
        assert eq.can_activate({PathType.WARRIOR: 2}) is False
        assert eq.can_activate({PathType.WARRIOR: 3}) is True


class TestSimulatedUniverse:
    """模拟宇宙核心测试"""

    def test_create_universe(self):
        """测试创建模拟宇宙"""
        su = SimulatedUniverse(difficulty=1)
        assert su.difficulty == 1
        assert su.current_run is None

    def test_start_new_run(self):
        """测试开始新运行"""
        su = SimulatedUniverse()
        run = su.start_new_run()
        assert run is not None
        assert run.card_deck is not None
        assert run.current_floor == 1
        assert run.credits == 0
        assert len(run.blessings) == 0

    def test_get_current_state(self):
        """测试获取当前状态"""
        su = SimulatedUniverse()
        su.start_new_run()
        state = su.get_current_state()
        assert "floor" in state
        assert "credits" in state
        assert "deck_status" in state
        assert state["floor"] == 1

    def test_draw_hand(self):
        """测试抽卡"""
        su = SimulatedUniverse()
        su.start_new_run()
        result = su.draw_hand()
        assert "cards" in result
        assert len(result["cards"]) == 3

    def test_play_card(self):
        """测试打出卡牌"""
        su = SimulatedUniverse()
        su.start_new_run()
        # 先抽卡
        draw_result = su.draw_hand()
        assert len(draw_result["cards"]) == 3
        # 打出第一张
        play_result = su.play_card(0)
        assert "card_played" in play_result
        assert "action" in play_result

    def test_blessing_selection_flow(self):
        """测试祝福选择流程"""
        su = SimulatedUniverse()
        su.start_new_run()

        # 一直抽卡直到抽到祝福卡
        for _ in range(50):
            draw_result = su.draw_hand()
            if not draw_result.get("cards"):
                break
            # 找祝福卡
            blessing_card = None
            for card in draw_result["cards"]:
                if card["type"] == "blessing":
                    blessing_card = card
                    break
            if blessing_card:
                play_result = su.play_card(blessing_card["index"])
                if play_result.get("action") == "choose_blessing":
                    assert len(play_result["options"]) == 3
                    # 选择祝福
                    br = su.choose_blessing(0)
                    assert "chosen" in br
                    return
        # 如果没找到祝福卡，重置继续
        pytest.skip("未能抽到祝福卡（随机性）")

    def test_run_not_complete_initially(self):
        """测试运行初始状态未完成"""
        su = SimulatedUniverse()
        su.start_new_run()
        state = su.get_current_state()
        assert state.get("is_complete") is False
        assert state.get("is_failed") is False

    def test_complete_run(self):
        """测试完成运行"""
        su = SimulatedUniverse()
        su.start_new_run()
        su.complete_run(victory=True)
        state = su.get_current_state()
        assert state.get("is_complete") is True


class TestUniverseRun:
    """运行状态测试"""

    def test_init_deck(self):
        """测试初始化卡牌堆"""
        run = UniverseRun()
        assert run.card_deck is None
        run.init_deck(difficulty=1)
        assert run.card_deck is not None
        assert run.card_deck.difficulty == 1

    def test_add_blessing(self):
        """测试添加祝福"""
        run = UniverseRun()
        run.init_deck()
        blessings = get_random_blessings(1)
        run.add_blessing(blessings[0])
        assert len(run.blessings) == 1
        assert len(run.active_blessing_ids) == 1

    def test_add_curio(self):
        """测试添加奇物"""
        run = UniverseRun()
        run.init_deck()
        curio = list(CURIO_POOL.values())[0]
        run.add_curio(curio)
        assert len(run.curios) == 1

    def test_get_blessing_counts(self):
        """测试祝福计数"""
        run = UniverseRun()
        run.init_deck()
        blessing = BLESSING_POOL["path_warrior"]
        run.add_blessing(blessing)
        run.add_blessing(BLESSING_POOL["path_warrior_2"])
        counts = run.get_blessing_counts()
        assert counts[PathType.WARRIOR] == 2

    def test_add_credits_with_curio_bonus(self):
        """测试带奇物加成的信用点"""
        run = UniverseRun()
        run.init_deck()
        treasure_box = CURIO_POOL["curio_treasure_box"]
        run.add_curio(treasure_box)
        initial = run.credits
        run.add_credits(100)
        assert run.credits == initial + 120

    def test_advance_floor(self):
        """测试进入下一层"""
        run = UniverseRun()
        run.init_deck()
        assert run.current_floor == 1
        run.advance_floor()
        assert run.current_floor == 2

    def test_is_boss_floor(self):
        """测试是否Boss层"""
        run = UniverseRun()
        run.init_deck()
        run.current_floor = 8  # Boss层（第8层）
        assert run.is_boss_floor() is True
        run.current_floor = 7  # 非Boss层
        assert run.is_boss_floor() is False
