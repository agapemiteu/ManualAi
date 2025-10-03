# AWS EC2 Deployment Guide for ManualAi

## Quick Start Steps

### 1. Launch EC2 Instance

1. Go to [AWS EC2 Console](https://console.aws.amazon.com/ec2/)
2. Click **"Launch Instance"**
3. Configure:
   - **Name**: `ManualAi-Backend`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance type**: `t2.micro` or `t3.micro` (Free tier: 750 hours/month)
   - **Key pair**: Create new or select existing (download .pem file!)
   - **Security Group**: Create new with these rules:
     - SSH (22) - Your IP only
     - HTTP (80) - Anywhere (0.0.0.0/0)
     - HTTPS (443) - Anywhere (0.0.0.0/0) [optional]
   - **Storage**: 20 GB gp3 (minimum for ML models and vector DB)

4. Click **"Launch Instance"**

### 2. Connect to Your Instance

#### On Windows (PowerShell):
```powershell
# Set correct permissions for .pem file
icacls "your-key.pem" /inheritance:r
icacls "your-key.pem" /grant:r "$($env:USERNAME):(R)"

# Connect via SSH
ssh -i "your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

#### On Mac/Linux:
```bash
chmod 400 your-key.pem
ssh -i "your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

### 3. Run Deployment Script

Once connected to EC2:

```bash
# Download and run the setup script
curl -O https://raw.githubusercontent.com/agapemiteu/ManualAi/main/deploy-ec2.sh
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

**OR** manually copy the script:

```bash
nano deploy-ec2.sh
# Paste the content from deploy-ec2.sh
# Press Ctrl+X, Y, Enter to save

chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

The script will take **5-10 minutes** to:
- Install Python and dependencies
- Clone your repository
- Install ML models
- Set up systemd service
- Configure Nginx reverse proxy

### 4. Verify Deployment

Check if the service is running:
```bash
sudo systemctl status manualai
```

View logs:
```bash
sudo journalctl -u manualai -f
```

Test the API:
```bash
curl http://localhost:8000/
```

### 5. Get Your Public URL

Your backend will be available at:
```
http://YOUR_EC2_PUBLIC_IP
```

Find your public IP:
```bash
curl http://checkip.amazonaws.com
```

Or check in AWS Console → EC2 → Instances → Your instance → Public IPv4 address

## Update Vercel Frontend

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your `manual-ai` project
3. Go to **Settings** → **Environment Variables**
4. Update `NEXT_PUBLIC_API_URL`:
   - Value: `http://YOUR_EC2_PUBLIC_IP`
5. Go to **Deployments** → **Redeploy**

## Manage Your Instance

### Start/Stop/Restart Service
```bash
sudo systemctl start manualai    # Start
sudo systemctl stop manualai     # Stop
sudo systemctl restart manualai  # Restart
sudo systemctl status manualai   # Check status
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u manualai -f

# Last 100 lines
sudo journalctl -u manualai -n 100
```

### Update Code
```bash
cd /opt/manualai
git pull
sudo systemctl restart manualai
```

### Stop EC2 to Save Credits
When not using:
1. Go to AWS Console → EC2 → Instances
2. Select your instance
3. **Instance State** → **Stop instance**
4. Start again when needed (public IP will change unless you use Elastic IP)

## Cost Management

### Free Tier Usage (First 12 months):
- **750 hours/month** of t2.micro or t3.micro (one instance running 24/7)
- **30 GB EBS storage**
- **15 GB data transfer out**

### Estimated Monthly Cost (after free tier):
- **t2.micro instance**: ~$8-10/month (24/7)
- **Storage (20 GB)**: ~$2/month
- **Data transfer**: Minimal for demo usage
- **Total**: ~$10-12/month

### Your $100 Credit = 8-10 months of 24/7 operation!

### Save Even More:
- **Stop instance when not in use** (nights/weekends)
- **Use Elastic IP** ($0/month when attached and instance running)
- **Set up CloudWatch alarms** for billing alerts

## Optional: Set Up Domain Name

If you want a custom domain instead of IP address:

1. Get a free domain from [Freenom](https://freenom.com) or use your own
2. Point A record to your EC2 public IP (or Elastic IP)
3. Update CORS in `/opt/manualai/api/.env`:
   ```bash
   CORS_ALLOW_ORIGINS=https://manual-ai-psi.vercel.app,http://yourdomain.com
   ```
4. Restart: `sudo systemctl restart manualai`

## Optional: Add HTTPS (SSL/TLS)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
```

## Troubleshooting

### Service won't start:
```bash
# Check detailed logs
sudo journalctl -u manualai -xe

# Check if port 8000 is in use
sudo lsof -i :8000

# Test manually
cd /opt/manualai/api
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Out of disk space:
```bash
# Check disk usage
df -h

# Clean up
sudo apt-get autoremove
sudo apt-get clean
```

### Can't connect from browser:
1. Check security group allows HTTP (port 80) from 0.0.0.0/0
2. Check Nginx is running: `sudo systemctl status nginx`
3. Check instance public IP hasn't changed

## Monitoring

### Check resource usage:
```bash
# CPU and memory
htop

# Disk usage
df -h

# Service resource usage
sudo systemctl status manualai
```

### Set up CloudWatch (optional):
- AWS Console → CloudWatch → Alarms
- Create alarm for CPU > 80% or billing > $50

## Support

If you encounter issues:
1. Check logs: `sudo journalctl -u manualai -f`
2. Verify security groups in AWS Console
3. Test API locally: `curl http://localhost:8000`
4. Check GitHub issues: https://github.com/agapemiteu/ManualAi/issues
