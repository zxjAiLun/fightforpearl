import json
import re
import time
import subprocess
from pathlib import Path

DATA_DIR = Path("/home/ubuntu/.openclaw/workspace/fightforpearl/data/lightcones")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_markdown(lightcone_id):
    """Use web_fetch to get rendered content."""
    url = f"https://starrailstation.com/cn/lightcone/{lightcone_id}"
    result = subprocess.run(
        ["node", "-e", f"""
const {{ web_fetch }} = require('/home/ubuntu/.npm-global/lib/node_modules/openclaw/node_modules/@anthropic-ai/feature-utils/dist/webFetch.cjs');
web_fetch({{url: '{url}', extractMode: 'markdown', maxChars: 8000 }})
  .then(r => console.log(JSON.stringify(r)))
  .catch(e => console.error('ERROR:' + e.message));
"""],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
        return data.get('text', '')
    except:
        return None

def parse_markdown(md_text, lightcone_id):
    if not md_text or len(md_text) < 50:
        return None
    
    lines = md_text.split('\n')
    
    # Name: usually the first # heading
    name = None
    path = None
    stats = {}
    effect = None
    
    for line in lines:
        line = line.strip()
        # Extract name from # heading
        m = re.match(r'^#\s+(.+)$', line)
        if m and not name:
            name = m.group(1).strip()
        
        # Path from image alt text like ![存护]
        m = re.match(r'^!\[[^\]]*\]\(https://cdn\.starrailstation\.com/assets/[a-f0-9]+\.webp\)(.+)$', line)
        if m and not path:
            path = m.group(1).strip()
        
        # Stats: HP/ATK/DEF values - look for number followed by label
        if '生命值' in line or 'HP' in line.upper():
            m = re.search(r'(\d+)\s*$', line)
            if m:
                stats['hp'] = int(m.group(1))
        if '攻击力' in line or 'ATK' in line.upper():
            m = re.search(r'(\d+)\s*$', line)
            if m:
                stats['atk'] = int(m.group(1))
        if '防御力' in line or 'DEF' in line.upper():
            m = re.search(r'(\d+)\s*$', line)
            if m:
                stats['def'] = int(m.group(1))
        
        # Effect: large paragraph after stats section
        # Usually starts with "使" or similar action descriptions
        if len(line) > 30 and line.startswith('使'):
            if not effect:
                effect = line
    
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
    
    for cid in range(start, end + 1):
        print(f"[{series_name}] ID {cid}...", end=" ", flush=True)
        md_text = fetch_markdown(cid)
        
        if not md_text or len(md_text) < 50:
            print("EMPTY/NETWORK ERROR")
            empty_count += 1
        else:
            data = parse_markdown(md_text, cid)
            if data and data.get('name'):
                out_path = DATA_DIR / f"{cid}.json"
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"OK -> {data['name']} | HP={data['stats'].get('hp','?')} ATK={data['stats'].get('atk','?')} DEF={data['stats'].get('def','?')}")
                results.append(data)
                empty_count = 0
            else:
                print("PARSE FAILED")
                empty_count += 1
        
        if empty_count >= 5:
            print(f"[{series_name}] 5 consecutive failures, stopping.")
            break
        
        time.sleep(1)
    
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
