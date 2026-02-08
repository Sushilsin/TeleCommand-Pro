#!/usr/bin/env python3
"""
TeleCommand Pro Web Portal
Web interface for managing the bot, users, and viewing command logs
"""

import os
import json
import sqlite3
import subprocess
import signal
import time
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DATABASE'] = 'telecommand.db'
app.config['BOT_PID_FILE'] = 'bot.pid'
app.config['BOT_SCRIPT'] = 'bot.py'


# Database functions
def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Initialize database with tables"""
    db = get_db()
    
    # Create tables with current schema
    db.executescript('''
        CREATE TABLE IF NOT EXISTS portal_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            email TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS telegram_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            is_active INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id INTEGER,
            command TEXT NOT NULL,
            output TEXT,
            success INTEGER,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (telegram_user_id) REFERENCES telegram_users (user_id)
        );
        
        CREATE TABLE IF NOT EXISTS bot_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # Create default admin user if not exists
    cursor = db.execute('SELECT * FROM portal_users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        db.execute('INSERT INTO portal_users (username, password_hash, role, email) VALUES (?, ?, ?, ?)',
                   ('admin', generate_password_hash('admin123'), 'admin', 'admin@telecommand.local'))
    
    # Migration: Add missing columns to existing tables
    try:
        # Check if role column exists
        db.execute('SELECT role FROM portal_users LIMIT 1')
    except sqlite3.OperationalError:
        # Add role, email, is_active columns if they don't exist
        try:
            db.execute('ALTER TABLE portal_users ADD COLUMN role TEXT DEFAULT \'viewer\'')
        except sqlite3.OperationalError:
            pass
        try:
            db.execute('ALTER TABLE portal_users ADD COLUMN email TEXT')
        except sqlite3.OperationalError:
            pass
        try:
            db.execute('ALTER TABLE portal_users ADD COLUMN is_active INTEGER DEFAULT 1')
        except sqlite3.OperationalError:
            pass
    
    # Ensure admin user has admin role
    db.execute('''UPDATE portal_users SET role = ? 
                  WHERE username = ? AND (role IS NULL OR role = \'\' OR role = \'viewer\')''',
               ('admin', 'admin'))
    
    db.commit()
    db.close()


# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        
        db = get_db()
        user = db.execute('SELECT role FROM portal_users WHERE id = ?', (session['user_id'],)).fetchone()
        db.close()
        
        if not user or user['role'] != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


# Config management
def load_bot_config():
    """Load bot configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'telegram_token': '',
            'authorized_users': [],
            'whitelist_enabled': False,
            'allowed_commands': [],
            'command_timeout': 30
        }


def save_bot_config(config):
    """Save bot configuration to config.json"""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)


# Bot process management
def get_bot_pid():
    """Get bot process PID from file"""
    try:
        if os.path.exists(app.config['BOT_PID_FILE']):
            with open(app.config['BOT_PID_FILE'], 'r') as f:
                return int(f.read().strip())
    except:
        pass
    return None


def save_bot_pid(pid):
    """Save bot process PID to file"""
    with open(app.config['BOT_PID_FILE'], 'w') as f:
        f.write(str(pid))


def is_bot_running():
    """Check if bot process is running"""
    pid = get_bot_pid()
    if not pid:
        return False
    try:
        # Send signal 0 to check if process exists
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        # Process doesn't exist, clean up PID file
        if os.path.exists(app.config['BOT_PID_FILE']):
            os.remove(app.config['BOT_PID_FILE'])
        return False


def start_bot():
    """Start the bot process"""
    if is_bot_running():
        return {'success': False, 'message': 'Bot is already running'}
    
    try:
        # Start bot process
        process = subprocess.Popen(
            ['python3', app.config['BOT_SCRIPT']],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        save_bot_pid(process.pid)
        time.sleep(2)  # Give it time to start
        
        if is_bot_running():
            return {'success': True, 'message': f'Bot started successfully (PID: {process.pid})'}
        else:
            return {'success': False, 'message': 'Bot failed to start'}
    except Exception as e:
        return {'success': False, 'message': f'Error starting bot: {str(e)}'}


def stop_bot():
    """Stop the bot process"""
    if not is_bot_running():
        return {'success': False, 'message': 'Bot is not running'}
    
    pid = get_bot_pid()
    try:
        # Send SIGTERM to gracefully stop the bot
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)  # Wait for graceful shutdown
        
        # Check if still running
        if is_bot_running():
            # Force kill if still running
            os.kill(pid, signal.SIGKILL)
            time.sleep(1)
        
        # Clean up PID file
        if os.path.exists(app.config['BOT_PID_FILE']):
            os.remove(app.config['BOT_PID_FILE'])
        
        return {'success': True, 'message': 'Bot stopped successfully'}
    except Exception as e:
        return {'success': False, 'message': f'Error stopping bot: {str(e)}'}


