import json
import re
import time
import urllib.request
from pathlib import Path

DATA_DIR = Path("/home/ubuntu/.openclaw/workspace/fightforpearl/data/lightcones")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_html(lightcone_id):
    url = f"https://starrailstation.com/cn/lightcone/{lightcone_id}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        return None

def parse_lightcone(html, lightcone_id):
    if not html or len(html) < 500:
        return None

    result = {
        "id": lightcone_id,
        "name": None,
        "path": None,
        "stats": {},
        "effect": None
    }

    # 1. Extract name from window.PAGE_CONFIG
    m = re.search(r'window\.PAGE_CONFIG=\{"name":"([^"]+)"', html)
    if m:
        result["name"] = m.group(1)

    # 2. Extract baseType.name (the path, e.g. "存护", "巡猎", etc.)
    # The lightcone's baseType block appears near the start of the page data
    # Pattern: "baseType":{"id":0,"iconPath":"...","color":"...","name":"存护"...
    m = re.search(r'"baseType":\{"id":\d+,"iconPath":"[^"]+","color":"[^"]*","name":"([^"]+)"', html)
    if m:
        result["path"] = m.group(1)

    # 3. Extract base stats from levelData[0] (promotion 0, level 1)
    # Use levelData block separately to avoid field collision with materials
    ld_start = html.find('"levelData"')
    ld_end = html.find('}],"skill"', ld_start)
    if ld_start > 0 and ld_end > ld_start:
        level_data_block = html[ld_start:ld_end + 3]
        atk_m = re.search(r'"attackBase":([0-9.]+)', level_data_block)
        hp_m = re.search(r'"hpBase":([0-9.]+)', level_data_block)
        def_m = re.search(r'"defenseBase":([0-9.]+)', level_data_block)
        if atk_m and hp_m and def_m:
            result["stats"] = {
                "hp": int(round(float(hp_m.group(1)))),
                "atk": int(round(float(atk_m.group(1)))),
                "def": int(round(float(def_m.group(1))))
            }

    # 4. Extract skill description from skill.descHash
    # "skill":{"id":23023,"name":"全下","descHash":"使装备者的防御力提高...
    m = re.search(r'"skill":\{"id":\d+,"name":"([^"]+)","descHash":"(.+?)","levelData"', html, re.DOTALL)
    if m:
        skill_name = m.group(1)
        desc_raw = m.group(2)
        # Clean HTML tags: <span...>, <nobr>, </span>, </nobr>, <br />
        desc_clean = re.sub(r'<br\s*/?>', '\n', desc_raw)
        desc_clean = re.sub(r'<[^>]+>', '', desc_clean)
        desc_clean = re.sub(r'\n+', '\n', desc_clean).strip()
        # Also replace #1[i], #2[i], #1[f1] etc with param values
        # params are like [0.4, 0.4, 2, 1, 0.1, 2]
        params_m = re.search(r'"params":\[([^\]]+)\]', html)
        if params_m:
            params = [float(x) for x in params_m.group(1).split(',')]
            for i, p in enumerate(params, 1):
                if p == int(p):
                    desc_clean = desc_clean.replace(f'#{i}[i]', str(int(p)))
                    desc_clean = desc_clean.replace(f'#{i}[f1]', str(int(p * 100)))
                else:
                    desc_clean = desc_clean.replace(f'#{i}[i]', str(p))
                    desc_clean = desc_clean.replace(f'#{i}[f1]', str(round(p * 100, 1)))
        
        result["effect"] = desc_clean

    if not result["name"]:
        return None

    return result

def scrape_range(start, end, series_name):
    results = []
    empty_count = 0

    for cid in range(start, end + 1):
        print(f"[{series_name}] ID {cid}...", end=" ", flush=True)
        html = fetch_html(cid)

        if not html:
            print("NETWORK ERROR")
            empty_count += 1
        else:
            data = parse_lightcone(html, cid)
            if data and data.get('name'):
                out_path = DATA_DIR / f"{cid}.json"
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                hp = data['stats'].get('hp', '?')
                atk = data['stats'].get('atk', '?')
                df = data['stats'].get('def', '?')
                print(f"OK -> {data['name']} | {data['path']} | HP:{hp} ATK:{atk} DEF:{df}")
                results.append(data)
                empty_count = 0
            else:
                print("PARSE FAILED (no name extracted)")
                empty_count += 1

        if empty_count >= 5:
            print(f"[{series_name}] 5 consecutive failures, stopping.")
            break

        time.sleep(0.3)

    return results

# Run 23000 series
print("=" * 60)
print("Scraping 23000 series (23001-23100)")
print("=" * 60)
results_23000 = scrape_range(23001, 23100, "23000")

# Run 24000 series
print("\n" + "=" * 60)
print("Scraping 24000 series (24001-24100)")
print("=" * 60)
results_24000 = scrape_range(24001, 24100, "24000")

total = len(results_23000) + len(results_24000)
print(f"\n{'=' * 60}")
print(f"SCRAPING COMPLETE")
print(f"23000 series: {len(results_23000)} lightcones")
print(f"24000 series: {len(results_24000)} lightcones")
print(f"Total: {total} lightcones")
print(f"{'=' * 60}")
