from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import os
import sys
import shutil
import requests
from urllib.parse import urlparse
from playwright.async_api import async_playwright

app = Flask(__name__)
CORS(app)

# 1. ฟังก์ชันหลักสำหรับดึงลิงก์วิดีโอผ่าน Playwright
async def get_stream_url(detail_url, ep_num, log_func):
    base_play_url = detail_url.replace("/drama/detail/", "/play/detail/")
    target_url = f"{base_play_url}&ep={ep_num}"
    video_url = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,  # ⚠️ สำคัญมาก: บน Render ต้องเป็น True เพราะเซิร์ฟเวอร์ไม่มีหน้าจอแสดงผล
            args=[
                "--autoplay-policy=no-user-gesture-required",
                "--mute-audio",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        context = await browser.new_context()
        page = await context.new_page()

        def handle_request(req):
            nonlocal video_url
            url = req.url
            if ("cloudflarestorage.com" in url or ".mp4" in url or "full.mp4" in url) and "ads" not in url:
                video_url = url

        page.on("request", handle_request)

        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
            
            for _ in range(60):
                if video_url:
                    break
                
                try:
                    await page.click("body", timeout=100)
                except:
                    pass

                try:
                    selectors = [
                        ".close", ".ad-close", ".skip", ".ads-close", 
                        "text=skip", "text=ข้าม", "text=ปิด", "text=Close",
                        "[class*='close']", "[class*='skip']", "[id*='close']"
                    ]
                    for sel in selectors:
                        btn = page.locator(sel).first
                        if await btn.is_visible():
                            await btn.click(timeout=50)
                            log_func(f"⚡ [Auto-Ad] กดปิดโฆษณาตอนที่ {ep_num} สำเร็จ")
                            break
                except:
                    pass

                await asyncio.sleep(0.25)

        except Exception as e:
            log_func(f"❌ Error EP {ep_num}: {e}")

        await browser.close()
    return video_url

# 2. API Endpoint รองรับทั้ง 2 เส้นทาง
@app.route('/api/get-stream', methods=['GET'])
@app.route('/get-stream', methods=['GET'])
def get_stream():
    detail_url = request.args.get('url')
    ep_num = int(request.args.get('ep', 1))
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    video_url = loop.run_until_complete(get_stream_url(detail_url, ep_num, print))
    loop.close()
    
    if video_url:
        return jsonify({"video_url": video_url})
    return jsonify({"video_url": None}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
