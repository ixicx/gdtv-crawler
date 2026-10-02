import asyncio
import re
import requests
import os
import time

# 从Github密钥读取配置
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_NAMESPACE_ID = os.getenv("CF_NAMESPACE_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")

CHANNELS = [
    {"name": "广东卫视", "cid": "43", "page": "https://m.gdtv.cn/live?channelId=43"},
    {"name": "广东珠江", "cid": "44", "page": "https://m.gdtv.cn/live?channelId=44"},
    {"name": "广东新闻", "cid": "45", "page": "https://m.gdtv.cn/live?channelId=45"},
    {"name": "大湾区卫视", "cid": "51", "page": "https://m.gdtv.cn/live?channelId=51"},
    {"name": "大湾区卫视(海外版)", "cid": "46", "page": "https://m.gdtv.cn/live?channelId=46"},
    {"name": "广东影视", "cid": "47", "page": "https://m.gdtv.cn/live?channelId=47"},
    {"name": "广东体育", "cid": "48", "page": "https://m.gdtv.cn/live?channelId=48"},
    {"name": "4K超高清", "cid": "49", "page": "https://m.gdtv.cn/live?channelId=49"},
    {"name": "广东少儿", "cid": "50", "page": "https://m.gdtv.cn/live?channelId=50"},
    {"name": "嘉佳卡通", "cid": "52", "page": "https://m.gdtv.cn/live?channelId=52"},
    {"name": "岭南戏曲", "cid": "53", "page": "https://m.gdtv.cn/live?channelId=53"},
    {"name": "南方购物", "cid": "54", "page": "https://m.gdtv.cn/live?channelId=54"},
]

USER_AGENT = "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36"

def write_kv(cid, m3u_url):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_NAMESPACE_ID}/values/{cid}"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}
    resp = requests.put(url, headers=headers, data=m3u_url, timeout=10)
    res = resp.json()
    if res.get("success"):
        print(f"✅ KV写入成功 cid:{cid}")
    else:
        print(f"❌ KV写入失败 cid:{cid} | {res}")

async def fetch_channel(page, ch):
    start = time.time()
    try:
        await page.goto(ch["page"], timeout=15000)
        await page.wait_for_timeout(3000)
        html = await page.content()
        match = re.search(r'https?://[^"\']+\.m3u8[^"\']*', html)
        if match:
            m3u = match.group(0)
            print(f"✅ 抓取成功 {ch['name']}")
            write_kv(ch["cid"], m3u)
        else:
            print(f"⚠️ 无直播源 {ch['name']}")
    except Exception as e:
        print(f"❌ 抓取异常 {ch['name']} | {str(e)}")
    print(f"⏱ 耗时 {round(time.time()-start,2)}s\n")

async def main():
    print("===== 云端爬虫启动 =====")
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(user_agent=USER_AGENT)
        page = await ctx.new_page()
        for ch in CHANNELS:
            await fetch_channel(page, ch)
        await browser.close()
    print("===== 本轮抓取完成 =====")

if __name__ == "__main__":
    asyncio.run(main())