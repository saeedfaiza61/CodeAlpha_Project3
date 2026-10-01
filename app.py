import os
import sqlite3
import hashlib
import pickle
from flask import Flask, request, render_template_string, redirect, session

app = Flask(__name__)
app.secret_key = "supersecret123"      

DB_PATH = "users.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, "
        "username TEXT, password TEXT, is_admin INTEGER DEFAULT 0)"
    )
    conn.execute(
        "INSERT OR IGNORE INTO users (id, username, password, is_admin) "
        "VALUES (1, 'admin', ?, 1)",
        (hashlib.md5("admin123".encode()).hexdigest(),)  
    )
    conn.commit()
    conn.close()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        pw_hash = hashlib.md5(password.encode()).hexdigest()

        
        query = "SELECT id, is_admin FROM users WHERE username = '%s' AND password = '%s'" % (
            username, pw_hash
        )
        conn = get_db()
        cur = conn.execute(query)
        row = cur.fetchone()
        conn.close()

        if row:
            session["user_id"] = row[0]
            session["is_admin"] = bool(row[1])
            return redirect("/welcome")
        return "Invalid credentials", 401

    return '''
        <form method="post">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit">
        </form>
    '''


@app.route("/welcome")
def welcome():
    name = request.args.get("name", "Guest")
    
    template = "<h1>Welcome, " + name + "!</h1>"
    return render_template_string(template)


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    
    result = os.popen("ping -c 1 " + host).read()
    return f"<pre>{result}</pre>"


@app.route("/file")
def read_file():
    filename = request.args.get("name", "readme.txt")
   
    path = os.path.join("uploads", filename)
    with open(path, "r") as f:
        return f.read()


@app.route("/load_session", methods=["POST"])
def load_session():
  
    data = pickle.loads(request.data)
    return {"status": "ok", "data": str(data)}


@app.route("/admin")
def admin_panel():
   
    if session.get("is_admin"):
        return "Welcome to the admin panel."
    return "Forbidden", 403


if __name__ == "__main__":
    init_db()
    
    app.run(debug=True, host="0.0.0.0")
