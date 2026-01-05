from flask import Flask, request, redirect, session
import sqlite3, os
from datetime import datetime
import csv
from flask import Response

print("=== FRESH APP (NO ERROR VERSION) ===")

app = Flask(__name__)
app.secret_key = "pavanraje_agro_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "pavanraje.db")

os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)

def init_db():
 def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        date TEXT,
        start_time TEXT,
        end_time TEXT,
        start_photo TEXT,
        end_photo TEXT,
        latitude TEXT,
        longitude TEXT,
        work_desc TEXT
    )
    """)

    c.execute("SELECT id FROM employees WHERE username='employee1'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO employees (username,password) VALUES (?,?)",
            ("employee1","1234")
        )
    # -------- ADMIN UPDATES TABLE --------
    c.execute("""
    CREATE TABLE IF NOT EXISTS updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        message TEXT,
        photo TEXT,
        target TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Pavanraje Agro – Quality Seeds</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body{
            font-family: Arial, sans-serif;
            margin:0;
            background:#f5fff5;
            text-align:center;
        }
        header{
            background:#2e7d32;
            color:white;
            padding:25px;
        }
        .container{
            padding:30px;
        }
        .highlight{
            background:#e8f5e9;
            padding:20px;
            border-radius:10px;
            margin:20px auto;
            max-width:500px;
        }
        .btn{
            display:block;
            width:85%;
            max-width:320px;
            margin:15px auto;
            padding:15px;
            background:#2e7d32;
            color:white;
            text-decoration:none;
            font-size:18px;
            border-radius:8px;
        }
        footer{
            margin-top:40px;
            padding:15px;
            background:#e8f5e9;
            font-size:14px;
        }
    </style>
</head>
<body>

<header>
    <h2>🌱 Pavanraje Agro Producer Company Ltd.</h2>
    <p>Quality Seed Production & Supply</p>
</header>

<div class="container">

    <h3>शेतकऱ्यांच्या विश्वासाचं दर्जेदार बियाणे</h3>

    <div class="highlight">
        🌾 <b>आमची बियाणे:</b><br>
        सोयाबीन | तूर | हरभरा | कापूस | ज्वारी | बाजरी<br><br>

        🌱 <b>उच्च उगवण क्षमता</b><br>
        🧪 <b>प्रक्रिया व चाचणी केलेले बियाणे</b><br>
        👨‍🌾 <b>शेतकरी-केंद्रित उत्पादन</b>
    </div>

    <a class="btn" href="/employee_login">👨‍🌾 Employee Login</a>
    <a class="btn" href="/admin_login">👨‍💼 Admin Login</a>
    <a class="btn" href="/retailer_login">🧾 Retailer Login</a>

</div>

<footer>
    📍 Govardhanwadi, Dharashiv<br>
    📞 9900857777<br>
    🌐 www.pavanrajeagro.com
</footer>

</body>
</html>
"""


@app.route("/employee_login", methods=["GET","POST"])
def employee_login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM employees WHERE username=? AND password=?", (u,p))
        emp = c.fetchone()
        conn.close()
        if emp:
            session["employee_id"] = emp[0]
            return redirect("/attendance_start")
    return """
    <h3>Employee Login</h3>
    <form method='post'>
    <input name='username'><br>
    <input type='password' name='password'><br>
    <button>Login</button>
    </form>
    """

@app.route("/attendance_start", methods=["GET","POST"])
def attendance_start():
    if "employee_id" not in session:
        return redirect("/employee_login")

    if request.method == "POST":
        photo = request.files["photo"]
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        fname = f"{session['employee_id']}_start_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        photo.save(os.path.join(UPLOAD_FOLDER, fname))

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO attendance
            (employee_id,date,start_time,start_photo,latitude,longitude)
            VALUES (?,?,?,?,?,?)
        """, (
            session["employee_id"],
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%H:%M:%S"),
            fname, lat, lon
        ))
        conn.commit()
        conn.close()

        return redirect("/attendance_end")

    return """
    <h3>Day Start</h3>
    <form method='post' enctype='multipart/form-data'>
        <input type='hidden' name='lat' id='lat'>
        <input type='hidden' name='lon' id='lon'>
        Photo: <input type='file' name='photo' required><br><br>
        <button>Start Day</button>
    </form>
    <script>
    navigator.geolocation.getCurrentPosition(p=>{
        document.getElementById('lat').value=p.coords.latitude;
        document.getElementById('lon').value=p.coords.longitude;
    });
    </script>
    """

