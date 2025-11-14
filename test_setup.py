"""
สคริปต์ทดสอบการติดตั้งและตั้งค่า
รันด้วย: python test_setup.py
"""

import sys
import os

def test_python_version():
    """ตรวจสอบเวอร์ชัน Python"""
    print("🔍 ตรวจสอบ Python...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ❌ ต้องการ Python 3.8 ขึ้นไป")
        return False
    print("   ✅ เวอร์ชัน Python ถูกต้อง")
    return True

def test_imports():
    """ตรวจสอบ packages ที่จำเป็น"""
    print("\n🔍 ตรวจสอบ packages...")
    packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'replicate': 'Replicate',
        'dotenv': 'python-dotenv',
        'requests': 'Requests'
    }
    
    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - ยังไม่ได้ติดตั้ง")
            all_ok = False
    
    return all_ok

def test_env_file():
    """ตรวจสอบไฟล์ .env"""
    print("\n🔍 ตรวจสอบไฟล์ .env...")
    
    if not os.path.exists('.env'):
        print("   ⚠️  ไม่พบไฟล์ .env")
        print("   💡 สร้างไฟล์ .env และใส่: REPLICATE_API_TOKEN=your_token")
        return False
    
    print("   ✅ พบไฟล์ .env")
    
    # ตรวจสอบ token
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('REPLICATE_API_TOKEN')
    if not token:
        print("   ⚠️  ไม่พบ REPLICATE_API_TOKEN ในไฟล์ .env")
        return False
    
    if token == 'your_token_here' or token == 'your_api_token_here':
        print("   ⚠️  กรุณาใส่ API token จริงในไฟล์ .env")
        return False
    
    print(f"   ✅ พบ API token (เริ่มต้นด้วย: {token[:8]}...)")
    return True

def test_directories():
    """ตรวจสอบโฟลเดอร์ที่จำเป็น"""
    print("\n🔍 ตรวจสอบโครงสร้างโฟลเดอร์...")
    
    dirs = ['static', 'videos']
    all_ok = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ โฟลเดอร์ {dir_name}/")
        else:
            print(f"   ⚠️  ไม่พบโฟลเดอร์ {dir_name}/ (จะสร้างอัตโนมัติ)")
            all_ok = False
    
    # ตรวจสอบไฟล์สำคัญ
    files = ['app.py', 'static/index.html', 'requirements.txt']
    for file_name in files:
        if os.path.exists(file_name):
            print(f"   ✅ ไฟล์ {file_name}")
        else:
            print(f"   ❌ ไม่พบไฟล์ {file_name}")
            all_ok = False
    
    return all_ok

def test_port():
    """ตรวจสอบว่า port 5000 ว่างหรือไม่"""
    print("\n🔍 ตรวจสอบ port 5000...")
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    
    if result == 0:
        print("   ⚠️  Port 5000 กำลังถูกใช้งาน")
        print("   💡 ปิดโปรแกรมที่ใช้ port 5000 หรือเปลี่ยน port ใน app.py")
        return False
    
    print("   ✅ Port 5000 ว่าง")
    return True

def main():
    print("=" * 60)
    print("🧪 ทดสอบการติดตั้ง AI Video Generator")
    print("=" * 60)
    
    results = {
        'Python Version': test_python_version(),
        'Packages': test_imports(),
        'Environment File': test_env_file(),
        'Project Structure': test_directories(),
        'Port Availability': test_port()
    }
    
    print("\n" + "=" * 60)
    print("📊 สรุปผลการทดสอบ")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ ผ่าน" if result else "❌ ไม่ผ่าน"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ระบบพร้อมใช้งาน!")
        print("💡 รันด้วยคำสั่ง: python app.py")
    else:
        print("⚠️  มีบางอย่างต้องแก้ไข")
        print("\n📝 ขั้นตอนที่ต้องทำ:")
        
        if not results['Packages']:
            print("   1. ติดตั้ง packages: pip install -r requirements.txt")
        
        if not results['Environment File']:
            print("   2. สร้างไฟล์ .env และใส่ API token")
            print("      REPLICATE_API_TOKEN=your_token_here")
        
        if not results['Port Availability']:
            print("   3. ปิดโปรแกรมที่ใช้ port 5000")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
