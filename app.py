from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('lab.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, secret_data TEXT)')
    c.execute('DELETE FROM users')
    c.execute("INSERT INTO users VALUES (1, 'admin', 'SuperSecretPass123', 'Flag: IDOR_Access_Granted_Admin')")
    c.execute("INSERT INTO users VALUES (2, 'user2', 'Password123', 'Flag: IDOR_Access_Granted_User2')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return '<h2>Cybersecurity Challenge Lab</h2><ul><li><a href="/level1">المستوى الأول</a></li><li><a href="/level2">المستوى الثاني</a></li><li><a href="/level3?user_id=2">المستوى الثالث</a></li></ul>'

@app.route('/level1')
def level1():
    name = request.args.get('name', '')
    hint = "<p><i>تلميح: لاحظ إذا كانت المدخلات تظهر على الصفحة مباشرة دون تنقيح.</i></p>"
    return f"<h3>المستوى الأول - XSS</h3>{hint}<form method='GET'><input type='text' name='name'><button type='submit'>إرسال</button></form><h4>مرحباً: {name}</h4>"

@app.route('/level2', methods=['GET', 'POST'])
def level2():
    hint = "<p><i>تلميح: افحص الاستعلامات.</i></p>"
    message = ""
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('lab.db')
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{user}' AND password = '{password}'"
        try:
            c.execute(query)
            if c.fetchone():
                message = "<h4 style='color:green;'>تم تسجيل الدخول!</h4>"
            else:
                message = "<h4 style='color:red;'>خطأ في الدخول.</h4>"
        except Exception as e:
            message = f"خطأ: {e}"
    return f"<h3>المستوى الثاني - SQL Injection</h3>{hint}<form method='POST'><input type='text' name='username'><br><input type='password' name='password'><br><button type='submit'>دخول</button></form>{message}"

@app.route('/level3')
def level3():
    hint = "<p><i>تلميح: غيّر المعرّف في الرابط.</i></p>"
    user_id = request.args.get('user_id', '2')
    conn = sqlite3.connect('lab.db')
    c = conn.cursor()
    c.execute("SELECT id, username, secret_data FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    content = f"ID: {user[0]}<br>Name: {user[1]}<br>Secret: {user[2]}" if user else "المستخدم غير موجود."
    return f"<h3>المستوى الثالث - IDOR</h3>{hint}{content}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)