@app.route("/attendance_end", methods=["GET","POST"])
def attendance_end():
    if "employee_id" not in session:
        return redirect("/employee_login")

    if request.method == "POST":
        work = request.form["work"]
        photo = request.files["photo"]

        fname = f"{session['employee_id']}_end_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        photo.save(os.path.join(UPLOAD_FOLDER, fname))

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            UPDATE attendance
            SET end_time=?, end_photo=?, work_desc=?
            WHERE employee_id=? AND date=? AND end_time IS NULL
        """, (
            datetime.now().strftime("%H:%M:%S"),
            fname,
            work,
            session["employee_id"],
            datetime.now().strftime("%Y-%m-%d")
        ))
        conn.commit()
        conn.close()

        return "Attendance Completed ✅"

    return """
    <h3>Day End</h3>
    <form method='post' enctype='multipart/form-data'>
        End Photo: <input type='file' name='photo' required><br>
        Work:<br><textarea name='work'></textarea><br>
        <button>End Day</button>
    </form>
    """


@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"]=="admin" and request.form["password"]=="admin123":
            session["admin"] = True
            return redirect("/admin_dashboard")
    return "<form method='post'><input name='username'><input type='password' name='password'><button>Login</button></form>"

@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT e.username, a.date, a.start_time, a.end_time, a.work_desc
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
    """)
    rows = c.fetchall()
    conn.close()

    out = "<h3>Admin Dashboard</h3>"
    out += "<a href='/admin_attendance_csv'>⬇️ Download CSV</a><br><br>"
    out += "<table border=1>"
    out += "<tr><th>Employee</th><th>Date</th><th>Start</th><th>End</th><th>Work</th></tr>"

    for r in rows:
        out += (
            f"<tr>"
            f"<td>{r[0]}</td>"
            f"<td>{r[1]}</td>"
            f"<td>{r[2]}</td>"
            f"<td>{r[3]}</td>"
            f"<td>{r[4]}</td>"
            f"</tr>"
        )

    out += "</table>"
    return out
@app.route("/admin_updates", methods=["GET","POST"])
def admin_updates():
    if "admin" not in session:
        return redirect("/admin_login")

    if request.method == "POST":
        title = request.form["title"]
        message = request.form["message"]
        target = request.form["target"]
        photo_file = request.files["photo"]

        filename = ""
        if photo_file and photo_file.filename != "":
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + photo_file.filename
            save_path = os.path.join("uploads", "updates_photos", filename)
            photo_file.save(save_path)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO updates (title, message, photo, target, date)
            VALUES (?,?,?,?,?)
        """, (
            title, message, filename, target,
            datetime.now().strftime("%Y-%m-%d")
        ))
        conn.commit()
        conn.close()

        return "Update Saved Successfully ✅<br><a href='/admin_updates'>Add Another</a>"

    return """
    <h3>📢 Add New Update</h3>
    <form method='post' enctype='multipart/form-data'>
        Title:<br>
        <input name='title' required><br><br>

        Message:<br>
        <textarea name='message' required></textarea><br><br>

        Target:<br>
        <select name='target'>
            <option value='farmer'>👨‍🌾 Farmer</option>
            <option value='retailer'>🧾 Retailer</option>
            <option value='both'>👥 Both</option>
        </select><br><br>

        Photo (optional):<br>
        <input type='file' name='photo'><br><br>

        <button>Save Update</button>
    </form>
    <br>
    <a href="/admin_dashboard">⬅ Back to Dashboard</a>
    """

@app.route("/admin_attendance_csv")
def admin_attendance_csv():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT e.username, a.date, a.start_time, a.end_time,
               a.work_desc, a.latitude, a.longitude
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        ORDER BY a.date DESC
    """)
    rows = c.fetchall()
    conn.close()

    def generate():
        data = csv.writer([])
        yield "Employee,Date,Start,End,Work,Latitude,Longitude\n"
        for r in rows:
            yield ",".join([str(x or "") for x in r]) + "\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=attendance.csv"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


