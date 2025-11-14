# 🚀 คู่มือ Deploy โปรเจกต์ไปยัง VPS

## ⚠️ ก่อนเริ่ม - สำคัญมาก!

1. **เปลี่ยน root password ทันที:**
```bash
passwd
```

2. **สร้าง user ใหม่ (ไม่ใช้ root):**
```bash
adduser aiuser
usermod -aG sudo aiuser
```

---

## 📦 ขั้นตอนที่ 1: เชื่อมต่อ VPS

### Windows (ใช้ PowerShell หรือ CMD):
```bash
ssh root@27.254.143.53
```

### หรือใช้ PuTTY:
- Host: 27.254.143.53
- Port: 22
- Username: root
- Password: (ใส่ password)

---

## 🧹 ขั้นตอนที่ 2: ทำความสะอาดเซิร์ฟเวอร์

```bash
# อัปเดตระบบ
apt update && apt upgrade -y

# ลบไฟล์ไม่จำเป็น (ระวัง! จะลบทุกอย่างใน /var/www)
rm -rf /var/www/*
rm -rf /home/*/public_html

# ลบ Apache ถ้ามี (ถ้าไม่ต้องการ)
apt remove apache2 -y
apt autoremove -y
```

---

## 🐍 ขั้นตอนที่ 3: ติดตั้ง Python และ Dependencies

```bash
# ติดตั้ง Python 3.12
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install python3.12 python3.12-venv python3-pip -y

# ติดตั้ง Nginx
apt install nginx -y

# ติดตั้ง Git
apt install git -y
```

---

## 📁 ขั้นตอนที่ 4: อัปโหลดโปรเจกต์

### วิธีที่ 1: ใช้ Git (แนะนำ)
```bash
cd /var/www
git clone <your-github-repo-url> aivideo
cd aivideo
```

### วิธีที่ 2: อัปโหลดด้วย FileZilla/WinSCP
1. เชื่อมต่อ SFTP:
   - Host: 27.254.143.53
   - Port: 22
   - Username: root
   - Password: (ใส่ password)
2. อัปโหลดโฟลเดอร์โปรเจกต์ไปที่ `/var/www/aivideo`

---

## 🔧 ขั้นตอนที่ 5: ติดตั้ง Python Packages

```bash
cd /var/www/aivideo

# สร้าง virtual environment
python3.12 -m venv venv

# เปิดใช้งาน venv
source venv/bin/activate

# ติดตั้ง packages
pip install -r requirements.txt
```

---

## 🔑 ขั้นตอนที่ 6: ตั้งค่า Environment Variables

```bash
# สร้างไฟล์ .env
nano .env
```

ใส่ข้อมูล:
```
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

กด `Ctrl+X` แล้ว `Y` แล้ว `Enter` เพื่อบันทึก

---

## 🚀 ขั้นตอนที่ 7: ติดตั้ง Gunicorn (Production Server)

```bash
pip install gunicorn

# ทดสอบรัน
gunicorn --bind 0.0.0.0:8000 app:app
```

กด `Ctrl+C` เพื่อหยุด

---

## 🔄 ขั้นตอนที่ 8: สร้าง Systemd Service (รันอัตโนมัติ)

```bash
nano /etc/systemd/system/aivideo.service
```

ใส่ข้อมูล:
```ini
[Unit]
Description=AI Video Generator
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/aivideo
Environment="PATH=/var/www/aivideo/venv/bin"
ExecStart=/var/www/aivideo/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

บันทึกและเปิดใช้งาน:
```bash
systemctl daemon-reload
systemctl start aivideo
systemctl enable aivideo
systemctl status aivideo
```

---

## 🌐 ขั้นตอนที่ 9: ตั้งค่า Nginx (Reverse Proxy)

```bash
nano /etc/nginx/sites-available/aivideo
```

ใส่ข้อมูล:
```nginx
server {
    listen 80;
    server_name 27.254.143.53;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/aivideo/static;
    }
}
```

เปิดใช้งาน:
```bash
ln -s /etc/nginx/sites-available/aivideo /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

---

## 🔥 ขั้นตอนที่ 10: ตั้งค่า Firewall

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

## ✅ ทดสอบ

เปิดเบราว์เซอร์ไปที่:
```
http://27.254.143.53
```

---

## 🔒 ขั้นตอนที่ 11: ติดตั้ง SSL (HTTPS) - ถ้ามี Domain

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d yourdomain.com
```

---

## 📊 คำสั่งที่มีประโยชน์

```bash
# ดู log
journalctl -u aivideo -f

# รีสตาร์ทแอป
systemctl restart aivideo

# ดูสถานะ
systemctl status aivideo

# รีสตาร์ท Nginx
systemctl restart nginx
```

---

## 🆘 แก้ปัญหา

### ปัญหา: Port 8000 ถูกใช้งาน
```bash
lsof -i :8000
kill -9 <PID>
```

### ปัญหา: Permission denied
```bash
chmod -R 755 /var/www/aivideo
chown -R www-data:www-data /var/www/aivideo
```

### ปัญหา: Nginx error
```bash
nginx -t
tail -f /var/log/nginx/error.log
```

---

## 📝 หมายเหตุ

1. **เปลี่ยน password ทันที!**
2. สร้าง user ใหม่แทน root
3. ตั้งค่า SSH key authentication
4. อัปเดตระบบสม่ำเสมอ
5. Backup ข้อมูลเป็นประจำ

---

## 🎉 เสร็จสิ้น!

เว็บไซต์ของคุณพร้อมใช้งานแล้วที่:
- http://27.254.143.53

หรือถ้ามี domain:
- https://yourdomain.com
