from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="devi"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def teams():
    return render_template('teams.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin')  # login page
def admin_login():
    return render_template('login.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == 'admin123' and password == '1234':
            session['admin'] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for("admin_login"))
    
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student_registrations")
        students = cursor.fetchall()
        cursor.close()
        
        # Ensure the students list has the correct keys matching the template
        for student in students:
            student.setdefault('id', student.get('id', 'N/A'))
            student.setdefault('name', student.get('name', 'Unknown'))
            student.setdefault('gender', student.get('gender', 'N/A'))
            student.setdefault('sport', student.get('sport', 'N/A'))
            student.setdefault('department', student.get('department', 'N/A'))
            student.setdefault('contact', student.get('contact', 'N/A'))
        
        return render_template("admin.html", students=students)
    except Exception as e:
        return f"<h2>Error fetching data: {e}</h2>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = (
            request.form.get('name'),
            request.form.get('student_id'),
            request.form.get('gender'),
            request.form.get('sport'),
            request.form.get('department', ''),
            request.form.get('contact', '')
        )
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO student_registrations 
                    (name, student_id, gender, sport, department, contact)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, data)
                db.commit()
        except Exception as e:
            return f"<h2>Error: {e}</h2>"
        return redirect(url_for('success', type='registration'))
    return render_template('register.html')

@app.route('/Addplayer', methods=['GET', 'POST'])
def addplayer():
    if request.method == 'POST':
        data = (
            request.form.get('name'),
            request.form.get('role'),
            request.form.get('matches'),
            request.form.get('goals'),
            request.form.get('assists'),
            request.form.get('energy')
        )
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO players
                    (name, role, matches, goals, assists, energy)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, data)
                db.commit()
            return redirect(url_for('addplayer'))
        except Exception as e:
            return f"<h2>Error: {e}</h2>"
    return render_template('Addplayer.html')
    
 @app.route('/Performance')
def Performance():
    return render_template('Performance.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = (
            request.form.get('name'),
            request.form.get('email'),
            request.form.get('message')
        )
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO game
                    (name, email, message)
                    VALUES (%s, %s, %s)
                """, data)
                db.commit()
            return redirect(url_for('contact', message='Message sent successfully!'))
            return redirect(url_for('contact', message='Message sent successfully!'))
        except Exception as e:
            return render_template('contact.html', error=str(e))
    return render_template('contact.html')

@app.route('/success')
def success():
    submission_type = request.args.get('type', 'generic')
    if submission_type == 'student_registration':
        return "<h2>Registration successful!</h2>"
    elif submission_type == 'contact':
        return "<h2>Message sent successfully!</h2>"
    return "<h2>Submission successful!</h2>"

@app.route('/edit/<student_id>')
def edit(student_id):
    return f"Edit Student ID: {student_id}"

@app.route('/delete/<student_id>')
def delete(student_id):
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM  student_registrations WHERE id = %s", (student_id,))
            db.commit()
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        return f"<h2>Error deleting record: {e}</h2>"
if __name__ == '__main__':
    app.run(debug=True)