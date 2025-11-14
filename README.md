# 🎬 AI Video Generator - WG THAILAND

ระบบสร้างวิดีโอด้วย AI คุณภาพสูง พร้อมเสียงพากย์ภาษาไทย

## ✨ ฟีเจอร์

- 🎥 **สร้างวิดีโอจาก Text** - ใช้ Luma AI Dream Machine (ray-3)
- 🇹🇭 **รองรับภาษาไทย** - แปลภาษาไทยเป็นอังกฤษอัตโนมัติ
- 🎤 **เสียงพากย์ภาษาไทย** - เพิ่มเสียงพากย์ด้วย Google TTS
- ⚡ **วิดีโอคุณภาพสูง** - ความละเอียด HD, 5 วินาที
- 🎨 **2 โหมด** - เหมือนจริง และ ธรรมดา
- 📱 **Responsive Design** - ใช้งานได้ทุกอุปกรณ์

## 🚀 การติดตั้ง

### ความต้องการ

- Python 3.12+
- FFmpeg (สำหรับ MoviePy)
- Luma AI API Key
- Replicate API Key (สำหรับแปลภาษา)

### ติดตั้งบน Local

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ai-video-generator.git
cd ai-video-generator

# สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ
venv\Scripts\activate  # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt

# ตั้งค่า environment variables
cp .env.example .env
# แก้ไข .env ใส่ API keys

# รัน server
python app.py
```

เปิดเบราว์เซอร์ที่: http://localhost:5000

### ติดตั้งบน VPS

ดูคู่มือโดยละเอียดที่: [DEPLOY_VPS_GUIDE.md](DEPLOY_VPS_GUIDE.md)

## 🔑 API Keys

### 1. Luma AI API Key

1. ไปที่ https://lumalabs.ai
2. สมัครสมาชิก
3. ซื้อ credits ($10 = 10 วิดีโอ)
4. สร้าง API key ที่ https://lumalabs.ai/dashboard/api-keys

### 2. Replicate API Key

1. ไปที่ https://replicate.com
2. สมัครสมาชิก
3. ไปที่ https://replicate.com/account/api-tokens
4. สร้าง API token

## 📝 การใช้งาน

1. **ใส่คำอธิบายวิดีโอ** - เช่น "สุนัข 3 ตัววิ่งเล่นบนชายหาด"
2. **เลือกโหมด** - เหมือนจริง หรือ ธรรมดา
3. **เลือกระยะเวลา** - 3-5 วินาที
4. **เลือกเสียงพากย์** (ถ้าต้องการ)
5. **กดสร้างวิดีโอ** - รอ 1-2 นาที
6. **ดาวน์โหลด** - คลิกขวาที่วิดีโอ > Save video as

## 🛠️ เทคโนโลยี

- **Backend**: Flask (Python)
- **AI Models**: 
  - Luma AI Dream Machine (ray-3) - Video Generation
  - Meta Llama 3 - Thai Translation
  - FLUX 1.1 Pro - Image Generation (fallback)
- **TTS**: Google Text-to-Speech (gTTS)
- **Video Processing**: MoviePy
- **Frontend**: HTML, CSS, JavaScript

## 📊 ราคา

### Luma AI
- $10 = 1,000 credits = ~10 วิดีโอ (5 วินาที)
- $20 = 2,000 credits = ~20 วิดีโอ

### Replicate
- จ่ายตามใช้จริง
- แปลภาษา: ~$0.001 ต่อครั้ง

## 🐛 แก้ปัญหา

### MoviePy Error
```bash
pip uninstall moviepy -y
pip install moviepy==1.0.3
```

### FFmpeg Not Found
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **CentOS/RHEL**: `sudo yum install ffmpeg`
- **Windows**: ดาวน์โหลดจาก https://ffmpeg.org/download.html

### Luma AI 404 Error
- ตรวจสอบ API key ถูกต้อง
- ตรวจสอบว่าเติมเงินแล้ว (ต้องซื้อ credits)

## 📄 License

MIT License

## 👨‍💻 Author

WG THAILAND

## 🙏 Credits

- [Luma AI](https://lumalabs.ai) - Video Generation
- [Replicate](https://replicate.com) - AI Models
- [gTTS](https://github.com/pndurette/gTTS) - Text-to-Speech
- [MoviePy](https://zulko.github.io/moviepy/) - Video Processing
