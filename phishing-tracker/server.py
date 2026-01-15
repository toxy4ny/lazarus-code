#!/usr/bin/env python3
"""
Phishing Campaign Tracker Server
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import json
import logging

app = Flask(__name__)
CORS(app)

DATABASE = 'phishing_campaign.db'
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.company.local')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', 'security-awareness@company.local')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'security-team@company.local')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phishing_tracker.log'),
        logging.StreamHandler()
    ]
)

def init_db():
   
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS victims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        username TEXT,
        hostname TEXT,
        os TEXT,
        os_version TEXT,
        workspace TEXT,
        vscode_version TEXT,
        event TEXT,
        campaign TEXT,
        email_sent INTEGER DEFAULT 0,
        ip_address TEXT,
        user_agent TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL,
        active INTEGER DEFAULT 1,
        total_targets INTEGER DEFAULT 0,
        total_victims INTEGER DEFAULT 0
    )''')
    
    conn.commit()
    conn.close()
    logging.info("Database initialized successfully")

@app.route('/api/log', methods=['POST'])
def log_event():
   
    try:
        data = request.json
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        logging.info(f"New victim: {data.get('username')}@{data.get('hostname')} from {ip_address}")
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''INSERT INTO victims 
                     (timestamp, username, hostname, os, os_version, workspace, 
                      vscode_version, event, campaign, ip_address, user_agent)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data.get('timestamp'),
                   data.get('username'),
                   data.get('hostname'),
                   data.get('os') or data.get('platform'),
                   data.get('os_version'),
                   data.get('workspace') or data.get('workspaceFolder'),
                   data.get('vscode_version') or data.get('vsCodeVersion'),
                   data.get('event'),
                   data.get('campaign'),
                   ip_address,
                   user_agent))
        
        victim_id = c.lastrowid
        conn.commit()
        conn.close()
        
        update_campaign_stats(data.get('campaign'))
        
        email = get_user_email(data.get('username'))
        if email:
            try:
                send_awareness_email(email, data)
                mark_email_sent(victim_id)
            except Exception as e:
                logging.error(f"Failed to send email to {email}: {e}")
        
        return jsonify({"status": "ok", "id": victim_id}), 200
        
    except Exception as e:
        logging.error(f"Error processing log: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
   
    try:
        campaign_id = request.args.get('campaign')
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        if campaign_id:
            c.execute('''SELECT * FROM victims 
                        WHERE campaign = ? 
                        ORDER BY timestamp DESC''', (campaign_id,))
        else:
            c.execute('SELECT * FROM victims ORDER BY timestamp DESC')
        
        columns = [description[0] for description in c.description]
        results = [dict(zip(columns, row)) for row in c.fetchall()]
        
        conn.close()
        
        return jsonify({
            "status": "ok",
            "count": len(results),
            "victims": results
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting stats: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/campaigns', methods=['GET', 'POST'])
def manage_campaigns():
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    if request.method == 'GET':
        c.execute('SELECT * FROM campaigns ORDER BY created_at DESC')
        columns = [description[0] for description in c.description]
        results = [dict(zip(columns, row)) for row in c.fetchall()]
        conn.close()
        return jsonify({"status": "ok", "campaigns": results}), 200
    
    elif request.method == 'POST':
        data = request.json
        try:
            c.execute('''INSERT INTO campaigns 
                        (campaign_id, name, description, created_at, total_targets)
                        VALUES (?, ?, ?, ?, ?)''',
                     (data['campaign_id'],
                      data['name'],
                      data.get('description', ''),
                      datetime.now().isoformat(),
                      data.get('total_targets', 0)))
            conn.commit()
            conn.close()
            return jsonify({"status": "ok"}), 201
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"status": "error", "message": "Campaign already exists"}), 400

@app.route('/dashboard')
def dashboard():
   
    return render_template_string(DASHBOARD_HTML)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200


def get_user_email(username):
   
    if username:
        return f"{username}@company.local"
    return None

def send_awareness_email(to_email, victim_data):
  
    subject = "🎓 Результат теста на осведомлённость о фишинге"
    
    body = f"""
Здравствуйте, {victim_data.get('username', 'Коллега')}!

Вы только что приняли участие в учебном тесте на осведомлённость о кибербезопасности.

═══════════════════════════════════════════════════════════════
📊 РЕЗУЛЬТАТЫ ТЕСТА
═══════════════════════════════════════════════════════════════

❌ К сожалению, вы попались на имитацию фишинговой атаки.

🕐 Время события: {victim_data.get('timestamp')}
💻 Компьютер: {victim_data.get('hostname')}
📁 Проект: {victim_data.get('workspace', 'N/A')}

═══════════════════════════════════════════════════════════════
🎯 ЧТО ПРОИЗОШЛО?
═══════════════════════════════════════════════════════════════

Вы открыли проект из неизвестного источника в VS Code и согласились
доверять авторам проекта ("Trust workspace"), что привело к автоматическому
выполнению вредоносного кода из файла .vscode/tasks.json.

Это реальная техника, используемая APT-группировками (например, Lazarus Group)
для компрометации разработчиков через фишинговые предложения работы.

═══════════════════════════════════════════════════════════════
🚨 РЕАЛЬНЫЕ ПОСЛЕДСТВИЯ
═══════════════════════════════════════════════════════════════

В реальном сценарии атакующие могли бы:

✗ Украсть криптовалютные ключи и seed-фразы
✗ Получить доступ к паролям и токенам из браузеров
✗ Установить backdoor для удалённого управления
✗ Похитить исходный код и интеллектуальную собственность
✗ Использовать ваш компьютер для дальнейших атак

═══════════════════════════════════════════════════════════════
🛡️ КАК ЗАЩИТИТЬСЯ?
═══════════════════════════════════════════════════════════════

