"""模拟宇宙 TUI 界面 - 抽卡版"""
from .cards import CardType


def show_universe_menu(su: "SimulatedUniverse"):
    """显示宇宙菜单"""
    while True:
        state = su.get_current_state()

        if state.get("is_complete") or state.get("is_failed"):
            print(f"\n=== 运行{'完成' if state.get('is_complete') else '失败'} ===")
            print(f"到达层数: {state.get('floor', 0)}")
            break

        print(f"\n=== 模拟宇宙 - {state.get('map_progress', '0/8')} ===")
        print(f"信用点: {state.get('credits', 0)}")
        print(f"祝福: {len(state.get('blessings', []))}")
        print(f"奇物: {len(state.get('curios', []))}")
        print(f"方程: {len(state.get('equations', []))}")

        deck_status = state.get("deck_status", {})
        print(f"牌堆: 抽牌堆 {deck_status.get('draw_pile', 0)} | 弃牌堆 {deck_status.get('discard_pile', 0)}")

        # 抽3张手牌
        print("\n--- 抽卡阶段 ---")
        draw_result = su.draw_hand()
        if "error" in draw_result:
            print(f"抽卡失败: {draw_result['error']}")
            break

        hand_info = draw_result.get("cards", [])
        print("\n你的手牌：")
        for card in hand_info:
            rarity_str = "★" * card.get("rarity", 1)
            print(f"  [{card['index']}] {rarity_str} {card['name']} - {card['description']}")

        # 玩家选择打出的卡牌
        try:
            choice = int(input("\n请选择要打出的卡牌编号: "))
            if choice < 0 or choice >= len(hand_info):
                print("无效选择，跳过")
                continue
        except ValueError:
            print("无效输入")
            continue

        # 打出卡牌
        result = su.play_card(choice)
        if "error" in result:
            print(f"打出卡牌失败: {result['error']}")
            continue

        print(f"\n>>> 打出: {result.get('card_played')}")
        print(f">>> {result.get('description')}")

        action = result.get("action")

        if action == "battle":
            print(f">>> 进入战斗！敌人: {result.get('enemies')}")
            # TODO: 调用战斗系统
            input("按回车继续...")
        elif action == "boss_battle":
            print(f">>> 进入首领战！敌人: {result.get('enemies')}")
            # TODO: 调用战斗系统
            input("按回车继续（首领战胜后运行完成）...")
            su.complete_battle(victory=True)
            su.complete_run(victory=True)
        elif action == "choose_blessing":
            print("\n选择一份祝福：")
            for opt in result.get("options", []):
                print(f"  [{opt['index']}] {opt['name']} ({opt['path']}) - {opt['description']}")
            try:
                blessing_choice = int(input("请选择: "))
                br = su.choose_blessing(blessing_choice)
                print(f">>> 获得祝福：{br.get('chosen')} - {br.get('description')}")
                if br.get("new_equations"):
                    print(f">>> 激活方程：{br.get('new_equations')}")
            except (ValueError, IndexError):
                print("无效选择")
        elif action == "choose_curio":
            print("\n选择一件奇物：")
            for opt in result.get("options", []):
                print(f"  [{opt['index']}] {opt['name']} - {opt['description']}")
            try:
                curio_choice = int(input("请选择: "))
                cr = su.choose_curio(curio_choice)
                print(f">>> 获得奇物：{cr.get('chosen')} - {cr.get('description')}")
            except (ValueError, IndexError):
                print("无效选择")
        elif action == "reward":
            print(f">>> 获得 {result.get('credits')} 信用点！")
        elif action == "shop":
            print(">>> 商店功能开发中...")
        elif action == "mystery":
            print(f">>> {result.get('result')}")
        elif action == "rest":
            print(f">>> {result.get('heal')}")
        else:
            print(f">>> 事件已处理")
