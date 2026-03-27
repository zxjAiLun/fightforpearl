"""
光锥数据爬虫 - 使用Playwright
"""
import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "https://starrailstation.com/cn/lightcone"

async def crawl_lightcone(page, lightcone_id: int) -> dict | None:
    """爬取单个光锥数据"""
    url = f"{BASE_URL}/{lightcone_id}"
    try:
        await page.goto(url, wait_until="networkidle", timeout=15000)
        # 等待页面加载
        await page.wait_for_timeout(1000)
        
        # 提取数据
        data = await page.evaluate("""
            () => {
                const result = {};
                
                // 获取标题
                const titleEl = document.querySelector('h1, h2, .title');
                if (titleEl) result.name = titleEl.textContent.trim();
                
                // 获取命途
                const pathEl = document.querySelector('img[alt*="存护"], img[alt*="巡猎"], img[alt*="同谐"], img[alt*="虚无"], img[alt*="丰饶"], img[alt*="毁灭"]');
                if (pathEl) result.path = pathEl.alt;
                
                // 获取属性
                const stats = {};
                const statEls = document.querySelectorAll('[class*="stat"], [class*="hp"], [class*="atk"], [class*="def"]');
                statEls.forEach(el => {
                    const text = el.textContent;
                    if (text.includes('生命')) {
                        const match = text.match(/\\d+/);
                        if (match) stats.hp = parseInt(match[0]);
                    }
                    if (text.includes('攻击力')) {
                        const match = text.match(/\\d+/);
                        if (match) stats.atk = parseInt(match[0]);
                    }
                    if (text.includes('防御力')) {
                        const match = text.match(/\\d+/);
                        if (match) stats.def = parseInt(match[0]);
                    }
                });
                if (Object.keys(stats).length > 0) result.stats = stats;
                
                // 获取效果描述
                const effectEl = document.querySelector('[class*="effect"], .description, .skill-desc');
                if (effectEl) result.effect = effectEl.textContent.trim();
                
                // 如果有description但不是上面的选择器
                if (!result.effect) {
                    const descEl = document.querySelector('p');
                    if (descEl) result.effect = descEl.textContent.trim();
                }
                
                return result;
            }
        """)
        
        # 检查是否有有效数据
        if data and (data.get('name') or data.get('effect')):
            data['id'] = lightcone_id
            return data
        return None
    except Exception as e:
        print(f"Error crawling {lightcone_id}: {e}")
        return None

async def crawl_range(start: int, end: int, output_dir: Path):
    """爬取ID范围的光锥"""
    results = []
    empty_count = 0
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for lightcone_id in range(start, end + 1):
            print(f"Crawling {lightcone_id}...", end=" ")
            data = await crawl_lightcone(page, lightcone_id)
            
            if data:
                # 保存到文件
                file_path = output_dir / f"{lightcone_id}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"✓ {data.get('name', 'unknown')}")
                results.append(data)
                empty_count = 0
            else:
                print("✗ (empty)")
                empty_count += 1
                # 连续5个空页面则停止
                if empty_count >= 5:
                    print(f"Stopping: 5 consecutive empty pages at {lightcone_id}")
                    break
        
        await browser.close()
    
    return results

async def main():
    output_dir = Path("data/lightcones_playwright")
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 50)
    print("光锥数据爬虫 - Playwright版")
    print("=" * 50)
    
    # 23000系列
    print("\n📦 爬取23000系列 (23001-23100)...")
    results_23 = await crawl_range(23001, 23100, output_dir)
    print(f"获取 {len(results_23)} 个光锥")
    
    # 24000系列
    print("\n📦 爬取24000系列 (24001-24100)...")
    results_24 = await crawl_range(24001, 24100, output_dir)
    print(f"获取 {len(results_24)} 个光锥")
    
    # 汇总
    all_results = results_23 + results_24
    print(f"\n✅ 总计获取 {len(all_results)} 个光锥")
    
    # 保存汇总文件
    summary_file = output_dir / "summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"📁 汇总保存到 {summary_file}")

if __name__ == "__main__":
    asyncio.run(main())
