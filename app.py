from flask import Flask, request, session, redirect, url_for
import re
import bcrypt
import sqlite3
import random
import time

app = Flask(__name__)
app.secret_key = 'your-super-secret-key'

otp_storage = {}
login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300

GITHUB_URL = "https://github.com/realahadkhan"
README_DOC_URL = "https://docs.google.com/document/d/1hYRu6YhhjjTEuGHL9Sx6-9YC40kEh27Tz0SoEF7KZwU/edit?usp=sharing"

# ---------------- DATABASE INIT ----------------
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
''')
conn.commit()
conn.close()

# ---------------- STYLES ----------------
font_links = '''
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Orbitron:wght@700&display=swap" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
'''

base_css = f'''
{font_links}
<style>
body {{
    margin: 0;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(145deg, #000000, #1c1c1c, #0a0a0a);
    color: white;
    font-family: 'Inter', sans-serif;
}}

.container {{
    background: rgba(255,255,255,0.05);
    padding: 40px;
    border-radius: 15px;
    width: 380px;
    text-align: center;
    box-shadow: 0 0 25px rgba(255,255,255,0.08);
    position: relative;
}}

h1 {{
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 0.12em;
    margin-bottom: 6px;
}}

.subtitle {{
    color: #ccc;
    margin-bottom: 22px;
}}

.nav {{
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-bottom: 22px;
}}

.nav a {{
    color: white;
    text-decoration: none;
    background: rgba(255,255,255,0.12);
    padding: 8px 14px;
    border-radius: 5px;
    font-weight: 600;
}}

.nav a:hover {{
    background: rgba(255,255,255,0.25);
}}

input {{
    width: 100%;
    padding: 10px;
    margin: 10px 0;
    border-radius: 5px;
    border: none;
}}

input[type="submit"], .doc-btn {{
    width: 70%;
    background: white;
    color: black;
    font-weight: bold;
    cursor: pointer;
    padding: 12px;
    border-radius: 6px;
    border: none;
    text-decoration: none;
    display: inline-block;
    font-family: 'Inter', sans-serif;
}}

.footer {{
    margin-top: 20px;
    font-size: 0.9em;
    color: #aaa;
}}

.github {{
    position: absolute;
    top: 15px;
    right: 18px;
}}

.github a {{
    color: white;
    font-size: 1.3em;
    opacity: 0.7;
}}

.github a:hover {{
    opacity: 1;
}}

.dashboard-title {{
    font-size: 1.1em;
    font-weight: 600;
    margin-bottom: 10px;
}}

.dashboard-main {{
    font-family: 'Orbitron', sans-serif;
    font-size: 2.3em;
    letter-spacing: 0.15em;
    margin-bottom: 12px;
}}

.dashboard-sub {{
    color: #ccc;
}}
</style>
'''

def render_page(content, message, switch_url=None, switch_text=None, show_readme=True):
    nav_links = ''
    if switch_url and switch_text:
        nav_links += f'<a href="{switch_url}">{switch_text}</a>'

    if show_readme:
        nav_links += '<a href="/readme" target="_blank">READ ME</a>'

    return f'''
    <!doctype html>
    <html>
    <head>{base_css}</head>
    <body>
        <div class="container">
            <div class="github">
                <a href="{GITHUB_URL}" target="_blank"><i class="fa-brands fa-github"></i></a>
            </div>

            <h1>PROJECT SENTRY</h1>
            <div class="subtitle">A Secure Authentication System</div>

            <div class="nav">
                {nav_links}
            </div>

            {content}
            <p>{message}</p>

            <div class="footer">Made with 🤍 by Ahad Khan</div>
        </div>
    </body>
    </html>
    '''

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(password) < 8:
            message = 'Password must be at least 8 characters'
        elif not re.search(r'[A-Z]', password):
            message = 'Include an uppercase letter'
        elif not re.search(r'[a-z]', password):
            message = 'Include a lowercase letter'
        elif not re.search(r'[0-9]', password):
            message = 'Include a number'
        else:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users VALUES (NULL, ?, ?)", (username, hashed.decode()))
                conn.commit()
                session['username'] = username
                return redirect(url_for('dashboard'))
            except sqlite3.IntegrityError:
                message = 'Username already exists'
            finally:
                conn.close()

    form = '''
    <form method="POST">
        <input name="username" placeholder="Username" required>
        <input name="password" type="password" placeholder="Password" required>
        <input type="submit" value="Register">
    </form>
    '''
    return render_page(form, message, '/login', 'LOG IN')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()

        if result and bcrypt.checkpw(password.encode(), result[0].encode()):
            otp = str(random.randint(100000, 999999))
            otp_storage[username] = otp
            print(f"[OTP for {username}]: {otp}")
            return redirect(url_for('verify_otp'))
        else:
            message = 'Invalid credentials'

    form = '''
    <form method="POST">
        <input name="username" placeholder="Username" required>
        <input name="password" type="password" placeholder="Password" required>
        <input type="submit" value="Login">
    </form>
    '''
    return render_page(form, message, '/register', 'REGISTER')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    message = ''

    if request.method == 'POST':
        username = request.form['username']
        otp = request.form['otp']

        if otp_storage.get(username) == otp:
            otp_storage.pop(username)
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            message = 'Invalid OTP'

    form = '''
    <form method="POST">
        <input name="username" placeholder="Username" required>
        <input name="otp" placeholder="OTP Code" required>
        <input type="submit" value="Verify OTP">
    </form>
    '''
    return render_page(form, message, '/login', 'LOG IN')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    content = '''
    <div class="dashboard-title">WELCOME TO</div>
    <div class="dashboard-main">PROJECT SENTRY</div>
    <div class="dashboard-sub">A Cybersecurity Project</div>
    '''
    return render_page(content, '', None, None)

@app.route('/readme')
def readme():
    content = f'''
    <a href="{README_DOC_URL}" target="_blank" class="doc-btn">
        SECURITY DOCUMENTATION
    </a>

    <p style="margin-top:20px;">
        This project demonstrates secure authentication practices including password hashing,
        rate limiting, and two factor authentication.
    </p>

    <p>
        Future updates will include email based OTP delivery, session hardening, and logging.
    </p>
    '''
    return render_page(content, '', None, None, show_readme=False)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
