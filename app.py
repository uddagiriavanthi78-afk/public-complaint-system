from flask import Flask, render_template, request, session
import sqlite3
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "mysecretkey"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            complaint TEXT,
            category TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------- AI CATEGORY (ML STYLE SIMPLE) ----------------
def predict_category(text):
    text = text.lower()

    if "water" in text:
        return "Water Issue"
    elif "electricity" in text or "power" in text:
        return "Electricity Issue"
    elif "road" in text or "pothole" in text:
        return "Road Issue"
    elif "garbage" in text or "clean" in text:
        return "Sanitation Issue"
    else:
        return "General Issue"

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- SUBMIT ----------------
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    complaint = request.form['complaint']

    category = predict_category(complaint)

    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO complaints (name, complaint, category, status) VALUES (?, ?, ?, ?)",
        (name, complaint, category, "Pending")
    )

    conn.commit()
    conn.close()

    return f"Thanks {name}, your complaint is saved as {category} issue!"

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            session['admin'] = True
            return "Login successful! <br><a href='/admin'>Go to Admin</a>"
        else:
            return "Invalid login"

    return render_template('login.html')

# ---------------- ADMIN ----------------
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return "Unauthorized! <br><a href='/login'>Login</a>"

    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute("SELECT * FROM complaints")
    data = c.fetchall()
    conn.close()

    return render_template('admin.html', complaints=data)

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('admin'):
        return "Unauthorized!"

    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute("DELETE FROM complaints WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return "Deleted successfully! <br><a href='/admin'>Go back</a>"

# ---------------- RESOLVE ----------------
@app.route('/resolve/<int:id>')
def resolve(id):
    if not session.get('admin'):
        return "Unauthorized!"

    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute("UPDATE complaints SET status = 'Resolved' WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return "Marked as resolved <br><a href='/admin'>Go back</a>"

# ---------------- CHART ----------------
@app.route('/chart')
def chart():
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()

    c.execute("SELECT category, COUNT(*) FROM complaints GROUP BY category")
    data = c.fetchall()

    conn.close()

    categories = [i[0] for i in data]
    values = [i[1] for i in data]

    plt.figure()
    plt.bar(categories, values)
    plt.title("Complaint Categories")

    plt.savefig("static/chart.png")
    plt.close()

    return render_template("chart.html")

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return "Logged out <br><a href='/login'>Login again</a>"

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)