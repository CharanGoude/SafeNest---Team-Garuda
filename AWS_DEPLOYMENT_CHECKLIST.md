# 📋 SafeNest Pre-Deployment Checklist

## 🚀 AWS Deployment Quick Start

### Prerequisites (Before EC2 Setup)
- [ ] AWS account created
- [ ] EC2 key pair generated and saved locally (.pem file)
- [ ] Domain registered (e.g., safenest-garuda.com)
- [ ] Email address for SSL certificates
- [ ] GitHub account with access to SafeNest repo

---

## 🔧 Phase 1: AWS Console Setup (10 minutes)

### EC2 Instance Launch
- [ ] Go to AWS EC2 Dashboard
- [ ] Click "Launch Instance"
- [ ] Select Ubuntu 22.04 LTS (t3.medium minimum)
- [ ] Create/select key pair → save .pem file securely
- [ ] Create security group with rules:
  - [ ] SSH (22) - Your IP only
  - [ ] HTTP (80) - 0.0.0.0/0
  - [ ] HTTPS (443) - 0.0.0.0/0
- [ ] Launch instance
- [ ] Wait for "Running" status

### Get Instance Details
```bash
# After instance is running, get public IP:
AWS_INSTANCE_ID="i-xxxxxxxxx"  # From AWS Console
aws ec2 describe-instances --instance-ids $AWS_INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
```

### Domain DNS Configuration
- [ ] Log in to domain registrar
- [ ] Create A record pointing to EC2 public IP
- [ ] Wait 5-10 minutes for DNS propagation
- [ ] Verify: `nslookup safenest-garuda.com`

---

## 💻 Phase 2: SSH & Automated Setup (5 minutes)

### Connect to Instance
```bash
chmod 600 /path/to/safenest-key.pem
ssh -i /path/to/safenest-key.pem ubuntu@<PUBLIC_IP>
```

### Run Automated Setup Script
```bash
# Download setup script
curl -O https://raw.githubusercontent.com/CharanGoude/SafeNest---Team-Garuda/main/setup-safenest-aws.sh
chmod +x setup-safenest-aws.sh

# Run with domain and email
./setup-safenest-aws.sh safenest-garuda.com your-email@example.com

# Script will:
# ✓ Update system packages
# ✓ Install Python 3.10 & Node.js 18
# ✓ Clone SafeNest repo
# ✓ Setup Python virtual environment
# ✓ Build frontend
# ✓ Get SSL certificate
# ✓ Configure Nginx
# ✓ Setup Supervisor
# ✓ Configure backups
# ✓ Start services
```

---

## ✅ Phase 3: Verification (5 minutes)

### Test Backend
```bash
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"..."}
```

### Test API
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "X-API-Key: sk-safenest-demo-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TX_TEST_001",
    "amount": 50000,
    "currency": "INR",
    "merchant_name": "Test Merchant",
    "account_number": "****1234",
    "user_id": "USER_001",
    "location_country": "IN",
    "device_id": "device_001",
    "ip_address": "192.168.1.1",
    "is_new_device": false,
    "account_age_days": 500,
    "user_avg_transaction": 50000
  }'
```

### Access Dashboard
```bash
# From browser: https://safenest-garuda.com
# Or: https://<PUBLIC_IP>
```

### View Logs
```bash
# Backend logs
tail -f /var/log/safenest/backend-access.log

# Errors
tail -f /var/log/safenest/backend-error.log

# Supervisor status
sudo supervisorctl status
```

---

## 📊 Phase 4: Production Verification

### All Checks
- [ ] DNS resolves correctly: `nslookup safenest-garuda.com`
- [ ] Dashboard loads: https://safenest-garuda.com
- [ ] API responds: https://safenest-garuda.com/api/v1/health
- [ ] Backend logs show no errors
- [ ] SSL certificate valid (no browser warning)
- [ ] Supervisor showing safenest:* as RUNNING
- [ ] Nginx showing running processes

### Optional: Test Real-Time Features
```bash
# From your local machine:
cd backend
python simulator.py

