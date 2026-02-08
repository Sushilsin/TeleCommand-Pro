# Platform Compatibility Guide

## Supported Platforms

✅ **Windows** (7, 8, 10, 11, Server 2012+)
✅ **Linux** (Ubuntu, Debian, CentOS, RHEL, Fedora, Arch, etc.)
✅ **macOS** (10.14+)

## System Commands by Platform

### Windows Commands

| Feature | Command |
|---------|---------|
| CPU Info | `wmic cpu get name,numberofcores,maxclockspeed` |
| Memory | `systeminfo \| findstr /C:"Total Physical Memory"` |
| Disk Space | `wmic logicaldisk get name,freespace,size` |
| Network | `ipconfig /all` |
| Processes | `tasklist` |
| Services | `sc query` |
| Uptime | `systeminfo \| findstr /C:"System Boot Time"` |

### Linux Commands

| Feature | Command |
|---------|---------|
| CPU Info | `lscpu` |
| Memory | `free -h` |
| Disk Space | `df -h` |
| Network | `ip addr show` or `ifconfig` |
| Processes | `ps aux` |
| Services | `systemctl status` |
| Uptime | `uptime` |

### macOS Commands

| Feature | Command |
|---------|---------|
| CPU Info | `sysctl -n machdep.cpu.brand_string` |
| Memory | `vm_stat` |
| Disk Space | `df -h` |
| Network | `ifconfig` |
| Processes | `ps aux` |
| Services | `launchctl list` |
| Uptime | `uptime` |

## Installation by Platform

### Windows

**Requirements:**
- Python 3.8+ (install from python.org)
- Telegram account
- Administrator privileges (optional, for system commands)

**Setup:**
```cmd
cd telegram_bot
setup.bat
```

**Edit config.json**, then run:
```cmd
venv\Scripts\activate.bat
python bot.py
```

### Linux

**Requirements:**
- Python 3.8+ (usually pre-installed)
- pip and venv
- Telegram account

**Setup:**
```bash
cd telegram_bot
./setup.sh
```

**Edit config.json**, then run:
```bash
source venv/bin/activate
python3 bot.py
```

### macOS

**Requirements:**
- Python 3.8+ (install via Homebrew or python.org)
- Telegram account

**Setup:**
```bash
cd telegram_bot
./setup.sh
```

**Edit config.json**, then run:
```bash
source venv/bin/activate
python3 bot.py
```

## Common Use Cases

### Windows Server Management
```
/exec sc query w32time
/exec wmic service where "state='running'" get name
/exec tasklist /FI "MEMUSAGE gt 100000"
/exec netstat -ano | findstr :80
```

### Linux Server Management
```
/exec systemctl status nginx
/exec docker ps
/exec journalctl -xe
/exec netstat -tlnp
```

### macOS Management
```
/exec brew list
/exec launchctl list
/exec top -l 1 -n 10
/exec diskutil list
```

## Troubleshooting by Platform

### Windows

**Issue: Command not found**
- Make sure the command exists in `C:\Windows\System32`
- Try running cmd.exe as administrator
- Check if the tool is installed (e.g., wmic)

**Issue: Permission denied**
- Run the bot as administrator
- Check Windows Firewall settings
- Ensure antivirus allows the bot

### Linux

**Issue: Command not found**
- Install required packages: `sudo apt install net-tools` (for ifconfig)
- Check if command is in PATH: `which <command>`
- Use `sudo` prefix if needed (configure in whitelist)

**Issue: Permission denied**
- Add user to required groups (docker, etc.)
- Use sudo for privileged commands
- Check file permissions

### macOS

**Issue: Command not found**
- Install Xcode Command Line Tools: `xcode-select --install`
- Install Homebrew for additional tools
- Check if command is in PATH

**Issue: Permission denied**
- Grant Full Disk Access in System Preferences > Security & Privacy
- Use `sudo` for privileged commands

## Performance Considerations

### Windows
- Command execution may be slower due to cmd.exe overhead
- `wmic` commands can take several seconds
- Use specific queries to improve speed

### Linux
- Generally fastest command execution
- Minimal overhead
- Best for high-frequency monitoring

### macOS
- Similar performance to Linux
- Some system commands may require special permissions
- Gatekeeper may require approval for first run

## Security Considerations

### Windows
- Run the bot with a limited user account when possible
- Use command whitelist to prevent dangerous commands
- Monitor Event Viewer for unauthorized access
- Consider using Windows Firewall to restrict network access

### Linux
- Run the bot with a non-root user
- Use sudo only when necessary (whitelist specific sudo commands)
- Enable AppArmor or SELinux for additional security
- Monitor logs in /var/log

### macOS
- Run with standard user account
- Use System Integrity Protection (SIP)
- Monitor Console app for security events
- Consider using Little Snitch for network monitoring
