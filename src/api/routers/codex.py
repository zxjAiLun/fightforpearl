"""图鉴 API"""
import json
import os
from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter(prefix="/api/codex", tags=["codex"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def _load_lightcones():
    """加载所有光锥数据"""
    lightcones_dir = DATA_DIR / "lightcones"
    results = []
    for f in sorted(lightcones_dir.glob("*.json")):
        with open(f, encoding="utf-8") as fp:
            results.append(json.load(fp))
    return results


def _load_characters():
    """加载角色基础数据"""
    with open(DATA_DIR / "characters.json", encoding="utf-8") as f:
        return json.load(f)


def _load_skills():
    """加载角色技能数据"""
    with open(DATA_DIR / "skills.json", encoding="utf-8") as f:
        return json.load(f)


@router.get("/lightcones")
def list_lightcones():
    """返回所有光锥数据"""
    return _load_lightcones()


@router.get("/lightcones/paths")
def list_lightcone_paths():
    """返回所有命途分类"""
    lightcones = _load_lightcones()
    paths = sorted(set(lc.get("path", "未知") for lc in lightcones))
    return paths


@router.get("/lightcones/{lc_id}")
def get_lightcone(lc_id: int):
    """返回指定光锥数据"""
    lightcones = _load_lightcones()
    for lc in lightcones:
        if lc.get("id") == lc_id:
            return lc
    raise HTTPException(status_code=404, detail="光锥不存在")


@router.get("/characters")
def list_characters():
    """返回所有角色数据（带技能）"""
    characters = _load_characters()
    skills_map = {s["character"]: s["skills"] for s in _load_skills()}
    
    result = []
    for char in characters:
        entry = dict(char)
        entry["skills"] = skills_map.get(char["name"], [])
        result.append(entry)
    return result


@router.get("/characters/{name}")
def get_character(name: str):
    """返回指定角色数据"""
    characters = _load_characters()
    skills_map = {s["character"]: s["skills"] for s in _load_skills()}
    
    for char in characters:
        if char["name"] == name:
            entry = dict(char)
            entry["skills"] = skills_map.get(name, [])
            return entry
    raise HTTPException(status_code=404, detail="角色不存在")
