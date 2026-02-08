# TeleCommand Pro Web Portal

🌐 Web-based management interface for TeleCommand Pro bot

## Features

- 📊 **Dashboard** - Real-time statistics and activity overview
- 👥 **User Management** - Add/remove authorized Telegram users via UI
- 📜 **Command Logs** - View all executed commands with full output
- ⚙️ **Configuration** - Edit bot settings through web interface
- 🔐 **Secure Login** - Password-protected access
- 📱 **Responsive Design** - Works on desktop and mobile

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Portal

```bash
python3 web_portal.py
```

The portal will be available at: **http://localhost:5000**

### 3. Login

**Default credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change the default password immediately after first login!**

## Running Bot & Portal Together

### Option 1: Separate Terminals

**Terminal 1 - Bot:**
```bash
python3 bot.py
```

**Terminal 2 - Portal:**
```bash
python3 web_portal.py
```

### Option 2: Background Processes (Linux/macOS)

```bash
# Start portal in background
python3 web_portal.py &

# Start bot
python3 bot.py
```

### Option 3: Using screen (Linux)

```bash
# Create screen for portal
screen -dmS telecommand-portal python3 web_portal.py

# Create screen for bot
screen -dmS telecommand-bot python3 bot.py

# View portal
screen -r telecommand-portal

# View bot
screen -r telecommand-bot

# Detach: Ctrl+A, then D
```

## Features Guide

### 📊 Dashboard

The dashboard provides:
- Total active users count
- Total commands executed
- Success/failure statistics
- Recent command history
- Active user list with last seen times

### 👥 User Management

**Add Users:**
1. Get user's Telegram ID from @userinfobot
2. Enter ID, username (optional), and name (optional)
3. Click "Add User"
4. User is immediately authorized

**Remove Users:**
1. Find user in the list
2. Click "Remove"
3. Confirm action
4. User is deauthorized

**Auto-sync:** Changes are automatically synced to `config.json`

### 📜 Command Logs

View detailed logs of all executed commands:
- Timestamp
- User who executed
- Full command
- Complete output
- Success/failure status
- Searchable and paginated

**View Details:**
- Click "View Details" on any command
- See full output and execution details
- Useful for debugging and auditing

### ⚙️ Configuration

Edit bot settings through the UI:

**Bot Token:**
- Update your Telegram bot token
- Get from @BotFather

**Command Whitelist:**
- Enable/disable command restrictions
- Add/remove allowed commands
- One command per line

**Timeout:**
- Set maximum execution time
- Range: 5-300 seconds
- Prevents hanging commands

**Note:** Restart bot after changing configuration!

## Security

### Change Default Password

**Method 1: Via Database**
```bash
sqlite3 telecommand.db
```

```sql
UPDATE portal_users 
SET password_hash = '<new_hash>' 
WHERE username = 'admin';
```

**Method 2: Via Python**
```python
from werkzeug.security import generate_password_hash
import sqlite3

new_password = 'your_new_password'
password_hash = generate_password_hash(new_password)

db = sqlite3.connect('telecommand.db')
db.execute('UPDATE portal_users SET password_hash = ? WHERE username = ?', 
           (password_hash, 'admin'))
db.commit()
db.close()
```

### Add New Portal Users

```python
from werkzeug.security import generate_password_hash
import sqlite3

db = sqlite3.connect('telecommand.db')
db.execute('INSERT INTO portal_users (username, password_hash) VALUES (?, ?)',
           ('newuser', generate_password_hash('password123')))
db.commit()
db.close()
```

### Security Best Practices

1. **Change default password immediately**
2. **Use strong passwords**
3. **Enable HTTPS in production** (use nginx/Apache as reverse proxy)
4. **Restrict access by IP** (firewall rules)
5. **Keep database backups**
6. **Monitor access logs**

## Database

The portal uses SQLite database: `telecommand.db`

### Tables

