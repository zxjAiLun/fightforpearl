"""角色创建 TUI — 交互式属性分配"""
from __future__ import annotations

from .character import (
    StatAllocator,
    TOTAL_POINTS,
    STAT_DISPLAY,
    STAT_LIMITS,
    create_character,
    list_presets,
    create_character_from_preset,
)
from .models import Element


ELEMENTS = list(Element)


def _elem_name(e: Element) -> str:
    names = {
        Element.PHYSICAL: "物理",
        Element.WIND: "风",
        Element.THUNDER: "雷",
        Element.FIRE: "火",
        Element.ICE: "冰",
        Element.QUANTUM: "量子",
        Element.IMAGINARY: "虚数",
    }
    return names.get(e, e.name)


def _fmt_stat_line(key: str, base: float, allocated: float) -> str:
    current = base + allocated
    if key in ("crit_rate", "effect_hit", "effect_res"):
        return f"{current:.0%}  (基础 {base:.0%}  分配 {allocated:+.0%})"
    elif key == "crit_dmg":
        return f"{current:.0%}  (基础 {base:.0%}  分配 {allocated:+.0%})"
    else:
        return f"{int(current)}  (基础 {int(base)}  分配 {int(allocated):+d})"


def run_character_creator() -> "Character | None":
    """
    交互式角色创建流程
    返回创建好的 Character 或 None（用户取消）
    """
    print("\n" + "=" * 52)
    print("  ⚔️  Fight for Pearl — 创建角色")
    print("=" * 52)

    print("\n请选择角色创建方式:")
    print("  1. 从预设角色中选择")
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
        elem_zh = _elem_name(Element[p["element"]])
        print(f"  {i}. {p['name']}  [{elem_zh}]")

    idx_str = input(f"\n请选择角色编号 [1-{len(presets)}]: ").strip()
    if not idx_str.isdigit() or not (1 <= int(idx_str) <= len(presets)):
        print("无效选择，默认选择 1。")
        idx_str = "1"

    preset = presets[int(idx_str) - 1]
    char = create_character_from_preset(preset["name"])
    if char is None:
        print("加载预设失败。")
        return None

    print(f"\n已加载：{char.name}  [{_elem_name(char.element)}]")
    print(f"  HP: {char.stat.max_hp}  ATK: {char.stat.atk}  DEF: {char.stat.def_}  SPD: {char.stat.spd}")
    print(f"  暴击率: {char.stat.crit_rate:.0%}  暴击伤害: {char.stat.crit_dmg:.0%}")
    print(f"  效果命中: {char.stat.effect_hit:.0%}  效果抵抗: {char.stat.effect_res:.0%}")

    adjust = input("\n是否调整属性？\n  1. 保持预设属性\n  2. 重新分配属性点（100点自由分配）\n请输入 [1/2] (默认 1): ").strip() or "1"
    if adjust == "2":
        char = _run_stat_allocation(char)
        if char is None:
            return None

    print(f"\n✅ 角色创建成功：{char.name}")
    return char


def _create_custom_flow() -> "Character | None":
    print()
    name = input("请输入角色名: ").strip() or "无名旅者"

    print("\n【选择元素】")
    for i, elem in enumerate(ELEMENTS, 1):
        print(f"  {i}. {_elem_name(elem)}")

    idx_str = input(f"\n请输入元素编号 [1-{len(ELEMENTS)}]: ").strip()
    if not idx_str.isdigit() or not (1 <= int(idx_str) <= len(ELEMENTS)):
        print("无效选择，默认选择 1 (物理)。")
        idx_str = "1"
    element = ELEMENTS[int(idx_str) - 1]

    print(f"\n已选择：{name}  [{_elem_name(element)}]")
    print("接下来进入属性分配环节...")

    # 基础模板属性（全 0）
    from .models import Stat
    base_stat = Stat()
    char = create_character(name, element, base_stat)

    return _run_stat_allocation(char)


def _run_stat_allocation(char: "Character") -> "Character | None":
    """交互式属性分配流程"""
    allocator = StatAllocator(total_points=TOTAL_POINTS)
    allocator.set_base_stat(char.stat)

    while True:
        print("\n" + "-" * 52)
        print(f"【属性分配】  剩余点数: {allocator.remaining_points()}  /  {TOTAL_POINTS}")
        print("-" * 52)

        for i, (key, display) in enumerate(STAT_DISPLAY, 1):
            base = allocator.base_stat.get(key, 0)
            allocated = allocator.allocated[key]
            print(f"  {i}. {display:<10} {_fmt_stat_line(key, base, allocated)}")

        print()
        print("操作说明:")
        print("  1-8   : 为对应属性分配 1 点（百分比属性分配 1%）")
        print("  +1-8  : 为对应属性分配 10 点（百分比属性分配 10%）")
        print("  -1-8  : 从对应属性减少 1 点")
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
            stat = allocator.get_final_stat()
            return create_character(char.name, char.element, stat)

        if cmd == "r":
            for k in allocator.allocated:
                allocator.allocated[k] = 0
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
            if 0 <= idx < len(STAT_DISPLAY):
                key = STAT_DISPLAY[idx][0]
                actual_delta = delta / 100.0 if key in ("crit_rate", "crit_dmg", "effect_hit", "effect_res") else float(delta)
                if not allocator.allocate(key, actual_delta):
                    print(f"  无法分配！剩余点数不足，或已达属性上限。")
            else:
                print("无效的属性编号。")
        else:
            print("未知命令，请重试。")


def main():
    char = run_character_creator()
    if char:
        print(f"\n最终角色属性:")
        print(f"  名字: {char.name}")
        print(f"  元素: {_elem_name(char.element)}")
        print(f"  HP: {char.stat.max_hp}")
        print(f"  ATK: {char.stat.atk}")
        print(f"  DEF: {char.stat.def_}")
        print(f"  SPD: {char.stat.spd}")
        print(f"  暴击率: {char.stat.crit_rate:.0%}")
        print(f"  暴击伤害: {char.stat.crit_dmg:.0%}")
        print(f"  效果命中: {char.stat.effect_hit:.0%}")
        print(f"  效果抵抗: {char.stat.effect_res:.0%}")
    else:
        print("角色创建已取消。")


if __name__ == "__main__":
    main()
