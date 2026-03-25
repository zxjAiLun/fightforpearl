"""角色创建 TUI — 交互式属性分配（简化版）"""
from __future__ import annotations

from .character import (
    StatAllocator,
    create_character_from_preset,
    create_custom_character,
    list_presets,
)
from .models import Element, Stat


ELEMENT_NAMES = {
    Element.PHYSICAL: "物理",
    Element.WIND: "风",
    Element.THUNDER: "雷",
    Element.FIRE: "火",
    Element.ICE: "冰",
    Element.QUANTUM: "量子",
    Element.IMAGINARY: "虚数",
}


def _elem_name(e: Element) -> str:
    return ELEMENT_NAMES.get(e, e.name)


def run_character_creator() -> "Character | None":
    """
    交互式角色创建流程
    返回创建好的 Character 或 None（用户取消）
    """
    print("\n" + "=" * 52)
    print("  ⚔️  Fight for Pearl — 创建角色")
    print("=" * 52)

    print("\n请选择角色创建方式:")
    print("  1. 从预设角色中选择（推荐）")
    print("  2. 手动创建（输入名字 + 选择元素 + 分配属性）")

    choice = input("\n请输入选项 [1/2] (默认 1): ").strip() or "1"

    if choice == "1":
        return _create_from_preset_flow()
    else:
        return _create_custom_flow()


def _create_from_preset_flow() -> "Character | None":
    presets = list_presets()
    print("\n【预设角色列表】")
    for i, p in enumerate(presets, 1):
        elem_zh = _elem_name(Element[p]["element"] if isinstance(p, str) else p["element"])
        print(f"  {i}. {p}  [{elem_zh}]")

    idx_str = input(f"\n请选择角色编号 [1-{len(presets)}]: ").strip() or "1"
    if not idx_str.isdigit() or not (1 <= int(idx_str) <= len(presets)):
        print("无效选择，默认选择 1。")
        idx_str = "1"

    name = presets[int(idx_str) - 1]
    char = create_character_from_preset(name)

    print(f"\n已加载：{char.name}  [{_elem_name(char.element)}]")
    _print_stat(char)

    print(f"\n✅ 角色创建成功：{char.name}")
    return char


def _create_custom_flow() -> "Character | None":
    print()
    name = input("请输入角色名: ").strip() or "无名旅者"

    print("\n【选择元素】")
    elements = list(Element)
    for i, elem in enumerate(elements, 1):
        print(f"  {i}. {_elem_name(elem)}")

    idx_str = input(f"\n请输入元素编号 [1-{len(elements)}]: ").strip() or "1"
    if not idx_str.isdigit() or not (1 <= int(idx_str) <= len(elements)):
        idx_str = "1"
    element = elements[int(idx_str) - 1]

    print(f"\n已选择：{name}  [{_elem_name(element)}]")
    print("接下来进入属性分配环节...")

    # 基础模板（全 0）
    base_stat = Stat()
    char = create_custom_character(name, element, base_stat)

    return _run_stat_allocation(char)


def _run_stat_allocation(char: "Character") -> "Character | None":
    """交互式属性分配流程"""
    allocator = StatAllocator()

    while True:
        print("\n" + "-" * 52)
        print(f"【属性分配】  剩余点数: {allocator.remaining}  /  {allocator.TOTAL_POINTS}")
        print("-" * 52)

        stat_names = [
            ("max_hp", "生命值 HP"),
            ("atk", "攻击力 ATK"),
            ("def", "防御力 DEF"),
            ("spd", "速度 SPD"),
        ]
        for i, (key, display) in enumerate(stat_names, 1):
            base = getattr(char.stat, f"base_{key}" if key != "def" else "base_def")
            allocated = allocator.points.get(key, 0)
            current = base + allocated
            print(f"  {i}. {display:<12} {current:>6}  (基础 {base:>5}  分配 {allocated:>+5})")

        print()
        print("操作说明:")
        print("  1-4   : 为对应属性 +1 点")
        print("  +1-4  : 为对应属性 +10 点")
        print("  -1-4  : 为对应属性 -1 点")
        print("  r     : 重置所有分配")
        print("  c     : 确认并创建角色")
        print("  q     : 取消创建")

        cmd = input("\n请输入命令: ").strip().lower()
        if not cmd:
            continue

        if cmd == "q":
            print("已取消创建。")
            return None

        if cmd == "c":
            base = {
                "max_hp": char.stat.base_max_hp,
                "atk": char.stat.base_atk,
                "def": char.stat.base_def,
                "spd": char.stat.base_spd,
            }
            stat = allocator.get_final_stat(base)
            return create_custom_character(char.name, char.element, stat)

        if cmd == "r":
            allocator.reset()
            print("已重置所有分配。")
            continue

        # 解析 +/-N 命令
        delta = 1
        if cmd.startswith("+"):
            delta = 10
            cmd = cmd[1:]
        elif cmd.startswith("-"):
            delta = -1
            cmd = cmd[1:]

        if cmd.isdigit():
            idx = int(cmd) - 1
            keys = ["max_hp", "atk", "def", "spd"]
            if 0 <= idx < len(keys):
                key = keys[idx]
                if delta > 0:
                    allocator.add(key, delta)
                else:
                    # 不支持减少，只支持增加和重置
                    print("  只支持增加属性，请使用 r 重置后重新分配。")
            else:
                print("无效的属性编号。")
        else:
            print("未知命令，请重试。")


def _print_stat(char: "Character") -> None:
    s = char.stat
    print(f"  HP: {s.base_max_hp}  ATK: {s.base_atk}  DEF: {s.base_def}  SPD: {s.base_spd}")
    print(f"  暴击率: {s.crit_rate:.0%}  暴击伤害: {s.crit_dmg:.0%}")


def main():
    char = run_character_creator()
    if char:
        print(f"\n最终角色属性:")
        print(f"  名字: {char.name}")
        print(f"  元素: {_elem_name(char.element)}")
        s = char.stat
        print(f"  HP: {s.base_max_hp}  ATK: {s.base_atk}  DEF: {s.base_def}  SPD: {s.base_spd}")
        print(f"  暴击率: {s.crit_rate:.0%}  暴击伤害: {s.crit_dmg:.0%}")
    else:
        print("角色创建已取消。")


if __name__ == "__main__":
    main()