# Or test webhook registration
curl -X POST https://safenest-garuda.com/api/v1/webhooks/register \
  -H "X-API-Key: sk-safenest-demo-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_name": "Test Bank",
    "webhook_url": "https://your-webhook-endpoint.com/webhook",
    "webhook_secret": "test-webhook-secret-12345"
  }'
```

---

## 🔐 Phase 5: Secure Production Setup

### Update API Keys
```bash
# SSH into instance
ssh -i safenest-key.pem ubuntu@<PUBLIC_IP>

# Edit backend environment
sudo nano /opt/safenest/backend/.env

# Change these values:
# - API_WORKERS=4 (based on CPU cores, e.g., t3.medium has 2 cores → 4 workers)
# - Add real GOOGLE_API_KEY if using AI features
# - Update ALLOWED_ORIGINS if using different domain

# Restart backend to apply changes
sudo supervisorctl restart safenest:*
```

### Monitor Performance
```bash
# SSH into instance
ssh -i safenest-key.pem ubuntu@<PUBLIC_IP>

# Check CPU/Memory
htop

# Check disk space
df -h

# Check backend workers
ps aux | grep uvicorn
```

### Setup Email Alerts (Optional)
```bash
sudo apt install -y mailutils

# Test email
echo "Test email from SafeNest" | mail -s "SafeNest Alert" your-email@example.com
```

---

## 📈 Scaling & Optimization

### If experiencing high load:

1. **Increase Workers**
```bash
sudo nano /etc/supervisor/conf.d/safenest.conf
# Change: command=/opt/safenest/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 8
sudo supervisorctl restart safenest:*
```

2. **Upgrade Instance Type**
```bash
# AWS Console → Stop instance → Change type → Start instance
# t3.medium → t3.large → t3.xlarge (as needed)
```

3. **Add Load Balancer** (for multi-instance)
```bash
# AWS Console → Create ELB/ALB → Add EC2 instances
```

4. **Migrate to RDS** (for database scaling)
```bash
# Create RDS PostgreSQL instance
# Update DATABASE_URL in .env
# Restart backend
```

---

## 🆘 Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| 502 Bad Gateway | `sudo supervisorctl status` | Restart: `sudo supervisorctl restart safenest:*` |
| DNS not resolving | `nslookup safenest-garuda.com` | Wait 10 mins, check A record |
| SSL certificate error | `sudo certbot certificates` | Renew: `sudo certbot renew` |
| Slow response | `htop` | Increase workers or upgrade instance |
| WebSocket not working | Nginx config | Ensure `proxy_upgrade` settings present |
| Database locked | Check logs | Restart backend |
| High memory usage | `ps aux | grep uvicorn` | Reduce workers or upgrade instance |

---

## 🚨 Emergency Restart

```bash
ssh -i safenest-key.pem ubuntu@<PUBLIC_IP>

# Full restart
sudo supervisorctl restart safenest:*
sudo systemctl restart nginx

# Or individual restarts
sudo systemctl restart nginx
sudo supervisorctl restart safenest-backend

# Check status
sudo supervisorctl status
sudo systemctl status nginx
```

---

## 📞 Support Resources

- **SafeNest Repo**: https://github.com/CharanGoude/SafeNest---Team-Garuda
- **AWS EC2 Docs**: https://docs.aws.amazon.com/ec2/
- **Let's Encrypt**: https://letsencrypt.org/
- **Nginx Docs**: https://nginx.org/en/docs/
- **Supervisor Docs**: http://supervisord.org/

---

## ✅ Final Checklist

- [ ] EC2 instance running
- [ ] Domain DNS configured
- [ ] Setup script executed successfully
- [ ] All services running (Nginx, Supervisor, Backend)
- [ ] Dashboard accessible
- [ ] API responding to requests
- [ ] SSL certificate valid
- [ ] Backups configured
- [ ] Logs being collected
- [ ] Production credentials updated
- [ ] Monitoring tools installed
- [ ] Team notified of live deployment

---

## 🎉 Success!

Your SafeNest fraud detection system is now live on AWS!

**Dashboard**: https://safenest-garuda.com
**API Endpoint**: https://safenest-garuda.com/api/v1/
**WebSocket**: wss://safenest-garuda.com/ws

Monitor transactions, detect fraud in real-time, and integrate with your bank's systems! 🚀
