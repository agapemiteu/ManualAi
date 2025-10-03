#!/bin/bash
# ManualAi EC2 Deployment Script
# This script sets up ManualAi backend on a fresh Ubuntu EC2 instance

set -e

echo "=== ManualAi EC2 Setup Script ==="
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

echo "Installing Python 3.10 and pip..."
sudo apt-get install -y python3.10 python3.10-venv python3-pip

echo "Installing system dependencies for document processing..."
sudo apt-get install -y \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    libreoffice \
    pandoc

echo "Installing Docker (optional - for containerized deployment)..."
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

echo "Creating application directory..."
sudo mkdir -p /opt/manualai
sudo chown ubuntu:ubuntu /opt/manualai
cd /opt/manualai

echo "Cloning ManualAi repository..."
git clone https://github.com/agapemiteu/ManualAi.git .

echo "Setting up Python virtual environment..."
cd api
python3.10 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating data directories..."
mkdir -p ../data/uploads ../data/manual_store

echo "Setting up environment variables..."
cat > .env << EOF
CORS_ALLOW_ORIGINS=https://manual-ai-psi.vercel.app
PORT=8000
EOF

echo "Installing systemd service..."
sudo tee /etc/systemd/system/manualai.service > /dev/null << 'EOF'
[Unit]
Description=ManualAi FastAPI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/manualai/api
Environment="PATH=/opt/manualai/api/venv/bin"
ExecStart=/opt/manualai/api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Starting ManualAi service..."
sudo systemctl daemon-reload
sudo systemctl enable manualai
sudo systemctl start manualai

echo "Installing and configuring Nginx reverse proxy..."
sudo apt-get install -y nginx
sudo tee /etc/nginx/sites-available/manualai > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings for long-running requests
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/manualai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "ManualAi is now running on this EC2 instance!"
echo ""
echo "Service status: sudo systemctl status manualai"
echo "View logs: sudo journalctl -u manualai -f"
echo "Restart service: sudo systemctl restart manualai"
echo ""
echo "Your API should be accessible at: http://YOUR_EC2_PUBLIC_IP"
echo ""
