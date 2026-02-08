#!/usr/bin/env python3
"""
TeleCommand - Telegram Remote Command Bot
A secure bot for managing host systems via Telegram with OS-level command execution
"""

import os
import sys
import platform
import subprocess
import logging
import json
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HostManager:
    """Main bot class for host management"""
    
    def __init__(self, config_path='config.json'):
        """Initialize the bot with configuration"""
        self.config = self.load_config(config_path)
        self.authorized_users = set(self.config.get('authorized_users', []))
        self.allowed_commands = self.config.get('allowed_commands', [])
        self.command_history = []
        self.os_type = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)
        logger.info(f"Detected OS: {self.os_type}")
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {config_path} not found!")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file {config_path}!")
            raise
    
    def is_authorized(self, user_id):
        """Check if user is authorized"""
        return user_id in self.authorized_users
    
    def log_command(self, user_id, username, command, result):
        """Log executed commands"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'username': username,
            'command': command,
            'success': result['success']
        }
        self.command_history.append(entry)
        logger.info(f"Command executed by {username} ({user_id}): {command}")
        
        # Send to web portal
        try:
            requests.post('http://localhost:5000/api/log', json={
                'user_id': user_id,
                'command': command,
                'output': result.get('output', ''),
                'success': 1 if result['success'] else 0
            }, timeout=2)
        except:
            pass  # Silently fail if portal is not running
    
    def execute_command(self, command):
        """Execute OS command with safety checks"""
        try:
            # Security check: verify command is allowed if whitelist is enabled
            if self.config.get('whitelist_enabled', True):
                command_base = command.split()[0] if command else ''
                if command_base not in self.allowed_commands and '*' not in self.allowed_commands:
                    return {
                        'success': False,
                        'output': f"❌ Command '{command_base}' is not in the allowed list.",
                        'error': 'Command not whitelisted'
                    }
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.get('command_timeout', 30)
            )
            
            output = result.stdout if result.stdout else result.stderr
            
            return {
                'success': result.returncode == 0,
                'output': output if output else '✅ Command executed successfully (no output)',
                'error': result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '❌ Command timed out',
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'output': f'❌ Error executing command: {str(e)}',
                'error': str(e)
            }


# Initialize bot manager
bot_manager = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    welcome_message = f"""
👋 Welcome to Host Manager Bot!

🔐 User ID: `{user.id}`
👤 Username: @{user.username or 'N/A'}

This bot allows you to manage your host system remotely.

📋 Available Commands:
/start - Show this welcome message
/help - Show detailed help
/status - Show system status
/exec <command> - Execute OS command
/allowed - List allowed commands
/history - Show command history (last 10)
/sys - Quick system info menu

⚠️ Security Notice:
Only authorized users can execute commands.
All actions are logged for security audit.
"""
    
    if bot_manager.is_authorized(user.id):
        welcome_message += "\n✅ You are authorized to use this bot."
    else:
        welcome_message += "\n❌ You are NOT authorized. Contact the administrator."
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 *Host Manager Bot - Help*

*Basic Commands:*
• `/start` - Welcome message and status
• `/help` - This help message
• `/status` - System status information

*System Management:*
• `/exec <command>` - Execute any allowed OS command
  Example: `/exec ls -la /tmp`
  
• `/sys` - Interactive system info menu with quick actions

• `/allowed` - View list of whitelisted commands

• `/history` - View last 10 executed commands

*Security Features:*
🔐 User authentication
📝 Command logging
⏱ Command timeout protection
✅ Command whitelist (optional)

*Examples:*
`/exec uptime`
`/exec df -h`
`/exec ps aux | head -10`
`/exec systemctl status nginx`

⚠️ *Important:*
All commands are executed with the bot's user permissions.
Be careful with destructive commands!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def check_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Decorator-like function to check authorization"""
    user = update.effective_user
    if not bot_manager.is_authorized(user.id):
        await update.message.reply_text(
            f"❌ Unauthorized access attempt!\n"
            f"User ID: {user.id}\n"
            f"Username: @{user.username or 'N/A'}\n\n"
            f"This incident has been logged."
        )
        logger.warning(f"Unauthorized access attempt by {user.id} (@{user.username})")
        return False
    return True


