# TeleCommand Pro

> 🤖 A secure, cross-platform Telegram bot for remotely managing your servers and workstations with OS-level command execution capabilities.

[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Web Portal](#web-portal)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Platform-Specific Notes](#platform-specific-notes)
- [Running as a Service](#running-as-a-service)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- 🔐 **User Authentication** - Only authorized users can execute commands
- 📝 **Command Logging** - All commands are logged with timestamp and user info
- ✅ **Command Whitelist** - Restrict which commands can be executed (configurable)
- ⏱ **Timeout Protection** - Commands automatically timeout after configured duration
- 🖥 **System Monitoring** - Quick access to system status, CPU, memory, disk, network info
- 📊 **Interactive Menus** - Easy-to-use inline keyboard menus
- 📜 **Command History** - Track previously executed commands
- 🌐 **Cross-Platform** - Works on Windows, Linux, and macOS with OS-specific commands
- 🌐 **Web Portal** - Manage users, view logs, and configure bot through web UI

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Sushilsin/TeleCommand-Pro.git
cd TeleCommand-Pro

# Run setup script (Linux/macOS)
./setup.sh

# Or on Windows
setup.bat

# Configure your bot token and user ID
cp config.example.json config.json
nano config.json  # Edit with your details

# Run the bot
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.bat  # Windows

python3 bot.py
```

## 🌐 Web Portal

TeleCommand includes a powerful web-based management portal!

### Features

- 📊 **Dashboard** - Real-time statistics and activity monitoring
- 👥 **User Management** - Add/remove authorized users through UI
- 📜 **Command Logs** - View all commands with full output
- ⚙️ **Configuration** - Edit bot settings without touching files
- 🔐 **Secure Access** - Password-protected web interface

### Quick Start

```bash
# Start both bot and portal
./start.sh  # Linux/macOS
start.bat   # Windows

# Access portal at: http://localhost:5000
# Default login: admin / admin123
```

### Manual Start

```bash
# Terminal 1 - Web Portal
python3 web_portal.py

# Terminal 2 - Bot
python3 bot.py
```

**Portal URL:** http://localhost:5000  
**Default Credentials:** `admin` / `admin123`

📖 **Full documentation:** [PORTAL_README.md](PORTAL_README.md)

## 📦 Installation

### Prerequisites

- **Python 3.8+** installed on your system
- **pip** package manager
- **Telegram account**
- Internet connection

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sushilsin/TeleCommand-Pro.git
cd TeleCommand-Pro
```

### Step 2: Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts:
   - **Bot Name:** Can be anything (e.g., "My Server Manager")
   - **Bot Username:** Must be unique and end with 'bot' (e.g., "myserver_control_bot")
4. **Save the bot token** - BotFather will send you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

> ⚠️ **Important:** Keep your bot token secret! Anyone with this token can control your bot.

### Step 3: Get Your Telegram User ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Start a chat with it
3. **Save your user ID** (a number like `123456789`)

> 💡 **Tip:** Your User ID is a numeric value, NOT your @username

### Step 4: Install Dependencies

Choose your platform:

<details>
<summary><b>🐧 Linux / 🍎 macOS</b></summary>

**Automated Setup:**
```bash
./setup.sh
```

**Manual Setup:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
</details>

<details>
<summary><b>🪟 Windows</b></summary>

**Automated Setup:**
```cmd
setup.bat
```

**Manual Setup:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```
</details>

## ⚙️ Configuration

### Step 5: Create Configuration File

```bash
cp config.example.json config.json
```

### Step 6: Edit config.json

Open the file with your favorite editor:

```bash
# Linux/macOS
nano config.json
# or
vim config.json

# Windows
notepad config.json
```

**Example Configuration:**

```json
{
  "telegram_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "authorized_users": [
    123456789
  ],
  "whitelist_enabled": false,
  "allowed_commands": [
    "ls", "pwd", "df", "ps", "top", "uptime", "whoami", "hostname"
  ],
  "command_timeout": 30
}
```

### Step 7: Start the Application

**Option 1: Using Launcher Script (Recommended)**

```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

This starts both the web portal and bot automatically.

**Option 2: Manual Start**

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat  # Windows

# Start web portal
python3 web_portal.py  # In one terminal

# Start bot
python3 bot.py  # In another terminal
```

### Step 8: Access Web Portal

1. Open your browser
2. Navigate to: **http://localhost:5000**
3. Login with default credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
4. **⚠️ Change the default password immediately!** (Go to Profile → Change Password)

### Step 9: Test the Bot

1. Open Telegram
2. Search for your bot by username
3. Start a chat with `/start`
4. Try a test command: `/exec uptime`

---

### Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `telegram_token` | string | Your bot token from @BotFather | **Required** |
| `authorized_users` | array | List of authorized Telegram user IDs | `[]` |
| `whitelist_enabled` | boolean | Enable command whitelist (`true`/`false`) | `true` |
| `allowed_commands` | array | Allowed commands (when whitelist enabled) | See example |
| `command_timeout` | integer | Max seconds for command execution | `30` |

### Security Modes

**Restricted Mode (Recommended for Production):**
```json
{
  "whitelist_enabled": true,
  "allowed_commands": ["ls", "pwd", "df", "ps", "uptime"]
}
```

**Unrestricted Mode (Use with Caution):**
```json
{
  "whitelist_enabled": false,
  "allowed_commands": ["*"]
}
```

## 🎯 Usage

### Start the Bot

**Linux/macOS:**
```bash
cd telecommand
source venv/bin/activate
python3 bot.py
```

**Windows:**
```cmd
cd telecommand
venv\Scripts\activate.bat
python bot.py
```

### Bot Commands

### Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message & authorization status | `/start` |
| `/help` | Show detailed help information | `/help` |
| `/status` | Comprehensive system status | `/status` |
| `/exec <cmd>` | Execute OS command | `/exec uptime` |
| `/sys` | Interactive system info menu | `/sys` |
| `/allowed` | List whitelisted commands | `/allowed` |
| `/history` | Show last 10 executed commands | `/history` |

### Command Examples

**Linux/macOS:**
```
/exec uptime
/exec df -h
/exec ps aux | head -10
/exec systemctl status nginx
/exec docker ps
/exec tail -n 50 /var/log/syslog
/exec top -bn1 | head -20
```

**Windows:**
```
/exec systeminfo
/exec dir C:\
/exec tasklist
/exec netstat -an
/exec wmic process list brief
/exec ipconfig /all
/exec sc query
```

### System Menu

The `/sys` command provides an interactive menu with quick access to:
- 💻 CPU Information
- 💾 Memory Usage
- 💿 Disk Space
- 🌐 Network Info
- 📊 Top Processes
- ⏰ System Uptime

**Note:** The bot automatically detects your operating system and uses the appropriate commands.

## Platform-Specific Notes

### Windows
- Uses `cmd` for command execution
- System commands: `systeminfo`, `wmic`, `tasklist`, `netstat`, `ipconfig`
- To run on startup, create a scheduled task or add to startup folder
- Paths use backslashes: `C:\path\to\file`

### Linux
- Uses shell for command execution
- System commands: `systemctl`, `ps`, `df`, `free`, `lscpu`, `ip`
- Can run as systemd service (see below)
- Paths use forward slashes: `/path/to/file`

### macOS
- Uses shell for command execution
- System commands: `sysctl`, `vm_stat`, `top`, `ifconfig`
- Can run as launchd service
- Paths use forward slashes: `/path/to/file`

## Running as a Service

### Linux (systemd)

To keep the bot running 24/7, create a systemd service:

### 1. Create service file

```bash
sudo nano /etc/systemd/system/telecommand.service
```

### 2. Add configuration

```ini
[Unit]
Description=TeleCommand Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/telecommand
ExecStart=/usr/bin/python3 /path/to/telecommand/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Enable and start service

```bash
sudo systemctl daemon-reload
sudo systemctl enable telecommand
sudo systemctl start telecommand
sudo systemctl status telecommand
```

### 4. View logs

```bash
sudo journalctl -u telecommand -f
```

### Windows (Task Scheduler)

To run the bot on Windows startup:

**1. Create a batch file (run_bot.bat):**
```batch
@echo off
cd /d C:\path\to\telegram_bot
call venv\Scripts\activate.bat
python bot.py
```

**2. Open Task Scheduler:**
- Press `Win + R`, type `taskschd.msc`, press Enter

**3. Create Basic Task:**
- Click "Create Basic Task"
- Name: "TeleCommand"
- Trigger: "When the computer starts"
- Action: "Start a program"
- Program: `C:\path\to\telegram_bot\run_bot.bat`
- Check "Run with highest privileges"

**4. Alternative - NSSM (Non-Sucking Service Manager):**
```cmd
# Download NSSM from https://nssm.cc/
nssm install TelegramBot "C:\path\to\telegram_bot\venv\Scripts\python.exe" "C:\path\to\telegram_bot\bot.py"
nssm start TelegramBot
```

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>Bot doesn't respond</b></summary>

**Solutions:**
- Check if bot is running: `ps aux | grep bot.py` (Linux/macOS) or Task Manager (Windows)
- Verify bot token is correct in `config.json`
- Check `bot.log` for error messages
- Ensure internet connection is stable
- Verify bot isn't blocked by firewall

</details>

<details>
<summary><b>"Unauthorized" message in Telegram</b></summary>

**Solutions:**
- Confirm your user ID is in `authorized_users` array
- User IDs must be numbers, not @usernames
- Restart bot after modifying `config.json`
- Check for typos in user ID
- Get your ID again from @userinfobot

</details>

<details>
<summary><b>Commands timing out</b></summary>

**Solutions:**
- Increase `command_timeout` in config.json
- Test command in terminal first
- Some system commands are naturally slow
- Check system resources (CPU, memory)
- Try breaking complex commands into simpler ones

</details>

<details>
<summary><b>Command not allowed</b></summary>

**Solutions:**
- Check command is in `allowed_commands` list
- Set `whitelist_enabled: false` for testing
- Add command base name only (e.g., `ls`, not `/bin/ls`)
- Check for typos in command name
- Review whitelist configuration

</details>

<details>
<summary><b>Module not found errors</b></summary>

**Solutions:**
- Activate virtual environment first
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python3 --version` (must be 3.8+)
- Try deleting `venv/` and running setup again

</details>

## ❓ FAQ

**Q: Can I use this on multiple servers?**  
A: Yes! Install the bot on each server with the same bot token. Each instance will respond to commands sent to that specific bot.

**Q: How do I add multiple users?**  
A: Add their user IDs to the `authorized_users` array in config.json:
```json
"authorized_users": [123456789, 987654321, 555555555]
```

**Q: Can I use this bot on my Raspberry Pi?**  
A: Yes! It works on any device that runs Python 3.8+, including Raspberry Pi, ARM-based systems, etc.

**Q: Is it safe to expose my system this way?**  
A: When properly configured with authentication and whitelisting, it's secure. Always follow security best practices and monitor logs.

**Q: Can I run multiple bots on the same server?**  
A: Yes! Create separate directories and use different bot tokens for each instance.

**Q: How do I update the bot?**  
A: Pull latest changes: `git pull origin main`, then restart the bot.

**Q: Does this work behind a firewall/NAT?**  
A: Yes! The bot makes outbound connections to Telegram servers, so no port forwarding is needed.

## 📊 Logs & Monitoring

All bot activities are logged to:
- **Console**: Real-time output while running
- **bot.log**: Persistent file with timestamps

### Log Contents

- ✅ Successful command executions
- ❌ Failed command attempts
- 🚫 Unauthorized access attempts
- ⚠️ Errors and exceptions
- 🔄 Bot lifecycle events

### View Live Logs

```bash
# Linux/macOS
tail -f bot.log

# Windows (PowerShell)
Get-Content bot.log -Wait -Tail 50
```

### Log Rotation (Linux)

Create `/etc/logrotate.d/telegram-bot`:
```
/path/to/telecommand/bot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## 🤝 Contributing

Contributions are welcome! Here are some ways you can contribute:

### Ideas for Enhancement

- 📁 File upload/download capabilities
- ⏰ Scheduled command execution
- 📈 Advanced monitoring dashboards
- 🌐 Web interface
- 🔄 Multi-host management
- 📊 Command output visualization
- 🔔 Alert notifications
- 🔒 Two-factor authentication

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Setup

```bash
git clone https://github.com/yourusername/telecommand.git
cd telecommand
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📁 Project Structure

```
telecommand/
├── bot.py                          # Main bot application
├── config.json                     # Configuration file (gitignored)
├── config.example.json             # Example configuration
├── requirements.txt                # Python dependencies
├── setup.sh                        # Setup script (Linux/macOS)
├── setup.bat                       # Setup script (Windows)
├── README.md                       # This file
├── PLATFORM_GUIDE.md               # Platform-specific guide
├── telecommand.service   # Systemd service template
├── .gitignore                      # Git ignore rules
└── venv/                           # Virtual environment (gitignored)
```

## 🔒 Security Best Practices

### Essential Security Measures

1. **🔑 Protect Your Token**
   - Never commit `config.json` to version control
   - Use environment variables in production
   - Rotate tokens periodically

2. **👥 Whitelist Users Carefully**
   - Only add trusted user IDs
   - Regularly review authorized users
   - Remove inactive users

3. **✅ Enable Command Whitelist**
   - Use `whitelist_enabled: true` in production
   - Only allow necessary commands
   - Avoid wildcards in production

4. **📝 Monitor Logs**
   - Regularly check `bot.log`
   - Set up log rotation
   - Alert on suspicious activity

5. **🛡️ Run with Limited Permissions**
   - Don't run as root/administrator unless necessary
   - Use dedicated service account
   - Apply principle of least privilege

### Using Environment Variables

For enhanced security, use environment variables:

```bash
# Set environment variable
export TELEGRAM_BOT_TOKEN="your_token_here"
export AUTHORIZED_USER_ID="123456789"

# Run bot
python3 bot.py
```

Modify `bot.py` to read from environment:
```python
import os

# In load_config or main:
token = os.getenv('TELEGRAM_BOT_TOKEN') or config.get('telegram_token')
```

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2026 TeleCommand Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## ⚠️ Disclaimer

**IMPORTANT: READ BEFORE USE**

This bot executes OS-level commands with the permissions of the user running it. Improper use or misconfiguration can lead to:

- ⚠️ System damage or data loss
- 🔓 Security vulnerabilities
- 📊 Resource exhaustion
- ⚙️ Service disruptions

**By using this software, you acknowledge that:**

1. You understand the security implications
2. You will follow all security best practices
3. You accept full responsibility for its use
4. You will test in a safe environment first
5. The authors are not liable for any damages

**Security Checklist Before Production Use:**

- [ ] Bot token is kept secret and not committed to version control
- [ ] Only trusted users are in `authorized_users` list
- [ ] Command whitelist is enabled (`whitelist_enabled: true`)
- [ ] Only necessary commands are whitelisted
- [ ] Bot runs with limited user permissions (not root/admin)
- [ ] Logs are monitored regularly
- [ ] Firewall rules are properly configured
- [ ] System is regularly updated and patched
- [ ] Backups are in place

## 💬 Support & Community

### Getting Help

1. **Check Documentation**
   - Read this README thoroughly
   - Review [PLATFORM_GUIDE.md](PLATFORM_GUIDE.md) for OS-specific help
   - Check the [FAQ](#-faq) section

2. **Check Logs**
   - Review `bot.log` for error messages
   - Look for patterns in failed commands

3. **Test Locally**
   - Try commands in your terminal first
   - Verify bot token and user ID
   - Check Python version compatibility

4. **Community Support**
   - Open an issue on GitHub
   - Search existing issues first
   - Provide logs and configuration (remove sensitive data)

### Reporting Issues

When reporting issues, include:
- Operating system and version
- Python version
- Error messages from `bot.log`
- Steps to reproduce
- Expected vs actual behavior

**Example:**
```
OS: Ubuntu 22.04 LTS
Python: 3.10.4
Issue: Bot doesn't respond to /exec commands
Error in log: [paste relevant log lines]
Steps: 1. Start bot, 2. Send /exec uptime, 3. No response
```

## 🌟 Acknowledgments

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- Python 3.8+ - Programming language
- Love ❤️ and coffee ☕

## 📈 Changelog

### Version 1.0.0 (February 2026)
- ✨ Initial release
- ✅ Cross-platform support (Windows, Linux, macOS)
- 🔐 User authentication system
- ✅ Command whitelist functionality
- 🖥️ System monitoring commands
- 📊 Interactive menu system
- 📜 Command history tracking
- 📝 Comprehensive logging
- ⏱️ Command timeout protection
- 🌐 Platform-specific command adaptation

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

Made with ❤️ for sysadmins and DevOps engineers

[Report Bug](https://github.com/Sushilsin/TeleCommand-Pro/issues) · [Request Feature](https://github.com/Sushilsin/TeleCommand-Pro/issues) · [Documentation](https://github.com/Sushilsin/TeleCommand-Pro)

</div>
