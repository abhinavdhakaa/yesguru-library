from flask import Flask, request, jsonify, render_template
import psycopg2
from datetime import datetime
import razorpay

app = Flask(__name__)

# DB connection
def get_db_connection():
    return psycopg2.connect(
        host="dpg-d12gu1mmcj7s73fblae0-a.oregon-postgres.render.com",
        database="yesguru_db",
        user="yesguru_admin",
        password="t8PL0yKLPiRNlUVdNlgoPLPa23YTvhiu",
        port=5432
    )

# Razorpay credentials
RAZORPAY_KEY_ID = "rzp_test_KhHe2W8qafLz6Q"       # Your publishable key
RAZORPAY_KEY_SECRET = "TCdhjXche8HiPI6VTsSmzp7z"   # Your secret key
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Razorpay plan IDs (replace with your actual plan IDs)
PLAN_3_MONTHS = "plan_QejEDBpS7ao58Q"  # 3 months plan ID
PLAN_6_MONTHS = "plan_QejYivaGjJhgup"  # 6 months plan ID

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

@app.route('/create-subscription', methods=['POST'])
def create_subscription():
    try:
        data = request.json
        plan_duration = data.get('plan')  # "3" or "6"

        if plan_duration == "3":
            plan_id = PLAN_3_MONTHS
            total_count = 3
        elif plan_duration == "6":
            plan_id = PLAN_6_MONTHS
            total_count = 6
        else:
            return jsonify({"error": "Invalid plan selected"}), 400

        # Create Razorpay customer
        customer = razorpay_client.customer.create({
            "name": data['name'],
            "email": data['email'],
            "contact": data['phone']
        })

        # Create subscription
        subscription = razorpay_client.subscription.create({
            "plan_id": plan_id,
            "customer_notify": 1,
            "total_count": total_count,
            "customer_id": customer['id']
        })

        # Return subscription ID & Razorpay publishable key
        return jsonify({
            "id": subscription['id'],
            "razorpay_key": RAZORPAY_KEY_ID
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5500)