def restart_bot():
    """Restart the bot process"""
    stop_result = stop_bot()
    if not stop_result['success'] and 'not running' not in stop_result['message']:
        return stop_result
    
    time.sleep(1)
    return start_bot()


# Routes
@app.route('/')
@login_required
def index():
    """Dashboard"""
    db = get_db()
    
    # Get bot status
    bot_status = {
        'running': is_bot_running(),
        'pid': get_bot_pid()
    }
    
    # Get statistics
    stats = {
        'total_users': db.execute('SELECT COUNT(*) FROM telegram_users WHERE is_active = 1').fetchone()[0],
        'total_commands': db.execute('SELECT COUNT(*) FROM command_logs').fetchone()[0],
        'successful_commands': db.execute('SELECT COUNT(*) FROM command_logs WHERE success = 1').fetchone()[0],
        'failed_commands': db.execute('SELECT COUNT(*) FROM command_logs WHERE success = 0').fetchone()[0],
    }
    
    # Recent commands
    recent_commands = db.execute('''
        SELECT cl.*, tu.username, tu.first_name 
        FROM command_logs cl
        LEFT JOIN telegram_users tu ON cl.telegram_user_id = tu.user_id
        ORDER BY cl.executed_at DESC
        LIMIT 10
    ''').fetchall()
    
    # Active users
    active_users = db.execute('''
        SELECT * FROM telegram_users 
        WHERE is_active = 1 
        ORDER BY last_seen DESC
    ''').fetchall()
    
    db.close()
    
    return render_template('dashboard.html', stats=stats, recent_commands=recent_commands, active_users=active_users, bot_status=bot_status)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        user = db.execute('SELECT * FROM portal_users WHERE username = ?', (username,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['password_hash'], password):
            if user['is_active']:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Account is disabled', 'error')
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route('/portal-users')
@admin_required
def portal_users():
    """Portal user management page (admin only)"""
    db = get_db()
    users = db.execute('SELECT id, username, role, email, is_active, created_at FROM portal_users ORDER BY created_at DESC').fetchall()
    db.close()
    
    return render_template('portal_users.html', users=users)


@app.route('/portal-users/add', methods=['POST'])
@admin_required
def add_portal_user():
    """Add new portal user"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'viewer')
    email = request.form.get('email', '').strip()
    
    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('portal_users'))
    
    if role not in ['admin', 'viewer']:
        flash('Invalid role', 'error')
        return redirect(url_for('portal_users'))
    
    try:
        db = get_db()
        db.execute('''
            INSERT INTO portal_users (username, password_hash, role, email)
            VALUES (?, ?, ?, ?)
        ''', (username, generate_password_hash(password), role, email))
        db.commit()
        db.close()
        
        flash(f'User {username} added successfully', 'success')
    except sqlite3.IntegrityError:
        flash(f'Username {username} already exists', 'error')
    except Exception as e:
        flash(f'Error adding user: {str(e)}', 'error')
    
    return redirect(url_for('portal_users'))


@app.route('/portal-users/toggle/<int:user_id>', methods=['POST'])
@admin_required
def toggle_portal_user(user_id):
    """Toggle portal user active status"""
    # Prevent disabling yourself
    if user_id == session['user_id']:
        flash('Cannot disable your own account', 'error')
        return redirect(url_for('portal_users'))
    
    db = get_db()
    user = db.execute('SELECT username, is_active FROM portal_users WHERE id = ?', (user_id,)).fetchone()
    
    if user:
        new_status = 0 if user['is_active'] else 1
        db.execute('UPDATE portal_users SET is_active = ? WHERE id = ?', (new_status, user_id))
        db.commit()
        status_text = 'enabled' if new_status else 'disabled'
        flash(f'User {user["username"]} {status_text} successfully', 'success')
    else:
        flash('User not found', 'error')
    
    db.close()
    return redirect(url_for('portal_users'))


@app.route('/portal-users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_portal_user(user_id):
    """Delete portal user"""
    # Prevent deleting yourself
    if user_id == session['user_id']:
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('portal_users'))
    
    db = get_db()
    user = db.execute('SELECT username FROM portal_users WHERE id = ?', (user_id,)).fetchone()
    
    if user:
        db.execute('DELETE FROM portal_users WHERE id = ?', (user_id,))
        db.commit()
        flash(f'User {user["username"]} deleted successfully', 'success')
    else:
        flash('User not found', 'error')
    
    db.close()
    return redirect(url_for('portal_users'))


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    db = get_db()
    user = db.execute('SELECT id, username, role, email, created_at FROM portal_users WHERE id = ?', (session['user_id'],)).fetchone()
    db.close()
    
    return render_template('profile.html', user=user)


@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not current_password or not new_password or not confirm_password:
        flash('All fields are required', 'error')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('profile'))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters', 'error')
        return redirect(url_for('profile'))
    
    db = get_db()
    user = db.execute('SELECT password_hash FROM portal_users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user or not check_password_hash(user['password_hash'], current_password):
        flash('Current password is incorrect', 'error')
        db.close()
        return redirect(url_for('profile'))
    
    db.execute('UPDATE portal_users SET password_hash = ? WHERE id = ?',
               (generate_password_hash(new_password), session['user_id']))
    db.commit()
    db.close()
    
    flash('Password changed successfully', 'success')
    return redirect(url_for('profile'))


@app.route('/users')
@login_required
def users():
    """Telegram user management page"""
    db = get_db()
    telegram_users = db.execute('SELECT * FROM telegram_users ORDER BY added_at DESC').fetchall()
    db.close()
    
    config = load_bot_config()
    
    return render_template('users.html', users=telegram_users, authorized_ids=config.get('authorized_users', []))


@app.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    """Add new authorized user (admin only)"""
    user_id = request.form.get('user_id')
    username = request.form.get('username', '')
    first_name = request.form.get('first_name', '')
    
    if not user_id:
        flash('User ID is required', 'error')
        return redirect(url_for('users'))
    
    try:
        user_id = int(user_id)
        
        # Add to database
        db = get_db()
        db.execute('''
            INSERT OR REPLACE INTO telegram_users (user_id, username, first_name, is_active)
            VALUES (?, ?, ?, 1)
        ''', (user_id, username, first_name))
        db.commit()
        db.close()
        
        # Update config.json
        config = load_bot_config()
        if user_id not in config['authorized_users']:
            config['authorized_users'].append(user_id)
            save_bot_config(config)
        
        flash(f'User {user_id} added successfully', 'success')
    except ValueError:
        flash('Invalid user ID', 'error')
    except Exception as e:
        flash(f'Error adding user: {str(e)}', 'error')
    
    return redirect(url_for('users'))


@app.route('/users/remove/<int:user_id>', methods=['POST'])
@admin_required
def remove_user(user_id):
    """Remove authorized user (admin only)"""
    # Update database
    db = get_db()
    db.execute('UPDATE telegram_users SET is_active = 0 WHERE user_id = ?', (user_id,))
    db.commit()
    db.close()
    
    # Update config.json
    config = load_bot_config()
    if user_id in config['authorized_users']:
        config['authorized_users'].remove(user_id)
        save_bot_config(config)
    
    flash(f'User {user_id} removed successfully', 'success')
    return redirect(url_for('users'))


@app.route('/logs')
@login_required
def logs():
    """Command logs page"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    db = get_db()
    
    # Get total count
    total = db.execute('SELECT COUNT(*) FROM command_logs').fetchone()[0]
    
    # Get paginated logs
    command_logs = db.execute('''
        SELECT cl.*, tu.username, tu.first_name 
        FROM command_logs cl
        LEFT JOIN telegram_users tu ON cl.telegram_user_id = tu.user_id
        ORDER BY cl.executed_at DESC
        LIMIT ? OFFSET ?
    ''', (per_page, (page - 1) * per_page)).fetchall()
    
    db.close()
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('logs.html', logs=command_logs, page=page, total_pages=total_pages)


@app.route('/logs/<int:log_id>')
@login_required
def log_detail(log_id):
    """View detailed log"""
    db = get_db()
    log = db.execute('''
        SELECT cl.*, tu.username, tu.first_name, tu.last_name
        FROM command_logs cl
        LEFT JOIN telegram_users tu ON cl.telegram_user_id = tu.user_id
        WHERE cl.id = ?
    ''', (log_id,)).fetchone()
    db.close()
    
    if not log:
        flash('Log not found', 'error')
        return redirect(url_for('logs'))
    
    return render_template('log_detail.html', log=log)


@app.route('/config', methods=['GET', 'POST'])
@login_required
def config():
    """Bot configuration page"""
    if request.method == 'POST':
        # Check admin role for modifications
        if session.get('role') != 'admin':
            flash('Admin access required to modify configuration', 'error')
            return redirect(url_for('config'))
        
        config = load_bot_config()
        
        config['telegram_token'] = request.form.get('telegram_token', config.get('telegram_token', ''))
        config['whitelist_enabled'] = request.form.get('whitelist_enabled') == 'on'
        config['command_timeout'] = int(request.form.get('command_timeout', 30))
        
        # Parse allowed commands
        allowed_commands = request.form.get('allowed_commands', '').strip()
        if allowed_commands:
            config['allowed_commands'] = [cmd.strip() for cmd in allowed_commands.split('\n') if cmd.strip()]
        else:
            config['allowed_commands'] = []
        
        save_bot_config(config)
        flash('Configuration updated successfully', 'success')
        return redirect(url_for('config'))
    
    config = load_bot_config()
    allowed_commands_str = '\n'.join(config.get('allowed_commands', []))
    
    return render_template('config.html', config=config, allowed_commands_str=allowed_commands_str)


@app.route('/api/log', methods=['POST'])
def api_log():
    """API endpoint for bot to log commands"""
    data = request.json
    
    db = get_db()
    db.execute('''
        INSERT INTO command_logs (telegram_user_id, command, output, success)
        VALUES (?, ?, ?, ?)
    ''', (data.get('user_id'), data.get('command'), data.get('output'), data.get('success', 0)))
    
    # Update last seen
    db.execute('''
        UPDATE telegram_users 
        SET last_seen = CURRENT_TIMESTAMP 
        WHERE user_id = ?
    ''', (data.get('user_id'),))
    
    db.commit()
    db.close()
    
    return jsonify({'status': 'success'})


@app.route('/api/bot/status')
@login_required
def api_bot_status():
    """Get bot status"""
    return jsonify({
        'running': is_bot_running(),
        'pid': get_bot_pid()
    })


@app.route('/api/bot/start', methods=['POST'])
@admin_required
def api_bot_start():
    """Start the bot (admin only)"""
    result = start_bot()
    return jsonify(result)


@app.route('/api/bot/stop', methods=['POST'])
@admin_required
def api_bot_stop():
    """Stop the bot (admin only)"""
    result = stop_bot()
    return jsonify(result)


@app.route('/api/bot/restart', methods=['POST'])
@admin_required
def api_bot_restart():
    """Restart the bot (admin only)"""
    result = restart_bot()
    return jsonify(result)


@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for statistics"""
    db = get_db()
    
    # Commands per day (last 7 days)
    daily_stats = db.execute('''
        SELECT DATE(executed_at) as date, COUNT(*) as count
        FROM command_logs
        WHERE executed_at >= DATE('now', '-7 days')
        GROUP BY DATE(executed_at)
        ORDER BY date
    ''').fetchall()
    
    # Top commands
    top_commands = db.execute('''
        SELECT command, COUNT(*) as count
        FROM command_logs
        WHERE command NOT LIKE '/start%' AND command NOT LIKE '/help%'
        GROUP BY command
        ORDER BY count DESC
        LIMIT 10
    ''').fetchall()
    
    db.close()
    
    return jsonify({
        'daily': [{'date': row['date'], 'count': row['count']} for row in daily_stats],
        'top_commands': [{'command': row['command'], 'count': row['count']} for row in top_commands]
    })


if __name__ == '__main__':
    init_db()
    print('=' * 50)
    print('TeleCommand Pro Web Portal')
    print('=' * 50)
    print('Portal running at: http://localhost:5000')
    print('=' * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
