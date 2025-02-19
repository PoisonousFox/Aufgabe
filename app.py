from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Datenbank initialisieren
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'username' in session:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT sender, message, timestamp FROM messages ORDER BY id DESC')
        messages = cursor.fetchall()
        conn.close()
        return render_template('chat.html', username=session["username"], messages=messages)
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        session['username'] = username
        return redirect(url_for('home'))
    return 'Falsche Anmeldedaten! <a href="/">Zurück</a>'

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return 'Registrierung erfolgreich! <a href="/">Anmelden</a>'
    except sqlite3.IntegrityError:
        return 'Benutzername existiert bereits! <a href="/">Zurück</a>'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' in session:
        message = request.form['message']
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)', (session['username'], message, timestamp))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

# HTML Datei (templates/index.html)
# Erstelle eine Datei "templates/index.html" mit folgendem Inhalt:
'''
<!DOCTYPE html>
<html>
<head>
    <title>Login Seite</title>
</head>
<body>
    <h2>Login</h2>
    <form action="/login" method="post">
        <input type="text" name="username" placeholder="Benutzername" required>
        <input type="password" name="password" placeholder="Passwort" required>
        <button type="submit">Anmelden</button>
    </form>
    <h2>Registrierung</h2>
    <form action="/register" method="post">
        <input type="text" name="username" placeholder="Benutzername" required>
        <input type="password" name="password" placeholder="Passwort" required>
        <button type="submit">Registrieren</button>
    </form>
</body>
</html>
'''

# HTML Datei (templates/chat.html)
# Erstelle eine Datei "templates/chat.html" mit folgendem Inhalt:
'''
<!DOCTYPE html>
<html>
<head>
    <title>Chat</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h2>Willkommen {{ username }}</h2>
    <div class="chat-box">
        {% for sender, message, timestamp in messages %}
            <p><strong>{{ sender }}</strong> [{{ timestamp }}]: {{ message }}</p>
        {% endfor %}
    </div>
    <form action="/send_message" method="post">
        <input type="text" name="message" placeholder="Nachricht" required>
        <button type="submit">Senden</button>
    </form>
    <a href="/logout">Logout</a>
</body>
</html>
'''

# CSS Datei (static/style.css)
# Erstelle eine Datei "static/style.css" mit folgendem Inhalt:
'''
body {
    font-family: Arial, sans-serif;
    text-align: center;
}
.chat-box {
    width: 50%;
    margin: auto;
    border: 1px solid #ccc;
    padding: 10px;
    background: #f9f9f9;
}
form {
    margin-top: 20px;
}
'''
