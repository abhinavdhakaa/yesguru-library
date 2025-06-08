from flask import Flask, request, jsonify, render_template
import psycopg2
from datetime import datetime
import razorpay

app = Flask(__name__)

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        host="dpg-d12gu1mmcj7s73fblae0-a.oregon-postgres.render.com",
        database="yesguru_db",
        user="yesguru_admin",
        password="t8PL0yKLPiRNlUVdNlgoPLPa23YTvhiu",
        port=5432
    )

# Razorpay API credentials
RAZORPAY_KEY_ID = "rzp_test_KhHe2W8qafLz6Q"
RAZORPAY_KEY_SECRET = "TCdhjXche8HiPI6VTsSmzp7z"
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Serve the main page
@app.route('/')
def home():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        current_time = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return render_template('index.html', db_time=current_time)
    except Exception as e:
        return f"Error: {str(e)}", 500

# Route to add user after payment (can be used with webhook or success redirect)
@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        data = request.json
        student_name = data.get('student_name')
        father_name = data.get('father_name')
        email = data.get('email')
        mobile_number = data.get('mobile_number')
        ip_address = request.remote_addr
        subscribed_on = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (student_name, father_name, email, mobile_number, ip_address, subscribed_on)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (student_name, father_name, email, mobile_number, ip_address, subscribed_on)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User added successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to list all users
@app.route('/users')
def list_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, student_name, father_name, email, mobile_number, ip_address, subscribed_on FROM users;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "student_name": row[1],
                "father_name": row[2],
                "email": row[3],
                "mobile_number": row[4],
                "ip_address": row[5],
                "subscribed_on": row[6].isoformat() if row[6] else None
            })
        return jsonify(users)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to create Razorpay order for subscription
@app.route('/create-subscription', methods=['POST'])
def create_subscription():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        seat = data.get('seat')
        plan = int(data.get('plan'))  # plan in months

        price_per_month = 100  # ₹100 per month
        total_amount = plan * price_per_month * 100  # in paise

        order = razorpay_client.order.create({
            'amount': total_amount,
            'currency': 'INR',
            'payment_capture': 1,
        })

        return jsonify({
            "id": order['id'],
            "razorpay_key": RAZORPAY_KEY_ID
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Success page after payment
@app.route('/success')
def success():
    return "Payment successful! Thank you for subscribing."

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5500)
