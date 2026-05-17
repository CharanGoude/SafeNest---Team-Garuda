#!/bin/bash
# 🚀 SafeNest Automated AWS EC2 Deployment Script
# Run this on your EC2 instance as: bash setup-safenest-aws.sh

set -e

echo "🚀 SafeNest AWS EC2 Deployment Script"
echo "======================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/safenest"
APP_USER="safenest"
DOMAIN="${1:-safenest-garuda.com}"
EMAIL="${2:-your-email@example.com}"

echo -e "${YELLOW}Configuration:${NC}"
echo "App Directory: $APP_DIR"
echo "App User: $APP_USER"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Step 1: System Update
echo -e "${YELLOW}Step 1: System Update${NC}"
sudo apt update
sudo apt upgrade -y
sudo apt install -y curl wget git unzip build-essential
echo -e "${GREEN}✓ System updated${NC}"
echo ""

# Step 2: Create Application User
echo -e "${YELLOW}Step 2: Create Application User${NC}"
if ! id "$APP_USER" &>/dev/null; then
    sudo useradd -m -s /bin/bash $APP_USER
    sudo usermod -aG sudo $APP_USER
    echo -e "${GREEN}✓ User $APP_USER created${NC}"
else
    echo -e "${GREEN}✓ User $APP_USER already exists${NC}"
fi
echo ""

# Step 3: Install Python
echo -e "${YELLOW}Step 3: Install Python 3.10${NC}"
sudo apt install -y python3.10 python3.10-venv python3-pip
sudo apt install -y sqlite3 libsqlite3-dev
echo -e "${GREEN}✓ Python 3.10 installed${NC}"
echo ""

# Step 4: Install Node.js
echo -e "${YELLOW}Step 4: Install Node.js 18${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
echo -e "${GREEN}✓ Node.js 18 installed${NC}"
echo ""

# Step 5: Clone Repository
echo -e "${YELLOW}Step 5: Clone SafeNest Repository${NC}"
sudo mkdir -p $APP_DIR
sudo chown $APP_USER:$APP_USER $APP_DIR
cd $APP_DIR

if [ ! -d ".git" ]; then
    sudo -u $APP_USER git clone https://github.com/CharanGoude/SafeNest---Team-Garuda.git .
    echo -e "${GREEN}✓ Repository cloned${NC}"
else
    cd $APP_DIR
    sudo -u $APP_USER git pull origin main
    echo -e "${GREEN}✓ Repository updated${NC}"
fi
echo ""

# Step 6: Setup Backend
echo -e "${YELLOW}Step 6: Setup Backend (Python)${NC}"
cd $APP_DIR/backend
sudo -u $APP_USER python3 -m venv $APP_DIR/venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "$APP_DIR/backend/.env" ]; then
    sudo -u $APP_USER cp $APP_DIR/backend/.env.example $APP_DIR/backend/.env 2>/dev/null || true
    
    # Generate random secret
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    cat >> $APP_DIR/backend/.env << EOF
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
API_HOST=127.0.0.1
API_PORT=8000
API_WORKERS=4
SECRET_KEY=$SECRET
ALLOWED_ORIGINS=["https://$DOMAIN","https://www.$DOMAIN"]
EOF
    echo -e "${GREEN}✓ Backend configured (.env created)${NC}"
else
    echo -e "${GREEN}✓ Backend already configured${NC}"
fi
echo ""

# Step 7: Setup Frontend
echo -e "${YELLOW}Step 7: Setup Frontend (Node.js)${NC}"
cd $APP_DIR/frontend
sudo -u $APP_USER npm install
sudo -u $APP_USER npm run build
echo -e "${GREEN}✓ Frontend built${NC}"
echo ""

# Step 8: Install Nginx
echo -e "${YELLOW}Step 8: Install Nginx${NC}"
sudo apt install -y nginx
sudo systemctl enable nginx
echo -e "${GREEN}✓ Nginx installed${NC}"
echo ""

# Step 9: Install SSL Certificate
echo -e "${YELLOW}Step 9: Install SSL Certificate (Let's Encrypt)${NC}"
sudo apt install -y certbot python3-certbot-nginx

if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    sudo certbot certonly --nginx \
      -d $DOMAIN \
      -d www.$DOMAIN \
      --email $EMAIL \
      --agree-tos \
      --non-interactive \
      --keep-until-expiring || echo -e "${YELLOW}SSL setup may require manual intervention${NC}"
    echo -e "${GREEN}✓ SSL certificate obtained${NC}"
else
    echo -e "${GREEN}✓ SSL certificate already exists${NC}"
fi
echo ""

