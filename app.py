from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import replicate
import os
from dotenv import load_dotenv
import requests
import time
from pathlib import Path
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

# สร้างโฟลเดอร์สำหรับเก็บวิดีโอ
VIDEOS_DIR = Path("videos")
VIDEOS_DIR.mkdir(exist_ok=True)

# ตรวจสอบ API token
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    print("⚠️  กรุณาตั้งค่า REPLICATE_API_TOKEN ในไฟล์ .env")

@app.route('/')
def index():
    return send_file('static/index.html')

def is_thai(text):
    """ตรวจสอบว่าข้อความเป็นภาษาไทยหรือไม่"""
    thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
    return bool(thai_pattern.search(text))

def translate_thai_to_english(text):
    """แปลภาษาไทยเป็นอังกฤษด้วย AI"""
    try:
        print(f"🔄 กำลังแปลภาษาไทย: {text}")
        
        # ใช้ Claude หรือ GPT แปลภาษา (ใช้ Replicate)
        translation = replicate.run(
            "meta/meta-llama-3-70b-instruct",
            input={
                "prompt": f"Translate this Thai text to English for AI image generation. Keep it descriptive and detailed. Only return the English translation, nothing else:\n\n{text}",
                "max_tokens": 200,
                "temperature": 0.3
            }
        )
        
        # รวมผลลัพธ์
        english_text = "".join(translation).strip()
        print(f"✅ แปลเป็น: {english_text}")
        return english_text
        
    except Exception as e:
        print(f"⚠️  ไม่สามารถแปลได้: {str(e)}")
        # ถ้าแปลไม่ได้ ใช้ข้อความเดิม
        return text

@app.route('/api/generate', methods=['POST'])
def generate_video():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        duration = min(int(data.get('duration', 3)), 8)  # จำกัดไม่เกิน 8 วินาที (ข้อจำกัดของ model)
        mode = data.get('mode', 'realistic')  # realistic หรือ standard
        
        if not prompt:
            return jsonify({'error': 'กรุณาใส่คำอธิบายวิดีโอ'}), 400
        
        if not REPLICATE_API_TOKEN:
            return jsonify({'error': 'ไม่พบ API token กรุณาตั้งค่าในไฟล์ .env'}), 500
        
        print(f"🎬 คำอธิบายต้นฉบับ: {prompt}")
        
        # ตรวจสอบและแปลภาษาไทยเป็นอังกฤษ
        original_prompt = prompt
        if is_thai(prompt):
            prompt = translate_thai_to_english(prompt)
        
        print(f"🎬 กำลังสร้างวิดีโอ: {prompt}")
        print(f"⏱️  ระยะเวลา: {duration} วินาที")
        print(f"🎨 โหมด: {mode}")
        
        # ตั้งค่า API token
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        
        # สร้างรูปภาพคุณภาพสูง
        print("📸 กำลังสร้างรูปภาพ...")
        
        # ปรับ prompt ให้สมจริงขึ้น
        if mode == 'realistic':
            enhanced_prompt = f"professional photograph, photorealistic, highly detailed, 8k resolution, cinematic lighting: {prompt}"
            image_model = "black-forest-labs/flux-dev"
        else:
            enhanced_prompt = f"photorealistic, detailed: {prompt}"
            image_model = "black-forest-labs/flux-schnell"
        
        print(f"🤖 ใช้ model: {image_model}")
        
        image_output = replicate.run(
            image_model,
            input={
                "prompt": enhanced_prompt,
                "aspect_ratio": "16:9",
                "output_format": "png"
            }
        )
        
        first_frame = str(image_output[0] if isinstance(image_output, list) else image_output)
        print(f"✅ สร้างรูปภาพเสร็จ: {first_frame}")
        
        # แปลงเป็นวิดีโอ
        print("🎬 กำลังสร้างวิดีโอ...")
        
        output = replicate.run(
            "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
            input={
                "input_image": first_frame,
                "video_length": "25_frames_with_svd_xt",
                "sizing_strategy": "maintain_aspect_ratio",
                "frames_per_second": 6,
                "motion_bucket_id": 127,
                "cond_aug": 0.02
            }
        )
        
        # ดาวน์โหลดวิดีโอ
        # แปลง output เป็น string URL
        if isinstance(output, list):
            video_url = str(output[0])
        else:
            video_url = str(output)
        
        print(f"📥 กำลังดาวน์โหลดวิดีโอจาก: {video_url}")
        
        timestamp = int(time.time())
        filename = f"video_{timestamp}.mp4"
        filepath = VIDEOS_DIR / filename
        
        response = requests.get(video_url, timeout=60)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        file_size = filepath.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ สร้างวิดีโอสำเร็จ: {filename} ({file_size:.2f} MB)")
        
        return jsonify({
            'success': True,
            'video_url': f'/api/video/{filename}',
            'filename': filename
        })
        
    except requests.exceptions.RequestException as e:
        print(f"❌ เกิดข้อผิดพลาดในการดาวน์โหลด: {str(e)}")
        return jsonify({'error': f'ไม่สามารถดาวน์โหลดวิดีโอได้: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/video/<filename>')
def get_video(filename):
    filepath = VIDEOS_DIR / filename
    if filepath.exists():
        return send_file(filepath, mimetype='video/mp4')
    return jsonify({'error': 'ไม่พบไฟล์วิดีโอ'}), 404

@app.route('/api/models', methods=['GET'])
def get_models():
    """รายการ models ที่รองรับ"""
    models = [
        {
            'id': 'zeroscope-v2-xl',
            'name': 'Zeroscope V2 XL',
            'description': 'Text-to-video model คุณภาพสูง',
            'max_duration': 8
        }
    ]
    return jsonify(models)

if __name__ == '__main__':
    print("🚀 เริ่มต้น AI Video Generator")
    print("📝 เปิดเบราว์เซอร์ที่: http://localhost:5000")
    app.run(debug=True, port=5000)