1. ВСЕГДА проверяйте источник кода перед открытием
   ✓ Кто автор репозитория?
   ✓ Есть ли у него репутация?
   ✓ Запрашивали ли вы этот код?

2. ИЗУЧАЙТЕ содержимое .vscode/tasks.json перед доверием
   ✓ Есть ли параметр "runOn": "folderOpen"?
   ✓ Какие команды выполняются?
   ✓ Запускаются ли неизвестные скрипты?

3. ИСПОЛЬЗУЙТЕ изолированные среды для неизвестного кода
   ✓ Виртуальные машины (VirtualBox, VMware)
   ✓ Docker-контейнеры
   ✓ Песочницы (Windows Sandbox)

4. ПРОВЕРЯЙТЕ предложения о работе
   ✓ Существует ли компания реально?
   ✓ Есть ли информация о вакансии на официальном сайте?
   ✓ Соответствует ли email домену компании?

5. БУДЬТЕ СКЕПТИЧНЫ к слишком хорошим предложениям
   ✓ Завышенная зарплата без собеседования
   ✓ Срочность и давление
   ✓ Необычные технические задания

═══════════════════════════════════════════════════════════════
📚 ДОПОЛНИТЕЛЬНЫЕ МАТЕРИАЛЫ
═══════════════════════════════════════════════════════════════

• Статья о Lazarus Group и "Contagious Interview":
  https://opensourcemalware.com/blog/contagious-interview-vscode

• Настройка безопасности VS Code:
  https://code.visualstudio.com/docs/editor/workspace-trust

• Защита от social engineering:
  [ссылка на внутренний портал]

═══════════════════════════════════════════════════════════════
❓ ВОПРОСЫ?
═══════════════════════════════════════════════════════════════

Если у вас есть вопросы о безопасности или вы заметили
подозрительную активность, обращайтесь:

📧 Email: security-team@company.local
📞 Телефон: +7 (XXX) XXX-XX-XX
💬 Slack: #security-incidents

═══════════════════════════════════════════════════════════════

Помните: осведомлённость — ваша первая линия защиты! 🛡️

--
Команда информационной безопасности
Company Name
"""
    
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logging.info(f"Awareness email sent to {to_email}")
        
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        raise

def mark_email_sent(victim_id):

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE victims SET email_sent = 1 WHERE id = ?', (victim_id,))
    conn.commit()
    conn.close()

def update_campaign_stats(campaign_id):
  
    if not campaign_id:
        return
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM victims WHERE campaign = ?', (campaign_id,))
    total_victims = c.fetchone()[0]
    
    c.execute('''UPDATE campaigns 
                 SET total_victims = ? 
                 WHERE campaign_id = ?''', (total_victims, campaign_id))
    
    conn.commit()
    conn.close()

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Phishing Campaign Dashboard</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { margin-bottom: 30px; color: #f1f5f9; }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #1e293b;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #334155;
        }
        .stat-value { 
            font-size: 36px; 
            font-weight: bold; 
            color: #60a5fa;
            margin: 10px 0;
        }
        .stat-label { 
            color: #94a3b8; 
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        table {
            width: 100%;
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }
        th {
            background: #0f172a;
            color: #f1f5f9;
            font-weight: 600;
        }
        tr:hover { background: #293548; }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-success { background: #166534; color: #86efac; }
        .badge-danger { background: #991b1b; color: #fca5a5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Phishing Campaign Dashboard</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Total Victims</div>
                <div class="stat-value" id="totalVictims">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Today</div>
                <div class="stat-value" id="todayVictims">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Emails Sent</div>
                <div class="stat-value" id="emailsSent">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value" id="successRate">0%</div>
            </div>
        </div>
        
        <h2 style="margin-bottom: 20px;">Recent Victims</h2>
        <table id="victimsTable">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Username</th>
                    <th>Hostname</th>
                    <th>OS</th>
                    <th>IP Address</th>
                    <th>Email</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>
    
    <script>
        async function loadStats() {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            document.getElementById('totalVictims').textContent = data.count;
            
            const today = new Date().toISOString().split('T')[0];
            const todayCount = data.victims.filter(v => v.timestamp.startsWith(today)).length;
            document.getElementById('todayVictims').textContent = todayCount;
            
            const emailsSent = data.victims.filter(v => v.email_sent === 1).length;
            document.getElementById('emailsSent').textContent = emailsSent;
            
            // Assuming 100 total targets for demo
            const successRate = ((data.count / 100) * 100).toFixed(1);
            document.getElementById('successRate').textContent = successRate + '%';
            
            const tbody = document.querySelector('#victimsTable tbody');
            tbody.innerHTML = '';
            
            data.victims.forEach(victim => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${new Date(victim.timestamp).toLocaleString()}</td>
                    <td>${victim.username || 'N/A'}</td>
                    <td>${victim.hostname || 'N/A'}</td>
                    <td>${victim.os || 'N/A'}</td>
                    <td>${victim.ip_address || 'N/A'}</td>
                    <td>
                        <span class="badge ${victim.email_sent ? 'badge-success' : 'badge-danger'}">
                            ${victim.email_sent ? 'Sent' : 'Pending'}
                        </span>
                    </td>
                `;
            });
        }
        
        loadStats();
        setInterval(loadStats, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    init_db()
   
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO campaigns 
                    (campaign_id, name, description, created_at, total_targets)
                    VALUES (?, ?, ?, ?, ?)''',
                 ('contagious-interview-2026',
                  'Contagious Interview 2026',
                  'VS Code phishing simulation based on Lazarus Group tactics',
                  datetime.now().isoformat(),
                  100))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()
    
    logging.info("Starting phishing tracker server...")
    app.run(host='0.0.0.0', port=5000, debug=False, ssl_context='adhoc')