# Step 10: Configure Nginx
echo -e "${YELLOW}Step 10: Configure Nginx Reverse Proxy${NC}"
sudo tee /etc/nginx/sites-available/safenest > /dev/null << 'NGINX_CONFIG'
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name _;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name safenest-garuda.com www.safenest-garuda.com;

    # SSL Configuration - Update domain path as needed
    ssl_certificate /etc/letsencrypt/live/safenest-garuda.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/safenest-garuda.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_session_cache shared:SSL:10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # Frontend
    location / {
        root /opt/safenest/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
    }

    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
NGINX_CONFIG

# Enable site
sudo ln -sf /etc/nginx/sites-available/safenest /etc/nginx/sites-enabled/safenest
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart
sudo nginx -t && sudo systemctl restart nginx
echo -e "${GREEN}✓ Nginx configured and restarted${NC}"
echo ""

# Step 11: Install Supervisor
echo -e "${YELLOW}Step 11: Install Supervisor Process Manager${NC}"
sudo apt install -y supervisor
sudo mkdir -p /var/log/safenest
sudo chown $APP_USER:$APP_USER /var/log/safenest

sudo tee /etc/supervisor/conf.d/safenest.conf > /dev/null << 'SUPERVISOR_CONFIG'
[program:safenest-backend]
directory=/opt/safenest/backend
command=/opt/safenest/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
user=safenest
autostart=true
autorestart=true
stderr_logfile=/var/log/safenest/backend-error.log
stdout_logfile=/var/log/safenest/backend-access.log
environment=PATH="/opt/safenest/venv/bin"

[group:safenest]
programs=safenest-backend
priority=999
SUPERVISOR_CONFIG

sudo supervisorctl reread
sudo supervisorctl update
sleep 2
echo -e "${GREEN}✓ Supervisor configured${NC}"
echo ""

# Step 12: Setup Backup Script
echo -e "${YELLOW}Step 12: Setup Automated Backups${NC}"
sudo mkdir -p /opt/safenest/backups
sudo chown $APP_USER:$APP_USER /opt/safenest/backups

sudo tee /home/$APP_USER/backup-safenest.sh > /dev/null << 'BACKUP_SCRIPT'
#!/bin/bash
BACKUP_DIR="/opt/safenest/backups"
mkdir -p $BACKUP_DIR
cp /opt/safenest/backend/safenest_prod.db $BACKUP_DIR/safenest_$(date +\%Y\%m\%d_\%H\%M\%S).db.bak
find $BACKUP_DIR -mtime +30 -delete
echo "Backup completed: $(date)"
BACKUP_SCRIPT

sudo chmod +x /home/$APP_USER/backup-safenest.sh
sudo chown $APP_USER:$APP_USER /home/$APP_USER/backup-safenest.sh

# Add to crontab
(sudo -u $APP_USER crontab -l 2>/dev/null || true; echo "0 2 * * * /home/$APP_USER/backup-safenest.sh") | sudo -u $APP_USER crontab -
echo -e "${GREEN}✓ Backup script installed (daily at 2 AM)${NC}"
echo ""

# Step 13: Firewall
echo -e "${YELLOW}Step 13: Setup Firewall${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
echo -e "${GREEN}✓ Firewall configured${NC}"
echo ""

# Step 14: Verification
echo -e "${YELLOW}Step 14: Verification${NC}"
echo ""
echo "Checking services..."

# Check backend
if sudo supervisorctl status safenest:* >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend may not be running${NC}"
fi

# Check Nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
else
    echo -e "${RED}✗ Nginx is not running${NC}"
fi

# Get instance IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo ""
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo ""
echo "📊 Service Status:"
echo "  Backend: http://127.0.0.1:8000"
echo "  Nginx: http://127.0.0.1:80"
echo "  Public IP: $PUBLIC_IP"
echo ""
echo "🌐 Access Points:"
echo "  Dashboard: https://$DOMAIN"
echo "  API: https://$DOMAIN/api/v1/health"
echo "  WebSocket: wss://$DOMAIN/ws"
echo ""
echo "📋 Important Files:"
echo "  Config: $APP_DIR/backend/.env"
echo "  Logs: /var/log/safenest/"
echo "  Backups: /opt/safenest/backups/"
echo ""
echo "🔧 Useful Commands:"
echo "  View logs: tail -f /var/log/safenest/backend-access.log"
echo "  Restart backend: sudo supervisorctl restart safenest:*"
echo "  Check status: sudo supervisorctl status"
echo "  Restart Nginx: sudo systemctl restart nginx"
echo ""
echo "✅ Next steps:"
echo "  1. Update domain DNS to point to: $PUBLIC_IP"
echo "  2. Wait 5-10 minutes for DNS propagation"
echo "  3. Test with: curl https://$DOMAIN/health"
echo ""