async def execute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /exec command"""
    user = update.effective_user
    
    # Check authorization
    if not await check_auth(update, context):
        return
    
    # Get command from message
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /exec <command>\n"
            "Example: /exec uptime"
        )
        return
    
    command = ' '.join(context.args)
    
    # Show processing message
    processing_msg = await update.message.reply_text(
        f"⏳ Executing command...\n`{command}`",
        parse_mode='Markdown'
    )
    
    # Execute command
    result = bot_manager.execute_command(command)
    
    # Log command
    bot_manager.log_command(user.id, user.username or 'Unknown', command, result)
    
    # Format output
    output = result['output']
    if len(output) > 4000:
        output = output[:4000] + "\n\n... (output truncated)"
    
    status_icon = "✅" if result['success'] else "❌"
    response = f"{status_icon} *Command Result:*\n\n```\n{output}\n```"
    
    # Update message with result
    await processing_msg.edit_text(response, parse_mode='Markdown')


async def system_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user = update.effective_user
    
    if not await check_auth(update, context):
        return
    
    # Gather system information based on OS
    os_type = bot_manager.os_type
    
    if os_type == 'Windows':
        commands = {
            'Hostname': 'hostname',
            'OS': 'ver',
            'Uptime': 'systeminfo | findstr /C:"System Boot Time"',
            'CPU': 'wmic cpu get name',
            'Memory': 'systeminfo | findstr /C:"Total Physical Memory" /C:"Available Physical Memory"',
            'Disk': 'wmic logicaldisk get name,freespace,size',
            'Users': 'query user',
        }
    elif os_type == 'Linux':
        commands = {
            'Hostname': 'hostname',
            'Uptime': 'uptime',
            'CPU': "top -bn1 | grep 'Cpu(s)' | head -1 || lscpu | grep 'Model name'",
            'Memory': 'free -h | grep Mem',
            'Disk': 'df -h /',
            'Users': 'who',
        }
    else:  # macOS (Darwin)
        commands = {
            'Hostname': 'hostname',
            'Uptime': 'uptime',
            'CPU': "top -l 1 | grep 'CPU usage'",
            'Memory': 'vm_stat',
            'Disk': 'df -h /',
            'Users': 'who',
        }
    
    status_msg = f"🖥 *System Status ({os_type})*\n\n"
    
    for label, cmd in commands.items():
        result = bot_manager.execute_command(cmd)
        if result['success']:
            output = result['output'].strip()
            if len(output) > 200:
                output = output[:200] + '...'
            status_msg += f"*{label}:*\n`{output}`\n\n"
    
    await update.message.reply_text(status_msg, parse_mode='Markdown')


async def allowed_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /allowed command"""
    user = update.effective_user
    
    if not await check_auth(update, context):
        return
    
    whitelist_enabled = bot_manager.config.get('whitelist_enabled', True)
    allowed = bot_manager.allowed_commands
    
    if not whitelist_enabled or '*' in allowed:
        message = "✅ *Allowed Commands:* ALL\n\nWhitelist is disabled. All commands are allowed."
    else:
        commands_list = '\n'.join([f"• `{cmd}`" for cmd in allowed])
        message = f"✅ *Allowed Commands:*\n\n{commands_list}"
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def command_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command"""
    user = update.effective_user
    
    if not await check_auth(update, context):
        return
    
    history = bot_manager.command_history[-10:]  # Last 10 commands
    
    if not history:
        await update.message.reply_text("📝 No command history yet.")
        return
    
    message = "📝 *Command History (Last 10):*\n\n"
    
    for entry in reversed(history):
        timestamp = entry['timestamp'].split('T')[1].split('.')[0]
        status = "✅" if entry['success'] else "❌"
        message += f"{status} `{timestamp}` - @{entry['username']}\n`{entry['command']}`\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def system_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sys command - interactive system menu"""
    user = update.effective_user
    
    if not await check_auth(update, context):
        return
    
    keyboard = [
        [
            InlineKeyboardButton("💻 CPU Info", callback_data='sys_cpu'),
            InlineKeyboardButton("💾 Memory", callback_data='sys_mem'),
        ],
        [
            InlineKeyboardButton("💿 Disk Space", callback_data='sys_disk'),
            InlineKeyboardButton("🌐 Network", callback_data='sys_net'),
        ],
        [
            InlineKeyboardButton("📊 Processes", callback_data='sys_proc'),
            InlineKeyboardButton("⏰ Uptime", callback_data='sys_uptime'),
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data='sys_refresh'),
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🖥 *System Information Menu*\n\nSelect an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    user = query.from_user
    
    if not bot_manager.is_authorized(user.id):
        await query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    await query.answer()
    
    # Command mapping based on OS
    os_type = bot_manager.os_type
    
    if os_type == 'Windows':
        commands = {
            'sys_cpu': ('💻 CPU Information', 'wmic cpu get name,numberofcores,maxclockspeed'),
            'sys_mem': ('💾 Memory Usage', 'systeminfo | findstr /C:"Total Physical Memory" /C:"Available Physical Memory"'),
            'sys_disk': ('💿 Disk Usage', 'wmic logicaldisk get name,freespace,size'),
            'sys_net': ('🌐 Network Info', 'ipconfig /all'),
            'sys_proc': ('📊 Top Processes', 'tasklist /FO TABLE /NH | findstr /V "^$" | more +1'),
            'sys_uptime': ('⏰ System Uptime', 'systeminfo | findstr /C:"System Boot Time"'),
            'sys_refresh': ('🔄 Menu Refreshed', 'echo Menu refreshed'),
        }
    elif os_type == 'Linux':
        commands = {
            'sys_cpu': ('💻 CPU Information', 'lscpu | head -20'),
            'sys_mem': ('💾 Memory Usage', 'free -h'),
            'sys_disk': ('💿 Disk Usage', 'df -h'),
            'sys_net': ('🌐 Network Info', 'ip addr show || ifconfig'),
            'sys_proc': ('📊 Top Processes', 'ps aux --sort=-%mem | head -11'),
            'sys_uptime': ('⏰ System Uptime', 'uptime'),
            'sys_refresh': ('🔄 Menu Refreshed', 'echo "Menu refreshed"'),
        }
    else:  # macOS (Darwin)
        commands = {
            'sys_cpu': ('💻 CPU Information', 'sysctl -n machdep.cpu.brand_string && sysctl -n hw.ncpu'),
            'sys_mem': ('💾 Memory Usage', 'vm_stat'),
            'sys_disk': ('💿 Disk Usage', 'df -h'),
            'sys_net': ('🌐 Network Info', 'ifconfig'),
            'sys_proc': ('📊 Top Processes', 'ps aux -m | head -11'),
            'sys_uptime': ('⏰ System Uptime', 'uptime'),
            'sys_refresh': ('🔄 Menu Refreshed', 'echo "Menu refreshed"'),
        }
    
    if query.data in commands:
        label, cmd = commands[query.data]
        result = bot_manager.execute_command(cmd)
        
        output = result['output'].strip()
        if len(output) > 3500:
            output = output[:3500] + "\n... (truncated)"
        
        response = f"*{label}*\n\n```\n{output}\n```"
        await query.edit_message_text(response, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    user = update.effective_user
    
    if not bot_manager.is_authorized(user.id):
        await update.message.reply_text(
            "❌ You are not authorized to use this bot.\n"
            f"Your User ID: `{user.id}`\n\n"
            "Please contact the administrator to get access.",
            parse_mode='Markdown'
        )
        return
    
    await update.message.reply_text(
        "Use /help to see available commands."
    )


def main():
    """Start the bot"""
    global bot_manager
    
    # Write PID file for process management by web portal
    pid_file = 'bot.pid'
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    
    try:
        # Initialize bot manager
        try:
            bot_manager = HostManager('config.json')
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return
        
        # Get token from config
        token = bot_manager.config.get('telegram_token')
        if not token:
            logger.error("No telegram_token found in config.json!")
            return
        
        # Create application
        application = Application.builder().token(token).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("exec", execute_command))
        application.add_handler(CommandHandler("status", system_status))
        application.add_handler(CommandHandler("allowed", allowed_commands))
        application.add_handler(CommandHandler("history", command_history))
        application.add_handler(CommandHandler("sys", system_menu))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Start bot
        logger.info("🚀 Bot started successfully!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        # Clean up PID file on exit
        if os.path.exists(pid_file):
            os.remove(pid_file)


if __name__ == '__main__':
    main()
