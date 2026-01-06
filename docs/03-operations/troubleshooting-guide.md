# TROUBLESHOOTING GUIDE

**Debian VPS Configurator - Problem Diagnosis & Resolution**
**Comprehensive Solutions for Common Issues**
**Date:** January 6, 2026

---

## 🎯 OVERVIEW

This guide provides **step-by-step troubleshooting procedures** for diagnosing and resolving common issues with Debian VPS Configurator.

**How to Use This Guide:**

1. Find your problem in the Table of Contents
2. Follow the diagnostic steps
3. Apply the solution
4. Verify the fix
5. Document what worked

**When to Use:**

- Something isn't working as expected
- Error messages appear
- Performance issues
- Users reporting problems

---

## 📋 QUICK REFERENCE

### By Symptom

| Problem             | Section                                       |
| ------------------- | --------------------------------------------- |
| Won't install       | [Installation Fails](#installation-fails)     |
| Config error        | [Configuration Errors](#configuration-errors) |
| Permission denied   | [Permission Denied](#permission-denied)       |
| Service won't start | [Service Won't Start](#service-wont-start)    |
| High CPU/Memory     | [High Usage](#high-cpu-usage)                 |
| User can't login    | [User Cannot Login](#user-cannot-login)       |
| SSH key issues      | [SSH Key Not Working](#ssh-key-not-working)   |
| 2FA code rejected   | [2FA Rejected](#2fa-rejected)                 |
| Backup fails        | [Backup Fails](#backup-fails)                 |
| Network issues      | [Cannot Connect](#cannot-connect)             |
| Slow commands       | [Slow Execution](#slow-commands)              |
| Email not sending   | [Email Not Sending](#email-not-sending)       |

---

## 🔧 INSTALLATION & SETUP ISSUES

### Installation Fails

**Symptom:**

```
pip install debian-vps-configurator
ERROR: Could not install packages due to an OSError
```

**Diagnostic Steps:**

```bash
# Check Python version
python3 --version
# Required: 3.9 or higher

# Check pip version
pip --version

# Check available disk space
df -h

# Check internet connectivity
ping -c 4 pypi.org
```

**Common Causes & Solutions:**

#### Cause 1: Python Version Too Old

```bash
# Check version
python3 --version

# If < 3.9, install newer Python
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip

# Use specific version
python3.11 -m venv venv
source venv/bin/activate
pip install debian-vps-configurator
```

#### Cause 2: Insufficient Permissions

```bash
# Install to user directory
pip install --user debian-vps-configurator

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install debian-vps-configurator
```

#### Cause 3: Missing System Dependencies

```bash
# Install build dependencies
sudo apt install -y \
  build-essential \
  python3-dev \
  libssl-dev \
  libffi-dev \
  libpam0g-dev

# Then retry installation
pip install debian-vps-configurator
```

#### Cause 4: Network/Firewall Issues

```bash
# Test PyPI connectivity
curl -I https://pypi.org

# If blocked, use proxy
pip install --proxy http://proxy:port debian-vps-configurator

# Or download offline and install
pip download debian-vps-configurator
pip install debian-vps-configurator*.whl
```

**Verification:**

```bash
# Should work without errors
vps-configurator --version
```

---

### Configuration Errors

**Symptom:**

```
vps-configurator init
ERROR: Invalid configuration file
```

**Diagnostic Steps:**

```bash
# Check config file exists
ls -la /etc/debian-vps-configurator/config.yaml

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('/etc/debian-vps-configurator/config.yaml'))"

# Check for syntax errors
vps-configurator config validate
```

**Common Causes & Solutions:**

#### Cause 1: YAML Syntax Error

```bash
# Common YAML errors:
# - Incorrect indentation (use spaces, not tabs)
# - Missing colons
# - Unquoted special characters

# Fix example:
# WRONG:
email: admin@company.com:587

# RIGHT:
email: "admin@company.com:587"

# Validate after fixing
vps-configurator config validate
```

#### Cause 2: Missing Required Fields

```bash
# Check which fields are missing
vps-configurator config validate --verbose

# Required fields:
general:
  environment: production
  hostname: vps.company.com
  admin_email: admin@company.com
```

#### Cause 3: Invalid Values

```bash
# Check logs for specific error
tail -50 /var/log/vps-configurator/main.log

# Common invalid values:
# - Port numbers: must be 1-65535
# - Email: must be valid format
# - Paths: must be absolute paths
# - Boolean: must be true/false (not yes/no)
```

**Solution: Reset to Default Config**

```bash
# Backup current config
sudo cp /etc/debian-vps-configurator/config.yaml /tmp/config.yaml.bak

# Generate fresh default config
vps-configurator config reset --default

# Manually merge your settings
sudo vim /etc/debian-vps-configurator/config.yaml
```

**Verification:**

```bash
vps-configurator config validate
# Should output: ✅ Configuration valid
```

---

### Permission Denied Errors

**Symptom:**

```
vps-configurator init
ERROR: Permission denied: '/etc/debian-vps-configurator'
```

**Diagnostic Steps:**

```bash
# Check current user
whoami

# Check directory ownership
ls -la /etc/debian-vps-configurator/
ls -la /var/lib/debian-vps-configurator/
ls -la /var/log/vps-configurator/

# Check user groups
groups
```

**Solutions:**

#### Solution 1: Not Running as Root/Sudo

```bash
# System operations require sudo
sudo vps-configurator init

# Or switch to root
sudo su -
vps-configurator init
```

#### Solution 2: Incorrect File Permissions

```bash
# Fix directory permissions
sudo chown -R vpsconfig:vpsconfig /opt/vps-configurator
sudo chown -R vpsconfig:vpsconfig /var/lib/debian-vps-configurator
sudo chown -R vpsconfig:vpsconfig /var/log/vps-configurator

# Fix config file permissions
sudo chmod 600 /etc/debian-vps-configurator/config.yaml
sudo chmod 600 /opt/vps-configurator/.env
```

**Verification:**

```bash
# Should work without sudo (for non-system operations)
vps-configurator user list
```

---

### Database Initialization Fails

**Symptom:**

```
ERROR: Could not initialize database
sqlite3.OperationalError: unable to open database file
```

**Diagnostic Steps:**

```bash
# Check database directory exists
ls -la /var/lib/debian-vps-configurator/activity/

# Check disk space
df -h /var/lib/debian-vps-configurator

# Check permissions
ls -la /var/lib/debian-vps-configurator/activity/activity.db

# Test SQLite
sqlite3 /var/lib/debian-vps-configurator/activity/activity.db ".tables"
```

**Solutions:**

#### Solution 1: Create Database Directory

```bash
# Create directory structure
sudo mkdir -p /var/lib/debian-vps-configurator/activity
sudo chown -R vpsconfig:vpsconfig /var/lib/debian-vps-configurator

# Re-initialize
vps-configurator init --force
```

#### Solution 2: Fix Database Permissions

```bash
# Fix ownership
sudo chown vpsconfig:vpsconfig /var/lib/debian-vps-configurator/activity/activity.db

# Fix permissions
sudo chmod 644 /var/lib/debian-vps-configurator/activity/activity.db
```

#### Solution 3: Rebuild Database

```bash
# Backup existing database
cp /var/lib/debian-vps-configurator/activity/activity.db /tmp/activity.db.bak

# Remove corrupted database
rm /var/lib/debian-vps-configurator/activity/activity.db

# Reinitialize
vps-configurator database init
```

**Verification:**

```bash
sqlite3 /var/lib/debian-vps-configurator/activity/activity.db ".tables"
# Should show: activity_events, ssh_sessions, anomalies
```

---

## ⚙️ SERVICE & SYSTEM ISSUES

### Service Won't Start

**Symptom:**

```
systemctl start vps-configurator
Job for vps-configurator.service failed
```

**Diagnostic Steps:**

```bash
# Check service status
systemctl status vps-configurator

# Check service logs
journalctl -u vps-configurator -n 50 --no-pager

# Check application logs
tail -50 /var/log/vps-configurator/main.log

# Check for port conflicts
sudo netstat -tulpn | grep vps-configurator
```

**Common Causes & Solutions:**

#### Cause 1: Configuration Error

```bash
# Validate configuration
vps-configurator config validate

# If errors found, fix them
sudo vim /etc/debian-vps-configurator/config.yaml

# Try starting again
systemctl start vps-configurator
```

#### Cause 2: Missing Dependencies

```bash
# Check Python environment
/opt/vps-configurator/app/venv/bin/python3 --version

# Reinstall dependencies
cd /opt/vps-configurator/app
source venv/bin/activate
pip install -r requirements.txt
```

#### Cause 3: File Permission Issues

```bash
# Check critical file permissions
ls -la /opt/vps-configurator/.env
ls -la /etc/debian-vps-configurator/config.yaml

# Fix if needed
sudo chown vpsconfig:vpsconfig /opt/vps-configurator/.env
sudo chmod 600 /opt/vps-configurator/.env
```

#### Cause 4: Previous Process Still Running

```bash
# Check for existing processes
ps aux | grep vps-configurator

# Kill if found
sudo pkill -f vps-configurator

# Wait a few seconds, then start
sleep 5
systemctl start vps-configurator
```

**Verification:**

```bash
systemctl status vps-configurator
# Should show: active (running)
```

---

### High CPU Usage

**Symptom:**

```
top
vps-configurator using 95%+ CPU
```

**Diagnostic Steps:**

```bash
# Identify high CPU processes
top -bn1 | head -20

# Check vps-configurator processes
ps aux | grep vps-configurator

# Check for runaway jobs
vps-configurator jobs list --running

# Profile CPU usage
sudo perf top -p $(pgrep -f vps-configurator)
```

**Common Causes & Solutions:**

#### Cause 1: Scanning in Progress

```bash
# Check if scan running
vps-configurator security status

# If scan taking too long:
# - Wait for completion
# - Or cancel: vps-configurator jobs cancel [job-id]

# Reschedule for off-hours
crontab -e
# Change scan time to 2 AM
```

#### Cause 2: Parallel Workers Too High

```bash
# Reduce max workers
sudo vim /etc/debian-vps-configurator/config.yaml

performance:
  parallel_execution:
    max_workers: 2  # Reduce from 4

# Restart service
systemctl restart vps-configurator
```

#### Cause 3: Log Parsing/Analysis

```bash
# Check log file sizes
du -sh /var/log/vps-configurator/*

# If logs too large, rotate now
logrotate -f /etc/logrotate.d/vps-configurator

# Consider reducing retention
sudo vim /etc/logrotate.d/vps-configurator
# Change: rotate 30 → rotate 7
```

#### Cause 4: Database Query Issue

```bash
# Check for slow queries
grep "took.*[5-9][0-9][0-9][0-9]ms" /var/log/vps-configurator/main.log

# Optimize database
sqlite3 /var/lib/debian-vps-configurator/activity/activity.db "VACUUM; ANALYZE;"

# Add indexes if missing
vps-configurator database optimize
```

**Verification:**

```bash
# CPU should drop to < 20%
top -bn1 | grep vps-configurator
```

---

### High Memory Usage

**Symptom:**

```
free -h
Memory usage > 85%
```

**Diagnostic Steps:**

```bash
# Check memory usage
free -h

# Check swap usage
swapon --show

# Identify memory hogs
ps aux --sort=-%mem | head -10
```

**Solutions:**

#### Solution 1: Clear Caches

```bash
# Clear package cache
sudo vps-configurator cache clear

# Clear system cache
sudo sync; echo 3 > /proc/sys/vm/drop_caches

# Clear Python cache
find /opt/vps-configurator -type d -name __pycache__ -exec rm -r {} +
```

#### Solution 2: Optimize Configuration

```bash
# Reduce in-memory caching
sudo vim /etc/debian-vps-configurator/config.yaml

performance:
  cache:
    max_size_gb: 5  # Reduce from 10

# Restart
systemctl restart vps-configurator
```

#### Solution 3: Archive Old Data

```bash
# Archive old activity logs
vps-configurator activity archive --older-than 90d

# Vacuum database
sqlite3 /var/lib/debian-vps-configurator/activity/activity.db "VACUUM;"
```

**Verification:**

```bash
free -h
# Available memory should be > 1GB
```

---

### Disk Space Full

**Symptom:**

```
df -h
/dev/sda1  99%  Used
```

**Diagnostic Steps:**

```bash
# Check disk usage
df -h

# Find large directories
sudo du -sh /* | sort -rh | head -10

# Find large files
sudo find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | head -20

# Check vps-configurator directories
du -sh /var/log/vps-configurator/*
du -sh /opt/vps-configurator/backups/*
du -sh /var/lib/debian-vps-configurator/*
```

**Solutions:**

#### Solution 1: Clean Up Logs

```bash
# Rotate logs now
logrotate -f /etc/logrotate.d/vps-configurator

# Remove old logs
find /var/log/vps-configurator -name "*.log.*" -mtime +30 -delete

# Compress large logs
gzip /var/log/vps-configurator/*.log
```

#### Solution 2: Clean Up Old Backups

```bash
# List backups by size
ls -lh /opt/vps-configurator/backups/ | sort -k5 -rh

# Keep only last 7 days
find /opt/vps-configurator/backups -name "*.tar.gz" -mtime +7 -delete

# Move old backups to remote storage
rclone move /opt/vps-configurator/backups/ remote:backups/archive/
```

#### Solution 3: Clean Package Cache

```bash
# Clear apt cache
sudo apt clean
sudo apt autoclean

# Remove old kernels
sudo apt autoremove

# Clear pip cache
pip cache purge
```

#### Solution 4: Archive Activity Database

```bash
# Check database size
du -h /var/lib/debian-vps-configurator/activity/activity.db

# Archive old records
vps-configurator activity archive --older-than 180d

# Vacuum database
sqlite3 /var/lib/debian-vps-configurator/activity/activity.db "VACUUM;"
```

**Verification:**

```bash
df -h
# Should be < 80% used
```

---

## 👤 USER ACCESS ISSUES

### User Cannot Login

**Symptom:**

```
ssh user@vps.company.com
Permission denied (publickey)
```

**Diagnostic Steps:**

```bash
# On server, check user status
vps-configurator user info [username]

# Check SSH logs
sudo grep [username] /var/log/auth.log | tail -20

# Check user's home directory
ls -la /home/[username]

# Check SSH key
cat /home/[username]/.ssh/authorized_keys
```

**Common Causes & Solutions:**

#### Cause 1: User Account Suspended/Offboarded

```bash
# Check status
vps-configurator user info [username]

# If suspended, reactivate
vps-configurator user activate [username]

# If offboarded, cannot reactivate
# Must create new account
```

#### Cause 2: SSH Key Not Deployed/Expired

```bash
# Check SSH keys
vps-configurator ssh list-keys --user [username]

# If no keys or expired:
vps-configurator ssh generate-key --user [username]

# Deploy new key
vps-configurator ssh deploy-key --user [username] --key [key-file]
```

#### Cause 3: File Permission Issues

```bash
# Check home directory permissions
ls -la /home/[username]

# Fix if needed
sudo chown -R [username]:[username] /home/[username]
sudo chmod 700 /home/[username]
sudo chmod 700 /home/[username]/.ssh
sudo chmod 600 /home/[username]/.ssh/authorized_keys
```

**Verification:**

```bash
# User should be able to login
ssh [username]@vps.company.com
```

---

### SSH Key Not Working

**Symptom:**

```
ssh -i ~/.ssh/id_ed25519 user@vps.company.com
Permission denied (publickey)
```

**Diagnostic Steps:**

```bash
# Verbose SSH output
ssh -vvv -i ~/.ssh/id_ed25519 user@vps.company.com
# Look for "Offered public key:..." messages

# Check key fingerprint
ssh-keygen -lf ~/.ssh/id_ed25519.pub

# On server, check authorized_keys
cat /home/user/.ssh/authorized_keys
```

**Solutions:**

#### Solution 1: Wrong Key File

```bash
# List all keys
ls -la ~/.ssh/

# Try different keys
ssh -i ~/.ssh/id_rsa user@vps.company.com
ssh -i ~/.ssh/id_ed25519 user@vps.company.com

# Check which key is deployed
vps-configurator ssh list-keys --user user
```

#### Solution 2: Key Not in authorized_keys

```bash
# On server, add key manually
echo "[public-key-content]" >> /home/user/.ssh/authorized_keys

# Or use vps-configurator
vps-configurator ssh deploy-key --user user --key /path/to/public-key
```

#### Solution 3: Key Permissions Wrong

```bash
# Fix local key permissions
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# Fix server permissions
sudo chmod 700 /home/user/.ssh
sudo chmod 600 /home/user/.ssh/authorized_keys
sudo chown -R user:user /home/user/.ssh
```

**Verification:**

```bash
ssh -i ~/.ssh/id_ed25519 user@vps.company.com
# Should login successfully
```

---

### 2FA Code Rejected

**Symptom:**

```
Enter verification code: 123456
ERROR: Invalid verification code
```

**Diagnostic Steps:**

```bash
# Check 2FA status
vps-configurator mfa status --user [username]

# Check time synchronization (critical for TOTP!)
timedatectl status

# Check failed 2FA attempts
grep "2FA" /var/log/vps-configurator/security.log | tail -20
```

**Common Causes & Solutions:**

#### Cause 1: Time Skew

```bash
# TOTP codes are time-based - clocks must be synced!

# Check server time
date

# Sync time
sudo systemctl stop systemd-timesyncd
sudo systemctl start systemd-timesyncd
timedatectl set-ntp true

# Verify sync
timedatectl status
# Look for: "System clock synchronized: yes"

# Ask user to check their device time
# Phone/computer must be accurate
```

#### Cause 2: Using Old Code

```bash
# TOTP codes expire every 30 seconds
# Wait for new code to appear in authenticator app
# Use the NEW code, not the old one
```

#### Cause 3: Wrong Secret/QR Code

```bash
# User might have scanned wrong QR code
# Reset 2FA
vps-configurator mfa reset --user [username]

# Re-enroll
vps-configurator mfa setup --user [username]

# Send new QR code to user
cat /home/[username]/.mfa-qr-code.txt
```

#### Cause 4: Account Locked After Failed Attempts

```bash
# Check lockout status
vps-configurator mfa status --user [username]

# If locked after 5 failed attempts
vps-configurator mfa unlock --user [username]

# Investigate why codes were wrong
# - Time sync issue?
# - User has wrong QR code?
# - Malicious attempts?
```

**Emergency: Use Backup Code**

```bash
# User lost authenticator app?
# Use backup codes

# Check backup codes
cat /home/[username]/.mfa-backup-codes.txt

# User enters backup code instead of TOTP
# Backup code works ONCE
```

**Verification:**

```bash
# User logs in and enters current 2FA code
# Should be accepted
```

---

### Temporary Access Expired

**Symptom:**

```
ssh contractor@vps.company.com
Permission denied
```

**Diagnostic Steps:**

```bash
# Check temporary access status
vps-configurator temp-access info contractor

# Check expiration date
vps-configurator temp-access list --user contractor
```

**Solutions:**

#### Solution 1: Extend Access

```bash
# If contractor still needed
vps-configurator temp-access extend contractor \
  --days 14 \
  --reason "Project extended" \
  --requested-by [manager]
```

#### Solution 2: Re-Grant Access

```bash
# If access fully expired and archived
vps-configurator temp-access grant contractor \
  --full-name "Contractor Name" \
  --email contractor@company.com \
  --role developer \
  --duration 30d \
  --reason "New project phase"
```

**Verification:**

```bash
# Contractor should be able to login
ssh contractor@vps.company.com
```

---

## 🔒 SECURITY ISSUES

### CIS Scan Fails

**Symptom:**

```
vps-configurator security cis-scan
ERROR: CIS scan failed to complete
```

**Diagnostic Steps:**

```bash
# Check scan logs
grep "CIS" /var/log/vps-configurator/security.log | tail -50

# Check if scan is stuck
ps aux | grep cis

# Check system resources
free -h
df -h
```

**Solutions:**

#### Solution 1: Timeout During Scan

```bash
# Increase timeout
sudo vim /etc/debian-vps-configurator/config.yaml

security:
  cis_benchmark:
    scan_timeout_seconds: 1800  # Increase from 900

# Retry scan
vps-configurator security cis-scan
```

#### Solution 2: Missing Audit Tools

```bash
# Install required tools
sudo apt install -y auditd aide

# Retry scan
vps-configurator security cis-scan
```

#### Solution 3: Permission Issues

```bash
# CIS scan needs root privileges
sudo vps-configurator security cis-scan
```

**Verification:**

```bash
vps-configurator security cis-scan
# Should complete with results
```

---

### SSL Certificate Issues

**Symptom:**

```
vps-configurator ssl issue vps.company.com
ERROR: Failed to issue certificate
```

**Common Causes & Solutions:**

#### Cause 1: DNS Not Propagated

```bash
# Check DNS resolution
nslookup vps.company.com
dig vps.company.com

# Wait for DNS propagation (up to 48 hours)
# Or use DNS-01 challenge instead of HTTP-01
```

#### Cause 2: Port 80 Not Accessible

```bash
# Let's Encrypt needs port 80 for validation
# Check firewall
sudo ufw status | grep 80

# Allow port 80
sudo ufw allow 80/tcp

# Check if service using port 80
sudo netstat -tulpn | grep :80
```

#### Cause 3: Rate Limit Exceeded

```bash
# Let's Encrypt has rate limits
# 5 failures per hour per domain

# Wait 1 hour, then retry
# Or use staging server for testing
vps-configurator ssl issue vps.company.com --staging
```

**Verification:**

```bash
vps-configurator ssl check vps.company.com
# Should show valid certificate
```

---

### Failed Login Attempts Spike

**Symptom:**

```
grep "Failed password" /var/log/auth.log | wc -l
500+ failed attempts
```

**Immediate Actions:**

```bash
# 1. Identify attacking IPs
sudo grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -10

# 2. Block top attackers
for ip in $(sudo grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -5 | awk '{print $2}'); do
    sudo ufw deny from $ip
done

# 3. Check fail2ban
sudo fail2ban-client status sshd

# 4. Verify legitimate users not locked
vps-configurator user list --locked
```

**Long-term Solutions:**

```bash
# Configure fail2ban more aggressively
sudo vim /etc/fail2ban/jail.local

[sshd]
enabled = true
maxretry = 3
bantime = 3600
findtime = 600

# Restart fail2ban
sudo systemctl restart fail2ban
```

**Verification:**

```bash
# Failed attempts should drop significantly
sudo fail2ban-client status sshd
```

---

## 💾 BACKUP & DATA ISSUES

### Backup Fails

**Symptom:**

```
/opt/vps-configurator/scripts/backup.sh
ERROR: Backup failed
```

**Diagnostic Steps:**

```bash
# Check backup logs
cat /opt/vps-configurator/backups/backup.log

# Check disk space
df -h /opt/vps-configurator/backups

# Check permissions
ls -la /opt/vps-configurator/backups

# Test tar command
tar --version
```

**Solutions:**

#### Solution 1: Insufficient Disk Space

```bash
# Check space needed
du -sh /etc/debian-vps-configurator /var/lib/debian-vps-configurator /var/log/vps-configurator

# Free up space
find /opt/vps-configurator/backups -name "*.tar.gz" -mtime +7 -delete

# Or backup to remote
rclone move /opt/vps-configurator/backups/ remote:backups/
```

#### Solution 2: Permission Denied

```bash
# Fix backup directory permissions
sudo chown -R vpsconfig:vpsconfig /opt/vps-configurator/backups
sudo chmod 755 /opt/vps-configurator/backups
```

**Verification:**

```bash
# Run backup manually
/opt/vps-configurator/scripts/backup.sh

# Check backup created
ls -lth /opt/vps-configurator/backups/ | head -2
```

---

### Cannot Restore from Backup

**Symptom:**

```
tar -xzf backup.tar.gz
tar: Error is not recoverable: exiting now
```

**Solutions:**

#### Solution 1: Corrupted Backup

```bash
# Check backup integrity
gzip -t backup.tar.gz

# If corrupted, try previous backup
ls -lt /opt/vps-configurator/backups/
# Use second-to-last backup
```

#### Solution 2: Permission Issues

```bash
# Restore with sudo
sudo tar -xzf backup.tar.gz -C /

# Then fix permissions
sudo chown -R vpsconfig:vpsconfig /var/lib/debian-vps-configurator
```

**Verification:**

```bash
# Check restored files
ls -la /etc/debian-vps-configurator/
systemctl restart vps-configurator
vps-configurator health-check
```

---

### Data Corruption

**Symptom:**

```
sqlite3.DatabaseError: database disk image is malformed
```

**Solutions:**

#### Solution 1: Database Recovery

```bash
# Try SQLite recovery
sqlite3 /var/lib/debian-vps-configurator/activity/activity.db ".recover" | sqlite3 recovered.db

# If successful, replace
mv /var/lib/debian-vps-configurator/activity/activity.db /var/lib/debian-vps-configurator/activity/activity.db.corrupt
mv recovered.db /var/lib/debian-vps-configurator/activity/activity.db
```

#### Solution 2: Restore from Backup

```bash
# Find most recent backup
ls -lt /opt/vps-configurator/backups/

# Extract database
tar -xzf /opt/vps-configurator/backups/[latest].tar.gz \
  var/lib/debian-vps-configurator/activity/activity.db

# Copy to location
sudo cp var/lib/debian-vps-configurator/activity/activity.db \
  /var/lib/debian-vps-configurator/activity/activity.db
```

**Verification:**

```bash
sqlite3 /var/lib/debian-vps-configurator/activity/activity.db "PRAGMA integrity_check"
# Should return: ok
```

---

### Database Locked

**Symptom:**

```
sqlite3.OperationalError: database is locked
```

**Solutions:**

#### Solution 1: Close Other Connections

```bash
# Find processes using database
sudo lsof /var/lib/debian-vps-configurator/activity/activity.db

# Kill if needed
sudo kill [PID]
```

#### Solution 2: Remove Lock File

```bash
# Remove stale lock
rm /var/lib/debian-vps-configurator/activity/activity.db-journal

# Restart service
systemctl restart vps-configurator
```

#### Solution 3: Wait and Retry

```bash
# SQLite locks are usually brief
# Retry after a few seconds
sleep 5
vps-configurator activity report --last 24h
```

**Verification:**

```bash
# Should work now
vps-configurator activity report --last 24h
```

---

## 🌐 NETWORK & CONNECTIVITY ISSUES

### Cannot Connect to Server

**Symptom:**

```
ssh admin@vps.company.com
ssh: connect to host vps.company.com port 22: Connection timed out
```

**Diagnostic Steps:**

```bash
# From local machine:

# 1. Check DNS
nslookup vps.company.com
ping vps.company.com

# 2. Check port 22 reachable
telnet vps.company.com 22
nc -zv vps.company.com 22

# 3. Traceroute
traceroute vps.company.com
```

**Common Causes & Solutions:**

#### Cause 1: Firewall Blocking

```bash
# Use console access to check firewall
sudo ufw status

# If port 22 not allowed
sudo ufw allow 22/tcp
sudo ufw reload
```

#### Cause 2: SSH Service Not Running

```bash
# Via console:
sudo systemctl status sshd

# If not running
sudo systemctl start sshd
sudo systemctl enable sshd
```

#### Cause 3: Wrong IP/Domain

```bash
# Verify server IP
# Use console or provider dashboard

# Try IP directly
ssh admin@203.0.113.50

# If works, DNS issue
# Update DNS records
```

**Verification:**

```bash
ssh admin@vps.company.com
# Should connect
```

---

### Firewall Blocking Access

**Symptom:**

```
curl https://vps.company.com
curl: (7) Failed to connect to vps.company.com port 443: Connection refused
```

**Solutions:**

```bash
# Check firewall rules
sudo ufw status numbered

# Allow HTTPS
sudo ufw allow 443/tcp

# Reload firewall
sudo ufw reload
```

**Verification:**

```bash
curl -I https://vps.company.com
# Should return HTTP headers
```

---

### DNS Resolution Fails

**Symptom:**

```
ping vps.company.com
ping: vps.company.com: Name or service not known
```

**Solutions:**

```bash
# Check DNS configuration
cat /etc/resolv.conf

# Try different DNS server
sudo vim /etc/resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4

# Test resolution
nslookup vps.company.com 8.8.8.8

# Clear DNS cache
sudo systemd-resolve --flush-caches
```

**Verification:**

```bash
nslookup vps.company.com
# Should return IP address
```

---

## ⚡ PERFORMANCE ISSUES

### Slow Command Execution

**Symptom:**

```
vps-configurator user list
(takes 30+ seconds)
```

**Solutions:**

#### Solution 1: Database Optimization

```bash
# Vacuum and analyze database
sqlite3 /var/lib/debian-vps-configurator/activity/activity.db "VACUUM; ANALYZE;"

# Add missing indexes
vps-configurator database optimize
```

#### Solution 2: Clear Caches

```bash
# Clear stale caches
vps-configurator cache clear

# Disable cache temporarily to test
vps-configurator --no-cache user list
```

**Verification:**

```bash
time vps-configurator user list
# Should complete in < 5 seconds
```

---

### Timeout Errors

**Symptom:**

```
vps-configurator security cis-scan
ERROR: Operation timed out
```

**Solutions:**

```bash
# Increase timeout
sudo vim /etc/debian-vps-configurator/config.yaml

timeouts:
  command_timeout: 300
  scan_timeout: 1800

# Or override per command
vps-configurator security cis-scan --timeout 1800
```

---

### Database Performance Issues

**Symptom:**

```
vps-configurator activity report
(very slow, 60+ seconds)
```

**Solutions:**

```bash
# Check database size
du -h /var/lib/debian-vps-configurator/activity/activity.db

# If > 5GB, archive old data
vps-configurator activity archive --older-than 180d

# Optimize
sqlite3 /var/lib/debian-vps-configurator/activity/activity.db "VACUUM; REINDEX;"

# Add indexes
vps-configurator database add-indexes
```

**Verification:**

```bash
time vps-configurator activity report --last 7d
# Should complete in < 10 seconds
```

---

## 🔗 INTEGRATION ISSUES

### Email Notifications Not Sending

**Symptom:**

```
No email alerts received
```

**Diagnostic Steps:**

```bash
# Check email configuration
grep -A 10 "email:" /etc/debian-vps-configurator/config.yaml

# Test SMTP connection
telnet smtp.gmail.com 587

# Check logs
grep "email\|smtp" /var/log/vps-configurator/main.log
```

**Solutions:**

#### Solution 1: SMTP Credentials Wrong

```bash
# Update SMTP password
vim /opt/vps-configurator/.env
SMTP_PASSWORD=correct-password-here

# Restart service
systemctl restart vps-configurator

# Test
vps-configurator alert test --email admin@company.com
```

#### Solution 2: SMTP Port Blocked

```bash
# Try alternative port
sudo vim /etc/debian-vps-configurator/config.yaml

notifications:
  email:
    smtp_port: 465  # Try 465 instead of 587
    smtp_use_ssl: true

systemctl restart vps-configurator
```

#### Solution 3: Gmail App Password Needed

```bash
# Gmail requires App Password (not regular password)
# Generate at: https://myaccount.google.com/apppasswords

# Update .env
SMTP_PASSWORD=generated-app-password

systemctl restart vps-configurator
```

**Verification:**

```bash
vps-configurator alert test --email your@email.com
# Check inbox for test email
```

---

### Cron Jobs Not Running

**Symptom:**

```
Scheduled backups/scans not happening
```

**Diagnostic Steps:**

```bash
# Check crontab
crontab -l

# Check cron service
systemctl status cron

# Check cron logs
grep CRON /var/log/syslog | tail -20

# Test cron entry manually
/opt/vps-configurator/scripts/backup.sh
```

**Solutions:**

#### Solution 1: Cron Service Not Running

```bash
sudo systemctl start cron
sudo systemctl enable cron
```

#### Solution 2: Wrong User Crontab

```bash
# Check which user's crontab
sudo crontab -l -u vpsconfig

# If empty, add jobs
sudo crontab -e -u vpsconfig
```

#### Solution 3: Path Issues in Cron

```bash
# Cron has limited PATH
# Use absolute paths

# Edit crontab
crontab -e

# Good:
0 1 * * * /opt/vps-configurator/scripts/backup.sh

# Bad:
0 1 * * * backup.sh
```

#### Solution 4: Script Not Executable

```bash
chmod +x /opt/vps-configurator/scripts/backup.sh
```

**Verification:**

```bash
# Wait for next scheduled run
# Or adjust cron to run in 2 minutes for testing
*/2 * * * * /opt/vps-configurator/scripts/backup.sh

# Check logs
tail -f /opt/vps-configurator/backups/backup.log
```

---

## 🆘 GENERAL TROUBLESHOOTING METHODOLOGY

### Step-by-Step Approach

**1. Identify the Problem (5 minutes)**

```
- What exactly is failing?
- When did it start?
- What changed recently?
- Is it affecting all users or just one?
```

**2. Gather Information (10 minutes)**

```bash
# Health check
vps-configurator health-check

# Recent logs
tail -100 /var/log/vps-configurator/main.log

# System resources
free -h; df -h; top -bn1 | head -10

# Service status
systemctl status vps-configurator
```

**3. Check Documentation (5 minutes)**

```
- Search this troubleshooting guide
- Check error message in logs
- Review recent changes log
```

**4. Form Hypothesis (5 minutes)**

```
- Based on symptoms, what's most likely?
- Have you seen this before?
- What are 2-3 possible causes?
```

**5. Test Hypothesis (10-30 minutes)**

```
- Try simplest solution first
- Change ONE thing at a time
- Document what you try
- Verify if it worked
```

**6. Escalate if Needed (as needed)**

```
- If stuck after 1 hour, escalate
- Document what you tried
- Provide logs and error messages
```

**7. Document Solution (5 minutes)**

```
- What was the problem?
- What fixed it?
- Update this guide
- Update runbook
```

---

## 📝 LOGGING BEST PRACTICES

### When Troubleshooting

**Enable Debug Logging:**

```bash
sudo vim /etc/debian-vps-configurator/config.yaml
logging:
  level: DEBUG

systemctl restart vps-configurator
```

**Follow Logs in Real-Time:**

```bash
tail -f /var/log/vps-configurator/main.log
```

**Search Logs:**

```bash
# Find errors
grep -i error /var/log/vps-configurator/main.log | tail -50

# Find specific user activity
grep "user: johndoe" /var/log/vps-configurator/activity-audit.log

# Find timeframe
grep "2026-01-07 14:" /var/log/vps-configurator/main.log
```

**After Troubleshooting:**

```bash
# Disable debug logging (to save disk space)
sudo vim /etc/debian-vps-configurator/config.yaml
logging:
  level: INFO

systemctl restart vps-configurator
```

---

## 📞 WHEN TO ESCALATE

### Escalation Criteria

**Escalate Immediately if:**

- ❌ Production system completely down
- ❌ Security breach suspected
- ❌ Data loss occurring
- ❌ Multiple users unable to work
- ❌ Backup/restore failing critically

**Escalate After 1 Hour if:**

- ⚠️ Problem not resolved with troubleshooting guide
- ⚠️ Root cause unclear
- ⚠️ Solution requires architectural change
- ⚠️ Outside your expertise

**What to Include When Escalating:**

```
1. Exact problem description
2. When it started
3. What you tried (steps from this guide)
4. Relevant log snippets
5. System state (health-check output)
6. Impact (how many users affected)
```

---

## ✅ TROUBLESHOOTING CHECKLIST

**Before You Start:**

```
[ ] Identified exact problem/error
[ ] Checked this guide's table of contents
[ ] Noted when problem started
[ ] Noted what changed recently
```

**During Troubleshooting:**

```
[ ] Backed up data before making changes
[ ] Documented each step taken
[ ] Changed only ONE thing at a time
[ ] Verified each change
[ ] Saved error messages/logs
```

**After Resolution:**

```
[ ] Verified system fully working
[ ] Returned debug settings to normal
[ ] Documented solution
[ ] Updated guide if new issue
[ ] Notified affected users
[ ] Performed post-incident review (if major issue)
```

---

**END OF TROUBLESHOOTING GUIDE**

🔧 **Keep this guide handy! Most problems have solutions here.**

💡 **If you find a new issue, add it to this guide!**
