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
    except:
        return None

def clean_effect(desc, params):
    """Replace #N[i] and #N[f1] placeholders with actual values."""
    if not params:
        return desc
    for i, p in enumerate(params, 1):
        val = float(p)
        if f'#{i}[i]' in desc:
            # [i]: if value is a decimal (< 10), multiply by 100 for percentage display
            # if value is already an integer, keep as-is
            if val != int(val) and val < 10:
                desc = desc.replace(f'#{i}[i]', str(int(val * 100)))
            else:
                desc = desc.replace(f'#{i}[i]', str(int(val)))
        if f'#{i}[f1]' in desc:
            # [f1]: multiply by 100, display as float with 1 decimal
            desc = desc.replace(f'#{i}[f1]', str(round(val * 100, 1)))
    return desc

def parse_lightcone(html, lightcone_id):
    if not html or len(html) < 500:
        return None

    result = {"id": lightcone_id, "name": None, "path": None, "stats": {}, "effect": None}

    # 1. Name from window.PAGE_CONFIG
    m = re.search(r'window\.PAGE_CONFIG=\{"name":"([^"]+)"', html)
    if m:
        result["name"] = m.group(1)

    # 2. Path from baseType.name
    m = re.search(r'"baseType":\{"id":\d+,"iconPath":"[^"]+","color":"[^"]*","name":"([^"]+)"', html)
    if m:
        result["path"] = m.group(1)

    # 3. Stats from levelData[0] block
    ld_start = html.find('"levelData"')
    ld_end = html.find('}],"skill"', ld_start) if ld_start > 0 else -1
    if ld_start > 0 and ld_end > ld_start:
        block = html[ld_start:ld_end + 3]
        atk_m = re.search(r'"attackBase":([0-9.]+)', block)
        hp_m = re.search(r'"hpBase":([0-9.]+)', block)
        def_m = re.search(r'"defenseBase":([0-9.]+)', block)
        if atk_m and hp_m and def_m:
            result["stats"] = {
                "hp": int(round(float(hp_m.group(1)))),
                "atk": int(round(float(atk_m.group(1)))),
                "def": int(round(float(def_m.group(1))))
            }

    # 4. Effect from skill.descHash with param substitution
    sk_start = html.find('"skill":{')
    sk_end = html.find('},"calculator"', sk_start) if sk_start > 0 else -1
    if sk_start > 0 and sk_end > sk_start:
        block = html[sk_start:sk_end]
        # descHash
        dm = re.search(r'"descHash":"(.+?)","levelData"', block, re.DOTALL)
        # params from skill block
        pm = re.search(r'"params":\[([^\]]+)\]', block)
        params = [float(x) for x in pm.group(1).split(',')] if pm else []
        if dm:
            desc = dm.group(1)
            # Remove HTML tags
            desc = re.sub(r'<br\s*/?>', '\n', desc)
            desc = re.sub(r'<[^>]+>', '', desc)
            desc = re.sub(r'\n+', '\n', desc).strip()
            # Replace placeholders
            desc = clean_effect(desc, params)
            result["effect"] = desc

    return result if result["name"] else None

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
            if data and data.get("name"):
                out_path = DATA_DIR / f"{cid}.json"
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                hp = data["stats"].get("hp", "?")
                atk = data["stats"].get("atk", "?")
                df = data["stats"].get("def", "?")
                print(f"OK -> {data['name']} | {data['path']} | HP:{hp} ATK:{atk} DEF:{df}")
                results.append(data)
                empty_count = 0
            else:
                print("PARSE FAILED")
                empty_count += 1

        if empty_count >= 5:
            print(f"[{series_name}] 5 consecutive failures, stopping.")
            break

        time.sleep(0.3)

    return results

print("=" * 60)
print("Scraping 23000 series (23001-23100)")
print("=" * 60)
results_23000 = scrape_range(23001, 23100, "23000")

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
