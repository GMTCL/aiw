from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import replicate
import os
from dotenv import load_dotenv
import requests
import time
from pathlib import Path
import re
from gtts import gTTS
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️  MoviePy ไม่พร้อมใช้งาน - ฟีเจอร์เสียงพากย์จะถูกปิด")
import tempfile

load_dotenv()

app = Flask(__name__)
CORS(app)

# สร้างโฟลเดอร์สำหรับเก็บวิดีโอและเสียง
VIDEOS_DIR = Path("videos")
VIDEOS_DIR.mkdir(exist_ok=True)
AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)

# ตรวจสอบ API token
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
LUMAAI_API_KEY = os.getenv("LUMAAI_API_KEY")

if not REPLICATE_API_TOKEN:
    print("⚠️  กรุณาตั้งค่า REPLICATE_API_TOKEN ในไฟล์ .env")
if not LUMAAI_API_KEY:
    print("⚠️  กรุณาตั้งค่า LUMAAI_API_KEY ในไฟล์ .env")

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

def add_thai_voiceover(video_path, text):
    """เพิ่มเสียงพากย์ภาษาไทยให้กับวิดีโอ"""
    if not MOVIEPY_AVAILABLE:
        print("⚠️  MoviePy ไม่พร้อมใช้งาน - ข้ามการเพิ่มเสียง")
        return video_path
    
    try:
        print(f"🎤 กำลังสร้างเสียงพากย์: {text}")
        
        # สร้างไฟล์เสียงจาก text
        timestamp = int(time.time())
        audio_file = AUDIO_DIR / f"voice_{timestamp}.mp3"
        
        tts = gTTS(text=text, lang='th', slow=False)
        tts.save(str(audio_file))
        
        print(f"✅ สร้างเสียงเสร็จ: {audio_file}")
        
        # รวมเสียงกับวิดีโอ
        print("🎬 กำลังรวมเสียงกับวิดีโอ...")
        
        video = VideoFileClip(str(video_path))
        audio = AudioFileClip(str(audio_file))
        
        # ถ้าวิดีโอมีเสียงอยู่แล้ว ให้รวมกัน
        if video.audio:
            final_audio = CompositeAudioClip([video.audio, audio])
        else:
            final_audio = audio
        
        video_with_audio = video.set_audio(final_audio)
        
        # บันทึกวิดีโอใหม่
        output_path = video_path.parent / f"voiced_{video_path.name}"
        video_with_audio.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(AUDIO_DIR / f"temp_{timestamp}.m4a"),
            remove_temp=True,
            logger=None
        )
        
        # ปิด clips
        video.close()
        audio.close()
        video_with_audio.close()
        
        # ลบไฟล์เสียงชั่วคราว
        audio_file.unlink()
        
        print(f"✅ รวมเสียงเสร็จ: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"⚠️  ไม่สามารถเพิ่มเสียงได้: {str(e)}")
        return video_path

@app.route('/api/generate', methods=['POST'])
def generate_video():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        duration = min(int(data.get('duration', 5)), 5)  # Luma AI รองรับสูงสุด 5 วินาที
        mode = data.get('mode', 'realistic')  # realistic หรือ standard
        add_voice = data.get('add_voice', False)  # เพิ่มเสียงพากย์หรือไม่
        
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
        
        if not LUMAAI_API_KEY:
            return jsonify({'error': 'ไม่พบ Luma AI API key กรุณาตั้งค่าในไฟล์ .env'}), 500
        
        print(f"🎬 กำลังสร้างวิดีโอด้วย Luma AI Dream Machine...")
        print(f"📝 Prompt: {prompt}")
        
        # เรียก Luma AI API ตาม documentation
        luma_url = "https://api.lumalabs.ai/dream-machine/v1/generations"
        headers = {
            "Authorization": f"Bearer {LUMAAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "ray-2",
            "prompt": prompt,
            "aspect_ratio": "16:9"
        }
        
        # สร้างวิดีโอ
        print("📤 ส่งคำขอไปยัง Luma AI...")
        response = requests.post(luma_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 201:
            error_detail = response.text
            print(f"❌ Luma AI Error: {error_detail}")
            raise Exception(f"Luma AI API Error ({response.status_code}): {error_detail}")
        
        generation_data = response.json()
        generation_id = generation_data.get("id")
        
        if not generation_id:
            raise Exception("ไม่ได้รับ generation ID จาก Luma AI")
        
        print(f"⏳ กำลังสร้างวิดีโอ... (ID: {generation_id})")
        
        # รอให้วิดีโอสร้างเสร็จ (polling)
        max_attempts = 120  # รอสูงสุด 10 นาที
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(5)  # รอ 5 วินาทีต่อครั้ง
            attempt += 1
            
            # เช็คสถานะ
            status_response = requests.get(
                f"{luma_url}/{generation_id}",
                headers=headers,
                timeout=10
            )
            
            if status_response.status_code != 200:
                print(f"⚠️  ไม่สามารถเช็คสถานะได้: {status_response.status_code}")
                continue
            
            status_data = status_response.json()
            state = status_data.get("state")
            print(f"📊 สถานะ: {state} ({attempt}/{max_attempts})")
            
            if state == "completed":
                video_data = status_data.get("assets", {})
                video_url = video_data.get("video")
                
                if not video_url:
                    raise Exception("ไม่พบ URL วิดีโอในผลลัพธ์")
                
                print(f"✅ สร้างวิดีโอเสร็จแล้ว!")
                output = video_url
                break
            elif state == "failed":
                error_msg = status_data.get("failure_reason", "Unknown error")
                raise Exception(f"การสร้างวิดีโอล้มเหลว: {error_msg}")
        else:
            raise Exception("หมดเวลารอการสร้างวิดีโอ (10 นาที)")
        
        # ดาวน์โหลดวิดีโอ
        video_url = str(output)
        
        print(f"📥 กำลังดาวน์โหลดวิดีโอจาก: {video_url}")
        
        timestamp = int(time.time())
        filename = f"video_{timestamp}.mp4"
        filepath = VIDEOS_DIR / filename
        
        video_response = requests.get(video_url, timeout=120)
        video_response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(video_response.content)
        
        file_size = filepath.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ สร้างวิดีโอสำเร็จ: {filename} ({file_size:.2f} MB)")
        
        # เพิ่มเสียงพากย์ถ้าเลือก
        final_filepath = filepath
        if add_voice:
            print("🎤 กำลังเพิ่มเสียงพากย์ภาษาไทย...")
            voiced_filepath = add_thai_voiceover(filepath, original_prompt)
            if voiced_filepath != filepath:
                final_filepath = voiced_filepath
                filename = final_filepath.name
                print(f"✅ เพิ่มเสียงพากย์สำเร็จ!")
        
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
