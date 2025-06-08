from flask import Flask, render_template, request, redirect, session
import psycopg2
from datetime import datetime
import os

admin_app = Flask(__name__, template_folder='templates_admin')
admin_app.secret_key = 'your_secret_key'  # Change to secure random key

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5500))  # Use PORT env var if available
    app.run(debug=False, host='0.0.0.0', port=port)

    
# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="dpg-d12gu1mmcj7s73fblae0-a.oregon-postgres.render.com",
        database="yesguru_db",
        user="yesguru_admin",
        password="t8PL0yKLPiRNlUVdNlgoPLPa23YTvhiu",
        port=5432
    )

# Admin credentials (store securely in production)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

# Admin login
@admin_app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        else:
            return render_template('admin_login.html', error="Invalid credentials.")
    return render_template('admin_login.html')

# Admin dashboard
@admin_app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, student_name, father_name, email, mobile_number, ip_address, subscribed_on FROM users ORDER BY subscribed_on DESC;")
        users = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        return f"Database error: {e}", 500

    return render_template('admin_dashboard.html', users=users)

# Admin logout
@admin_app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    admin_app.run(debug=True, port=5501)
