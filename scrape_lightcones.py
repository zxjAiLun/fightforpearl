import json
import re
import time
from pathlib import Path

BASE_URL = "https://starrailstation.com/cn/lightcone/{}"

def fetch_page(lightcone_id):
    import urllib.request
    url = BASE_URL.format(lightcone_id)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        return None

def parse_lightcone(html, lightcone_id):
    if not html or len(html) < 100:
        return None
    
    # Try to extract name
    name = None
    name_patterns = [
        r'"name"\s*:\s*"([^"]+)"',
        r'<h1[^>]*>([^<]+)</h1>',
        r'class="name"[^>]*>([^<]+)<',
        r'class="lightcone-name"[^>]*>([^<]+)<',
    ]
    for pat in name_patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            break
    
    # Try to extract path
    path = None
    path_patterns = [
        r'"path"\s*:\s*"([^"]+)"',
        r'"pathType"\s*:\s*"([^"]+)"',
        r'Path[^>]*>([^<]+)<',
        r'属性[^>]*>([^<]+)<',
    ]
    for pat in path_patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            path = m.group(1).strip()
            break
    
    # Try to extract stats
    stats = {}
    hp_m = re.search(r'"hp"\s*:\s*(\d+)', html)
    atk_m = re.search(r'"atk"\s*:\s*(\d+)', html)
    def_m = re.search(r'"def"\s*:\s*(\d+)', html)
    if hp_m: stats['hp'] = int(hp_m.group(1))
    if atk_m: stats['atk'] = int(atk_m.group(1))
    if def_m: stats['def'] = int(def_m.group(1))
    
    # Try to extract effect
    effect = None
    effect_patterns = [
        r'"effect"\s*:\s*"([^"]+)"',
        r'"description"\s*:\s*"([^"]+)"',
        r'效果[^>]*>([^<]+)<',
    ]
    for pat in effect_patterns:
        m = re.search(pat, html, re.DOTALL)
        if m:
            effect = m.group(1).strip()
            break
    
    if not name:
        return None
    
    return {
        "id": lightcone_id,
        "name": name,
        "path": path,
        "stats": stats,
        "effect": effect
    }

def scrape_range(start, end, series_name):
    results = []
    empty_count = 0
    data_dir = Path("/home/ubuntu/.openclaw/workspace/fightforpearl/data/lightcones")
    
    for cid in range(start, end + 1):
        print(f"[{series_name}] Checking ID {cid}...", end=" ")
        html = fetch_page(cid)
        
        if html is None or len(html) < 200:
            print("FAILED (network error)")
            empty_count += 1
        else:
            data = parse_lightcone(html, cid)
            if data and data.get('name'):
                out_path = data_dir / f"{cid}.json"
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"OK -> {data['name']}")
                results.append(data)
                empty_count = 0
            else:
                print("EMPTY (no valid data)")
                empty_count += 1
        
        if empty_count >= 5:
            print(f"[{series_name}] 5 consecutive empty pages, stopping.")
            break
        
        time.sleep(0.5)
    
    return results

# Run 23000 series
print("=" * 50)
print("Scraping 23000 series (23001-23100)")
print("=" * 50)
results_23000 = scrape_range(23001, 23100, "23000")

# Run 24000 series
print("\n" + "=" * 50)
print("Scraping 24000 series (24001-24100)")
print("=" * 50)
results_24000 = scrape_range(24001, 24100, "24000")

total = len(results_23000) + len(results_24000)
print(f"\n{'=' * 50}")
print(f"SCRAPING COMPLETE")
print(f"23000 series: {len(results_23000)} lightcones")
print(f"24000 series: {len(results_24000)} lightcones")
print(f"Total: {total} lightcones")
print(f"{'=' * 50}")
