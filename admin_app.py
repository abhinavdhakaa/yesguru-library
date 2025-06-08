from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__, template_folder='templates_admin', static_folder='static')
app.secret_key = 'your_secret_key'  # Change this in production


# your routes and logic here

if __name__ == "__main__":
    app.run()


# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Abc@123',
        database='yesguru_library'
    )

# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin_users WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials", "error")

    return render_template('admin_login.html')

# Admin dashboard with table
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")  # Ensure 'users' table exists with needed columns
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', users=users)

# Logout
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
