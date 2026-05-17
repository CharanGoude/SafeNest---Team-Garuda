# 🚀 SafeNest v2.0.1 — Production Deployment Guide

## Pre-Deployment Checklist

### Infrastructure Requirements

- [ ] Ubuntu 22.04 LTS or similar Linux server
- [ ] 2+ CPU cores, 4GB+ RAM minimum
- [ ] 20GB+ disk space
- [ ] HTTPS/SSL certificate (Let's Encrypt recommended)
- [ ] Firewall rules configured (80, 443, 8000 for API)
- [ ] Database backup system in place
- [ ] Monitoring tools (Prometheus, Grafana optional)
- [ ] Log aggregation (ELK Stack optional)

### Security Checklist

- [ ] Database encryption enabled
- [ ] API keys rotated and secured in .env
- [ ] CORS properly configured for bank domains
- [ ] Rate limiting configured
- [ ] DDoS protection enabled
- [ ] Regular security patches scheduled
- [ ] Backup and disaster recovery tested
- [ ] Compliance audit completed (PCI-DSS if needed)

---

## 1️⃣ Server Setup

### Step 1: Install Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.10+
sudo apt-get install -y python3.10 python3.10-venv python3-pip

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install other dependencies
sudo apt-get install -y git nginx supervisor certbot python3-certbot-nginx
```

### Step 2: Clone Repository

```bash
cd /opt
sudo git clone https://github.com/CharanGoude/SafeNest---Team-Garuda.git safenest
cd safenest
sudo chown -R $USER:$USER .
```

### Step 3: Setup Backend

```bash
cd backend
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create production .env file
cat > .env << EOF
DATABASE_URL=safenest_prod.db
GOOGLE_API_KEY=your-gemini-api-key
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF

chmod 600 .env
```

### Step 4: Setup Frontend

```bash
cd ../frontend
npm install
npm run build
# Creates optimized build in dist/
```

---

## 2️⃣ Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/safenest`:

```nginx
upstream safenest_backend {
    server 127.0.0.1:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Frontend (React)
    location / {
        root /opt/safenest/frontend/dist;
        try_files $uri $uri/ /index.html;
        gzip on;
        gzip_types text/plain text/css application/json application/javascript;
    }
    
    # API Backend
    location /api {
        proxy_pass http://safenest_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        
        # Timeouts for long-running requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://safenest_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
    
    # API Documentation
    location /docs {
        proxy_pass http://safenest_backend;
        proxy_set_header Host $host;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/safenest /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 3️⃣ Setup SSL Certificate

```bash
# Install Let's Encrypt certificate
sudo certbot certonly --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## 4️⃣ Configure Supervisor for Backend

Create `/etc/supervisor/conf.d/safenest.conf`:

```ini
[program:safenest]
directory=/opt/safenest/backend
command=/opt/safenest/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/safenest.log
environment=PATH="/opt/safenest/backend/venv/bin",ENVIRONMENT="production"

[group:safenest]
programs=safenest
```

Enable Supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start safenest
```

---

## 5️⃣ Database Setup for Production

```bash
cd /opt/safenest/backend

# Initialize production database
python3 << EOF
from agents.db.database import db
db.init_db()
print("✅ Production database initialized")
EOF

# Backup database daily
cat > /opt/safenest/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/safenest/backups"
mkdir -p $BACKUP_DIR
cp /opt/safenest/backend/safenest_prod.db $BACKUP_DIR/safenest_$(date +%Y%m%d_%H%M%S).db.bak
# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete
EOF

chmod +x /opt/safenest/backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/safenest/backup.sh") | crontab -
```

---

## 6️⃣ Production Configuration

Create `.env.production`:

```bash
# Environment
ENVIRONMENT=production

# Database
DATABASE_URL=safenest_prod.db
DATABASE_BACKUP_ENABLED=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# CORS (Configure for your bank domains)
CORS_ORIGINS=["https://your-domain.com", "https://bank1.com", "https://bank2.com"]

# Security
SECRET_KEY=your-very-long-random-secret-key-min-32-chars
API_KEY_PREFIX=sk-prod-
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/safenest.log

# Gemini AI (Optional)
GOOGLE_API_KEY=your-gemini-api-key

# Webhook Configuration
WEBHOOK_TIMEOUT=10
WEBHOOK_RETRIES=3
WEBHOOK_SIGNATURE_ALGORITHM=sha256

# Performance
CACHE_ENABLED=true
CACHE_TTL=300
DATABASE_POOL_SIZE=20
```

---

## 7️⃣ Monitoring & Logging

### Setup Structured Logging

```bash
# Install monitoring tools
pip install prometheus-client python-json-logger

# View logs
tail -f /var/log/safenest.log
journalctl -u safenest -f
```

### Health Check Endpoint

```bash
# Check system health
curl https://your-domain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-17T15:30:46Z",
  "uptime_seconds": 86400,
  "transactions_analyzed": 45230,
  "database_status": "connected",
  "api_version": "2.0.1"
}
```

---

## 8️⃣ Firewall Configuration

```bash
# UFW (Ubuntu Firewall)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Fail2Ban for DDoS protection
sudo apt-get install -y fail2ban

