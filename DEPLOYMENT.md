# 🚀 Deployment Guide - File Merger SPA

คู่มือการ Deploy แอปพลิเคชัน File Merger ในรูปแบบต่างๆ

## 📋 Table of Contents

- [🌐 Streamlit Cloud (แนะนำ)](#-streamlit-cloud-แนะนำ)
- [🐳 Docker Deployment](#-docker-deployment)
- [☁️ Cloud Platforms](#-cloud-platforms)
- [🖥 Local Production](#-local-production)
- [🔧 Environment Variables](#-environment-variables)
- [📊 Monitoring & Logging](#-monitoring--logging)
- [🐛 Troubleshooting](#-troubleshooting)

## 🌐 Streamlit Cloud (แนะนำ)

### ข้อดี
- ✅ ฟรี 100%
- ✅ Setup ง่ายที่สุด
- ✅ Auto-deploy เมื่อ push code
- ✅ HTTPS built-in
- ✅ Resource management อัตโนมัติ

### ขั้นตอนการ Deploy

#### 1. เตรียม Repository
```bash
# Clone หรือ fork repository
git clone https://github.com/yourusername/file-merger-spa.git
cd file-merger-spa

# Push ไปยัง GitHub repository ของคุณ
git remote set-url origin https://github.com/yourusername/your-repo-name.git
git push origin main
```

#### 2. Deploy บน Streamlit Cloud
1. **เข้าไปที่ [share.streamlit.io](https://share.streamlit.io/)**
2. **Sign in ด้วย GitHub account**
3. **คลิก "New app"**
4. **เลือก Repository และ Branch**
   - Repository: `yourusername/your-repo-name`
   - Branch: `main`
   - Main file path: `app.py`
5. **คลิก "Deploy!"**

#### 3. การตั้งค่าเพิ่มเติม (Optional)
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#8B4513"
backgroundColor = "#F5E6D3"
secondaryBackgroundColor = "#E5D4B1"
textColor = "#654321"

[server]
maxUploadSize = 200
maxMessageSize = 200
```

#### 4. Custom Domain (Optional)
- ใน Streamlit Cloud dashboard
- Settings → Custom domain
- เพิ่ม CNAME record ใน DNS

## 🐳 Docker Deployment

### ข้อดี
- ✅ Environment consistency
- ✅ Easy scaling
- ✅ Isolated deployment
- ✅ Works anywhere

### Single Container

#### Build และ Run
```bash
# Build image
docker build -t file-merger:latest .

# Run container
docker run -d \
  --name file-merger-app \
  -p 8501:8501 \
  --restart unless-stopped \
  file-merger:latest

# Check logs
docker logs file-merger-app

# Access application
# http://localhost:8501
```

### Docker Compose (Production Ready)

#### สร้าง production docker-compose.yml
```yaml
version: '3.8'

services:
  file-merger:
    build: .
    container_name: file-merger-app
    restart: unless-stopped
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
    volumes:
      - ./logs:/app/logs
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: file-merger-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - file-merger
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

#### Deploy ด้วย Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update and redeploy
git pull
docker-compose build
docker-compose up -d
```

### Nginx Configuration
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream streamlit {
        server file-merger:8501;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        location / {
            proxy_pass http://streamlit;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

## ☁️ Cloud Platforms

### 🚀 Railway

#### 1. เตรียมไฟล์
```bash
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
  }
}
```

#### 2. Deploy
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### ⚡ Render

#### 1. สร้าง render.yaml
```yaml
services:
  - type: web
    name: file-merger
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
    plan: free
```

#### 2. Deploy ผ่าน GitHub integration

### 🌊 DigitalOcean App Platform

#### 1. สร้าง .do/app.yaml
```yaml
name: file-merger-spa
services:
  - name: web
    source_dir: /
    github:
      repo: yourusername/file-merger-spa
      branch: main
    run_command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
```

### ☁️ Google Cloud Run

#### 1. เตรียม Dockerfile สำหรับ Cloud Run
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE $PORT

CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

#### 2. Deploy
```bash
# Build และ push image
gcloud builds submit --tag gcr.io/PROJECT-ID/file-merger

# Deploy to Cloud Run
gcloud run deploy --image gcr.io/PROJECT-ID/file-merger --platform managed
```

## 🖥 Local Production

### ข้อกำหนด
- Python 3.8+
- 2GB RAM ขึ้นไป
- 1GB disk space

### การติดตั้ง
```bash
# Clone repository
git clone https://github.com/yourusername/file-merger-spa.git
cd file-merger-spa

# สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Run in production mode
streamlit run app.py \
  --server.headless=true \
  --server.enableCORS=false \
  --server.port=8501 \
  --server.address=0.0.0.0
```

### Systemd Service (Linux)
```ini
# /etc/systemd/system/file-merger.service
[Unit]
Description=File Merger SPA
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/file-merger-spa
Environment=PATH=/path/to/file-merger-spa/venv/bin
ExecStart=/path/to/file-merger-spa/venv/bin/streamlit run app.py --server.headless=true --server.port=8501
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Enable และ start service
sudo systemctl enable file-merger.service
sudo systemctl start file-merger.service
sudo systemctl status file-merger.service
```

## 🔧 Environment Variables

### Streamlit Configuration
```bash
# Port configuration
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Performance settings
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200

# Security settings
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# Logging
export STREAMLIT_LOGGER_LEVEL=info
```

### Application Settings
```bash
# Memory limits (if needed)
export PYTHONMALLOC=malloc
export MALLOC_ARENA_MAX=2

# Pandas settings
export PANDAS_MAX_ROWS=10000
export PANDAS_MAX_COLUMNS=1000
```

## 📊 Monitoring & Logging

### Health Checks
```python
# health_check.py
import requests
import sys

try:
    response = requests.get('http://localhost:8501/_stcore/health', timeout=10)
    if response.status_code == 200:
        print("✅ App is healthy")
        sys.exit(0)
    else:
        print("❌ App is unhealthy")
        sys.exit(1)
except Exception as e:
    print(f"❌ Health check failed: {e}")
    sys.exit(1)
```

### Logging Configuration
```python
# logging_config.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
```

### Monitoring Script
```bash
#!/bin/bash
# monitor.sh
while true; do
    if ! python health_check.py; then
        echo "App is down, restarting..."
        # Restart command depends on your deployment method
        systemctl restart file-merger.service
    fi
    sleep 60
done
```

## 🐛 Troubleshooting

### ปัญหาที่พบบ่อย

#### 1. Port Already in Use
```bash
# หา process ที่ใช้ port 8501
sudo lsof -i :8501
# หรือ
sudo netstat -tulpn | grep :8501

# Kill process
sudo kill -9 <PID>
```

#### 2. Memory Issues
```bash
# เช็ค memory usage
free -h
htop

# เพิ่ม swap (Linux)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 3. File Upload Issues
```toml
# .streamlit/config.toml
[server]
maxUploadSize = 200
maxMessageSize = 200
```

####
