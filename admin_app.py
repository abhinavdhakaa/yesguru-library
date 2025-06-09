from flask import Flask, render_template, request, redirect, session
import os
import psycopg2

admin_app = Flask(__name__, template_folder='templates_admin', static_folder='static')
admin_app.secret_key = 'your_secret_key'

def get_db_connection():
    return psycopg2.connect(
        host="dpg-d12gu1mmcj7s73fblae0-a.oregon-postgres.render.com",
        database="yesguru_db",
        user="yesguru_admin",
        password="t8PL0yKLPiRNlUVdNlgoPLPa23YTvhiu",
        port=5432
    )

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

@admin_app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        return render_template('admin_login.html', error="Invalid credentials.")
    return render_template('admin_login.html')

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

@admin_app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

# Only one run block!
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5501))
    admin_app.run(debug=False, host='0.0.0.0', port=port)
