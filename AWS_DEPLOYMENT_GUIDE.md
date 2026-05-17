# 🚀 AWS EC2 Production Deployment Guide for SafeNest

**Domain:** safenest-garuda
**Platform:** AWS EC2
**OS:** Ubuntu 22.04 LTS
**Estimated Setup Time:** 30-45 minutes

---

## 📋 Pre-Deployment Checklist

- [ ] AWS account created
- [ ] EC2 key pair generated (.pem file)
- [ ] Security group created with ports 22 (SSH), 80 (HTTP), 443 (HTTPS) open
- [ ] Domain registered (e.g., safenest-garuda.com)
- [ ] Domain DNS pointing to EC2 instance IP
- [ ] GitHub repository cloned (https://github.com/CharanGoude/SafeNest---Team-Garuda)

---

## 🔧 Step 1: Launch EC2 Instance

### 1a. In AWS Console:
1. Go to **EC2 → Instances → Launch Instance**
2. **Name:** SafeNest-Prod
3. **AMI:** Ubuntu 22.04 LTS (ami-0c55b159cbfafe1f0)
4. **Instance Type:** `t3.medium` (minimum recommended)
   - 2 vCPU, 4GB RAM, ~$25/month
   - For high traffic: upgrade to `t3.large` or `m5.large`
5. **Key Pair:** Create new or select existing `.pem` file
6. **Security Group:** Create with inbound rules:
   ```
   SSH (22) - From Your IP
   HTTP (80) - From 0.0.0.0/0
   HTTPS (443) - From 0.0.0.0/0
   ```
7. **Storage:** 30GB gp3 (minimum)
8. **Launch Instance**

### 1b. Get Instance Details:
```bash
# After instance is running:
INSTANCE_IP=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=SafeNest-Prod" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Instance IP: $INSTANCE_IP"
```

---

## 🔐 Step 2: Configure Domain DNS

### 2a. Create A Record:
Go to your domain registrar (Namecheap, GoDaddy, Route53, etc.):

```
Type: A Record
Name: @ (or subdomain like api)
Value: <Your EC2 Public IP>
TTL: 300 (5 minutes)
```

**Example DNS Records:**
```
Record        Type    Value              TTL
@             A       52.1.2.3           300
safenest      A       52.1.2.3           300
api           A       52.1.2.3           300
www           CNAME   @                  300
```

### 2b. Verify DNS:
```bash
# Wait 5-10 minutes, then test:
nslookup safenest-garuda.com
# Should resolve to your EC2 IP
```

---

## 💻 Step 3: SSH Into Instance & Initial Setup

### 3a. Connect via SSH:
```bash
chmod 600 /path/to/safenest-key.pem
ssh -i /path/to/safenest-key.pem ubuntu@52.1.2.3
```

### 3b. System Update:
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y curl wget git unzip

# Enable UFW firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 3c. Create Application User:
```bash
sudo useradd -m -s /bin/bash safenest
sudo usermod -aG sudo safenest

# Switch to safenest user
sudo su - safenest
```

---

## 🐍 Step 4: Install Python & Dependencies

```bash
sudo apt install -y python3.10 python3.10-venv python3-pip
python3 --version  # Verify Python 3.10+

# Install system dependencies for database
sudo apt install -y sqlite3 libsqlite3-dev

# Create app directory
mkdir -p /opt/safenest
cd /opt/safenest
```

---

## 📦 Step 5: Clone Repository & Setup Backend

```bash
cd /opt/safenest
git clone https://github.com/CharanGoude/SafeNest---Team-Garuda.git .

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with production settings
nano .env
```

**Add to `.env`:**
```env
# SafeNest Production Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Database
DATABASE_URL=sqlite:///safenest_prod.db
DATABASE_TIMEOUT=30

# Security
SECRET_KEY=your-random-32-char-secret-here
ALLOWED_ORIGINS=["https://safenest-garuda.com", "https://www.safenest-garuda.com"]

# Optional: Gemini API for AI analysis
GOOGLE_API_KEY=your-gemini-api-key-here

# CORS Settings
CORS_ALLOW_CREDENTIALS=true
```

Generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🟢 Step 6: Install Node.js & Frontend

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version  # v18.x
npm --version   # 9.x

# Build frontend
cd /opt/safenest/frontend
npm install

# Build for production
npm run build

# Output should be in /opt/safenest/frontend/dist/
```

---

## 🔒 Step 7: SSL Certificate with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx

# Create certificate
sudo certbot certonly --standalone \
  -d safenest-garuda.com \
  -d www.safenest-garuda.com \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive

# Certificate path: /etc/letsencrypt/live/safenest-garuda.com/
# Expires in 90 days (auto-renewal via systemd)

# Verify auto-renewal
sudo systemctl status certbot.timer
```

---

## 🌐 Step 8: Nginx Reverse Proxy Setup

### 8a. Install Nginx:
```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 8b. Create Nginx Config:
```bash
sudo nano /etc/nginx/sites-available/safenest
```

**Paste this configuration:**
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name safenest-garuda.com www.safenest-garuda.com;
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name safenest-garuda.com www.safenest-garuda.com;

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/safenest-garuda.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/safenest-garuda.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 1000;

    # Frontend
    location / {
        root /opt/safenest/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeouts
        proxy_read_timeout 86400;
    }

    # Health Check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
}
```

### 8c. Enable Site & Test:
```bash
sudo ln -s /etc/nginx/sites-available/safenest /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

---

## 🔄 Step 9: Setup Supervisor for Process Management

### 9a. Install Supervisor:
```bash
sudo apt install -y supervisor
```

### 9b. Create Supervisor Config:
```bash
sudo nano /etc/supervisor/conf.d/safenest.conf
```

**Paste this:**
```ini
[program:safenest-backend]
directory=/opt/safenest/backend
command=/opt/safenest/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
user=safenest
autostart=true
autorestart=true
stderr_logfile=/var/log/safenest/backend-error.log
stdout_logfile=/var/log/safenest/backend-access.log
environment=PATH="/opt/safenest/venv/bin",DATABASE_URL="sqlite:///safenest_prod.db"

[group:safenest]
programs=safenest-backend
priority=999
```

### 9c. Setup Logging:
```bash
sudo mkdir -p /var/log/safenest
sudo chown safenest:safenest /var/log/safenest
sudo chmod 755 /var/log/safenest
```

### 9d. Start Services:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start safenest:*

# Check status
sudo supervisorctl status
```

---

## 💾 Step 10: Database Backup Strategy

### 10a. Create Backup Script:
```bash
cat > ~/backup-safenest.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/safenest/backups"
mkdir -p $BACKUP_DIR

# Backup database
cp /opt/safenest/backend/safenest_prod.db $BACKUP_DIR/safenest_$(date +%Y%m%d_%H%M%S).db.bak

# Keep only last 30 days of backups
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/safenest_$(date +%Y%m%d_%H%M%S).db.bak"
EOF

chmod +x ~/backup-safenest.sh
```

### 10b. Schedule Daily Backups:
```bash
crontab -e

# Add this line:
0 2 * * * /home/safenest/backup-safenest.sh
```

---

## 📊 Step 11: Monitoring & Logging

### 11a. Install Monitoring Tools:
```bash
# System monitoring
sudo apt install -y htop iotop nethogs

# Log aggregation (optional but recommended)
sudo apt install -y logwatch
```

### 11b. Check Application Logs:
```bash
# Real-time backend logs
tail -f /var/log/safenest/backend-access.log

# Error logs
tail -f /var/log/safenest/backend-error.log

# System logs
sudo journalctl -u nginx -f
```

### 11c. Setup Log Rotation:
```bash
sudo nano /etc/logrotate.d/safenest
```

**Paste:**
```
/var/log/safenest/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 640 safenest safenest
    sharedscripts
    postrotate
        sudo supervisorctl restart safenest:* > /dev/null
    endscript
}
```

---

## 🧪 Step 12: Verification & Testing

### 12a. Health Check:
```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend is served
curl https://safenest-garuda.com

# Check API endpoint
curl https://safenest-garuda.com/api/v1/health
```

### 12b. Full Workflow Test:
```bash
# Analyze a transaction
curl -X POST https://safenest-garuda.com/api/v1/analyze \
  -H "X-API-Key: sk-safenest-demo-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TX_PROD_001",
    "amount": 50000,
    "currency": "INR",
    "merchant_name": "Test Merchant",
    "account_number": "****1234",
    "user_id": "USER_PROD_001",
    "location_country": "IN",
    "device_id": "device_prod_001",
    "ip_address": "192.168.1.1",
    "is_new_device": false,
    "account_age_days": 500,
    "user_avg_transaction": 50000
  }'

# Expected response: action "APPROVE", risk_level "LOW"
```

### 12c. WebSocket Test:
```bash
# From browser console at https://safenest-garuda.com
const ws = new WebSocket('wss://safenest-garuda.com/ws');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({test: true}));
```

---

## 🚨 Step 13: Post-Deployment

### 13a. Update DNS Records (if needed):
```bash
# Verify domain resolution
nslookup safenest-garuda.com
dig safenest-garuda.com

# Should show your EC2 IP
```

### 13b. Setup Email Alerts (Optional):
```bash
# Install mail utilities
sudo apt install -y mailutils

# Test mail
echo "Test" | mail -s "SafeNest Alert Test" your-email@example.com
```

### 13c. Document Production Credentials:
Keep these in a secure location:
```
Domain: safenest-garuda.com
EC2 Instance ID: i-xxxxxxxxx
Public IP: 52.1.2.3
SSH Key: /path/to/safenest-key.pem
SSL Certificate: /etc/letsencrypt/live/safenest-garuda.com/
Database: /opt/safenest/backend/safenest_prod.db
Backend Port: 127.0.0.1:8000 (private)
Frontend: /opt/safenest/frontend/dist/
API Key: sk-safenest-demo-key-2026 (CHANGE THIS!)
```

---

## 🔄 Scaling & Performance

### Scale to Multiple Instances:
```bash
# Update Supervisor to use more workers
workers=8  # Adjust based on CPU cores

# Use RDS for database (instead of SQLite)
# Use CloudFront for CDN
# Use ELB/ALB for load balancing
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check backend: `sudo supervisorctl status` |
| SSL Certificate Error | Renew: `sudo certbot renew` |
| High CPU Usage | Increase workers: `workers=8` |
| Database Locked | Restart backend: `sudo supervisorctl restart safenest:*` |
| WebSocket Not Working | Check Nginx config has proxy_upgrade settings |
| Slow Response Times | Check logs, increase worker count, upgrade instance |

---

## ✅ Deployment Checklist

- [ ] EC2 instance launched and running
- [ ] Domain DNS pointing to instance
- [ ] SSH access verified
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Git repository cloned
- [ ] .env configured with production settings
- [ ] Frontend built (npm run build)
- [ ] SSL certificate obtained via Let's Encrypt
- [ ] Nginx configured and running
- [ ] Supervisor managing backend process
- [ ] Health checks passing
- [ ] Full workflow tested
- [ ] Backups configured
- [ ] Monitoring tools installed
- [ ] Production credentials documented

---

## 📞 Support

For issues:
1. Check logs: `/var/log/safenest/`
2. Check process status: `sudo supervisorctl status`
3. Test connectivity: `curl https://safenest-garuda.com/api/v1/health`
4. Review configuration files

**Emergency Restart:**
```bash
sudo supervisorctl restart safenest:*
sudo systemctl restart nginx
```

---

## 🎉 Congratulations!

Your SafeNest fraud detection system is now live on AWS! 
- Dashboard: https://safenest-garuda.com
- API: https://safenest-garuda.com/api/v1/
- Health: https://safenest-garuda.com/health

Monitor transactions, configure webhooks, and watch fraud detection in action! 🚀