# Create jail config
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
EOF

sudo systemctl restart fail2ban
```

---

## 9️⃣ Performance Tuning

### Database Connection Pooling

```python
# In main.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///safenest_prod.db',
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
    echo=False
)
```

### Caching Strategy

```python
# Redis caching for fraud scores
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

# Cache fraud scores for 5 minutes
cache.setex(f"fraud_score:{user_id}", 300, score)
```

### Load Balancing (Multiple Servers)

```nginx
upstream safenest_backend {
    server backend1.internal:8000;
    server backend2.internal:8000;
    server backend3.internal:8000;
    
    # Least connections method
    least_conn;
}
```

---

## 🔟 Scaling Strategy

### Horizontal Scaling (Multiple Servers)

```
Load Balancer (Nginx/HAProxy)
    │
    ├─ Backend Server 1
    ├─ Backend Server 2
    ├─ Backend Server 3
    └─ Backend Server 4
    
Shared:
    ├─ PostgreSQL Database (RDS)
    ├─ Redis Cache
    └─ File Storage (S3)
```

### Recommended AWS Architecture

```
CloudFront (CDN) → Application Load Balancer (ALB)
    │
    ├─ EC2 Auto-scaling group (Backend)
    │   ├─ 2-4 t3.medium instances
    │   └─ Auto-scale: 1000-2000 TPS
    │
    ├─ RDS PostgreSQL (Database)
    │   ├─ Multi-AZ for high availability
    │   └─ Read replicas for scaling reads
    │
    ├─ ElastiCache (Redis)
    │   └─ Cache layer for fraud scores
    │
    └─ S3 + CloudFront (Frontend)
        └─ Static React build
```

---

## ✅ Post-Deployment Checklist

- [ ] All services running: `sudo supervisorctl status`
- [ ] Nginx working: `curl https://your-domain.com`
- [ ] API responding: `curl https://your-domain.com/health`
- [ ] WebSocket working: Check dashboard loads
- [ ] Database accessible: Test transaction insertion
- [ ] SSL certificate valid: `sudo certbot certificates`
- [ ] Backups scheduled: `crontab -l`
- [ ] Monitoring active: Check logs flowing
- [ ] Webhook endpoints registered with all banks
- [ ] Rate limiting active
- [ ] DDoS protection enabled
- [ ] Incident response plan activated

---

## 🚨 Emergency Procedures

### Restart Services

```bash
# Restart backend
sudo supervisorctl restart safenest

# Restart Nginx
sudo systemctl restart nginx

# Full system restart
sudo reboot
```

### View Logs

```bash
# Backend logs
tail -100f /var/log/safenest.log

# Nginx logs
tail -100f /var/log/nginx/error.log
tail -100f /var/log/nginx/access.log

# System logs
sudo journalctl -u safenest -n 50 -f
```

### Rollback to Previous Version

```bash
cd /opt/safenest
git log --oneline
git checkout <previous-commit>
cd backend && venv/bin/pip install -r requirements.txt
sudo supervisorctl restart safenest
```

---

## 📊 Monitoring Queries

### Check Performance

```bash
# Transactions analyzed per hour
sqlite3 safenest_prod.db "
  SELECT DATE(timestamp), COUNT(*) as count 
  FROM transactions 
  GROUP BY DATE(timestamp) 
  ORDER BY timestamp DESC LIMIT 30;"

# Fraud detection accuracy
sqlite3 safenest_prod.db "
  SELECT action, COUNT(*) as count 
  FROM transactions 
  GROUP BY action;"

# Average processing time
sqlite3 safenest_prod.db "
  SELECT AVG(processing_time_ms) as avg_ms, 
         MAX(processing_time_ms) as max_ms 
  FROM transactions;"
```

### Alert Thresholds

Set alerts for:
- CPU usage > 80%
- Memory usage > 85%
- Error rate > 1%
- Response time > 1000ms
- Database connections > 80%

---

## 🔄 Continuous Deployment (Optional)

```bash
# GitHub Actions workflow (.github/workflows/deploy.yml)
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_SERVER }}
          username: deploy
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /opt/safenest
            git pull origin main
            cd frontend && npm install && npm run build
            cd ../backend && pip install -r requirements.txt
            sudo supervisorctl restart safenest
            echo "✅ Deployed successfully"
```

---

## 📞 Support Resources

- **Nginx Docs**: https://nginx.org/en/docs/
- **Supervisor Docs**: http://supervisord.org/
- **Let's Encrypt**: https://letsencrypt.org/
- **Ubuntu Security**: https://help.ubuntu.com/
- **Performance Tuning**: https://wiki.nginx.org/Tuning

---

## 🎯 Next Steps

1. Provision production server
2. Follow Steps 1-5 for basic setup
3. Configure Nginx (Step 6)
4. Setup SSL (Step 7)
5. Test thoroughly in staging first
6. Deploy to production during maintenance window
7. Monitor closely for 24 hours
8. Setup automated backups

**Production is ready!** 🚀