**portal_users** - Web portal login accounts
**telegram_users** - Authorized Telegram users
**command_logs** - All executed commands with outputs
**bot_config** - Additional configuration (future use)

### Backup Database

```bash
# Create backup
cp telecommand.db telecommand.db.backup

# Restore backup
cp telecommand.db.backup telecommand.db
```

### View Database

```bash
sqlite3 telecommand.db

# List tables
.tables

# View users
SELECT * FROM telegram_users;

# View recent logs
SELECT * FROM command_logs ORDER BY executed_at DESC LIMIT 10;

# Exit
.quit
```

## API Endpoints

The portal provides APIs for the bot:

### POST /api/log

Log a command execution

**Request:**
```json
{
  "user_id": 123456789,
  "command": "ls -la",
  "output": "total 48\ndrwxr-xr-x ...",
  "success": 1
}
```

**Response:**
```json
{
  "status": "success"
}
```

### GET /api/stats

Get statistics (requires login)

**Response:**
```json
{
  "daily": [
    {"date": "2026-02-08", "count": 45}
  ],
  "top_commands": [
    {"command": "ls", "count": 120}
  ]
}
```

## Customization

### Change Port

Edit `web_portal.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change from 5000
```

Also update bot.py:
```python
requests.post('http://localhost:8080/api/log', ...)  # Change from 5000
```

### Custom Branding

Edit `templates/base.html`:
- Change colors in `<style>` section
- Modify navbar brand name
- Add custom logo

### Add Features

The portal is built with Flask. Add new routes in `web_portal.py`:

```python
@app.route('/custom')
@login_required
def custom_page():
    return render_template('custom.html')
```

## Troubleshooting

### Portal won't start

**Check if port is in use:**
```bash
# Linux/macOS
lsof -i :5000

# Windows
netstat -ano | findstr :5000
```

**Solution:**
- Stop other services using port 5000
- Or change portal port

### Database locked error

**Cause:** Multiple processes accessing database simultaneously

**Solution:**
```bash
# Stop all processes
pkill -f web_portal.py

# Restart
python3 web_portal.py
```

### Logs not appearing

**Check:**
1. Bot is running
2. Commands are being executed
3. Log API endpoint is reachable
4. No firewall blocking localhost

**Test API:**
```bash
curl -X POST http://localhost:5000/api/log \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123, "command": "test", "output": "test output", "success": 1}'
```

### Can't login

**Reset admin password:**
```bash
python3 << EOF
from werkzeug.security import generate_password_hash
import sqlite3
db = sqlite3.connect('telecommand.db')
db.execute('UPDATE portal_users SET password_hash = ? WHERE username = ?',
           (generate_password_hash('admin123'), 'admin'))
db.commit()
db.close()
print('Password reset to: admin123')
EOF
```

## Production Deployment

### Using Gunicorn (Linux)

```bash
# Install Gunicorn
pip install gunicorn

# Run portal
gunicorn -w 4 -b 0.0.0.0:5000 web_portal:app
```

### Using Nginx Reverse Proxy

**/etc/nginx/sites-available/telecommand:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Using Systemd Service

**/etc/systemd/system/telecommand-portal.service:**
```ini
[Unit]
Description=TeleCommand Pro Web Portal
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/telecommand
ExecStart=/path/to/telecommand/venv/bin/python3 web_portal.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable telecommand-portal
sudo systemctl start telecommand-portal
```

## Screenshots

### Dashboard
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+View)

### User Management
![Users](https://via.placeholder.com/800x400?text=User+Management)

### Command Logs
![Logs](https://via.placeholder.com/800x400?text=Command+Logs)

### Configuration
![Config](https://via.placeholder.com/800x400?text=Configuration)

## Support

For issues with the web portal:
1. Check logs in console
2. Verify database exists
3. Test API endpoints
4. Check file permissions

For bot integration issues:
- See main [README.md](README.md)
- Check bot.log
- Verify network connectivity

---

**Made with ❤️ for system administrators**
