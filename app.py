from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
# เปิดใช้งาน CORS เพื่อให้เว็บไซต์อื่น (เช่น infinityfree.me) สามารถเรียกใช้งาน API ได้
CORS(app)

@app.route("/", methods=["GET"])
def home():
  return jsonify(
      {"status": "success", "message": "HDJ888 Python Backend is running!"}
  )


# กำหนด Route สำหรับดึงลิงก์วิดีโอ (คุณสามารถปรับเปลี่ยนฟังก์ชันภายในตามโค้ดเดิมของคุณได้เลย)
@app.route("/get-stream", methods=["GET", "POST"])
def get_stream():
  target_url = request.args.get("url") or (
      request.json.get("url") if request.is_json else None
  )

  if not target_url:
    return (
        jsonify({"status": "error", "message": "Missing target URL"}),
        400,
    )

  try:
    # --- ใส่โค้ด Playwright เดิมของคุณตรงนี้ ---
    # ตัวอย่างจำลองการส่งค่าผลลัพธ์กลับไปให้หน้าเว็บ
    stream_link = "https://example.com/stream.m3u8"  # แทนที่ด้วยลิงก์ที่ Playwright ดึงได้

    return jsonify({"status": "success", "stream_url": stream_link})
  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
  # Render จะใช้ PORT จาก Environment Variable หรือรันที่พอร์ต 10000
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
