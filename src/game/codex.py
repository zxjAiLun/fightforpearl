"""角色图鉴系统"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CharacterCodexEntry:
    """图鉴条目"""
    id: str
    name: str
    element: str
    path: str  # 命途
    description: str
    stats_summary: str
    skills: list[str] = field(default_factory=list)


class CharacterCodex:
    """角色图鉴管理器"""

    def __init__(self):
        self.discovered: set[str] = set()
        self._entries: dict[str, CharacterCodexEntry] = {}

    def discover(self, character_id: str) -> None:
        """发现角色"""
        self.discovered.add(character_id)

    def is_discovered(self, character_id: str) -> bool:
        """检查角色是否已发现"""
        return character_id in self.discovered

    def get_discovered_count(self) -> int:
        """获取已发现角色数量"""
        return len(self.discovered)

    def add_entry(self, entry: CharacterCodexEntry) -> None:
        """添加图鉴条目"""
        self._entries[entry.id] = entry

    def get_entry(self, character_id: str) -> Optional[CharacterCodexEntry]:
        """获取图鉴条目"""
        return self._entries.get(character_id)

    def get_all_entries(self) -> list[CharacterCodexEntry]:
        """获取所有图鉴条目"""
        return list(self._entries.values())

    def get_discovered_entries(self) -> list[CharacterCodexEntry]:
        """获取已发现的图鉴条目"""
        return [e for e in self._entries.values() if e.id in self.discovered]

    def get_undiscovered_entries(self) -> list[CharacterCodexEntry]:
        """获取未发现的图鉴条目"""
        return [e for e in self._entries.values() if e.id not in self.discovered]

    def discover_from_character(self, char) -> None:
        """从角色对象发现"""
        char_id = self._get_character_id(char)
        self.discover(char_id)

    def _get_character_id(self, char) -> str:
        """从角色对象获取ID"""
        return getattr(char, 'codex_id', char.name.lower().replace(' ', '_'))

    def register_character(
        self,
        character_id: str,
        name: str,
        element: str,
        path: str,
        description: str,
        stats_summary: str,
        skills: list[str] = None,
    ) -> None:
        """注册角色到图鉴"""
        entry = CharacterCodexEntry(
            id=character_id,
            name=name,
            element=element,
            path=path,
            description=description,
            stats_summary=stats_summary,
            skills=skills or [],
        )
        self.add_entry(entry)

    def to_dict(self) -> dict:
        """转换为字典（用于序列化）"""
        return {
            "discovered": list(self.discovered),
            "entries": {
                k: {
                    "id": v.id,
                    "name": v.name,
                    "element": v.element,
                    "path": v.path,
                    "description": v.description,
                    "stats_summary": v.stats_summary,
                    "skills": v.skills,
                }
                for k, v in self._entries.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CharacterCodex":
        """从字典恢复（用于反序列化）"""
        codex = cls()
        codex.discovered = set(data.get("discovered", []))
        entries_data = data.get("entries", {})
        for k, v in entries_data.items():
            entry = CharacterCodexEntry(
                id=v["id"],
                name=v["name"],
                element=v["element"],
                path=v["path"],
                description=v["description"],
                stats_summary=v["stats_summary"],
                skills=v.get("skills", []),
            )
            codex.add_entry(entry)
        return codex


# 全局图鉴实例
_global_codex: Optional[CharacterCodex] = None


def get_codex() -> CharacterCodex:
    """获取全局图鉴实例"""
    global _global_codex
    if _global_codex is None:
        _global_codex = CharacterCodex()
        _init_default_entries(_global_codex)
    return _global_codex


def _init_default_entries(codex: CharacterCodex) -> None:
    """初始化默认图鉴条目"""
    default_characters = [
        {
            "id": "march_7th",
            "name": "三月七",
            "element": "ICE",
            "path": " Preservation",
            "description": "来自仙舟「星槎海」的车厢服务员，擅长使用冰元素进行防御和辅助。",
            "stats_summary": "HP: 高 | ATK: 中 | DEF: 高 | SPD: 中",
            "skills": ["普通攻击", "战技", "终结技", "天赋"],
        },
        {
            "id": "welt",
            "name": "瓦尔特",
            "element": "IMAGINARY",
            "path": " Nihility",
            "description": "前逆萤议会成员，现为列车组顾问，操控虚数属性进行强力输出。",
            "stats_summary": "HP: 中 | ATK: 高 | DEF: 中 | SPD: 中",
            "skills": ["普通攻击", "战技", "终结技", "天赋"],
        },
        {
            "id": "himeko",
            "name": "姬子",
            "element": "FIRE",
            "path": " Erudition",
            "description": "列车领航员，炎元素的强力输出角色，擅长范围攻击。",
            "stats_summary": "HP: 中 | ATK: 高 | DEF: 低 | SPD: 高",
            "skills": ["普通攻击", "战技", "终结技", "天赋"],
        },
        {
            "id": "kafka",
            "name": "卡芙卡",
            "element": "THUNDER",
            "path": " Nihility",
            "description": "逆萤的使者，操控雷元素，擅长触发追加攻击和DOT效果。",
            "stats_summary": "HP: 低 | ATK: 高 | DEF: 低 | SPD: 高",
            "skills": ["普通攻击", "战技", "终结技", "天赋"],
        },
        {
            "id": "silverwolf",
            "name": "银狼",
            "element": "QUANTUM",
            "path": " Nihility",
            "description": "顶级程序员，操控量子元素，擅长弱化敌人和添加debuff。",
            "stats_summary": "HP: 低 | ATK: 中 | DEF: 低 | SPD: 高",
            "skills": ["普通攻击", "战技", "终结技", "天赋"],
        },
        {
            "id": "argenti",
            "name": "银枝",
            "element": "PHYSICAL",
            "path": " Erudition",
            "description": "圣殿骑士团骑士长，物理元素输出，擅长高爆发伤害。",
            "stats_summary": "HP: 高 | ATK: 高 | DEF: 中 | SPD: 低",
            "skills": ["普通攻击", "战技", "终结技", "天赋"],
        },
    ]

    for char in default_characters:
        codex.register_character(
            character_id=char["id"],
            name=char["name"],
            element=char["element"],
            path=char["path"],
            description=char["description"],
            stats_summary=char["stats_summary"],
            skills=char["skills"],
        )
