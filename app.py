from flask import Flask, request, jsonify, render_template
import razorpay
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Razorpay credentials
RAZORPAY_KEY_ID = "rzp_test_KhHe2W8qafLz6Q"
RAZORPAY_KEY_SECRET = "TCdhjXche8HiPI6VTsSmzp7z"

# Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# MySQL database connection
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Abc@123",             # ✅ your actual MySQL password as string
    database="yesguru_library"

)

cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html', razorpay_key_id=RAZORPAY_KEY_ID)

@app.route('/create-subscription', methods=['POST'])
def create_subscription():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    seat = data.get("seat")
    plan = int(data.get("plan"))

    # Create a Razorpay plan (once created, you can store and reuse its ID)
    plan_id = {
        3: 'plan_Qdx1SqDRLXuoSs',  # Replace with your actual Razorpay plan IDs
        6: 'plan_Qdx1SqDRLXuoSs'
    }.get(plan)

    if not plan_id:
        return jsonify({"error": "Invalid plan selected"}), 400

    subscription_data = {
        "plan_id": plan_id,
        "total_count": plan,
        "customer_notify": 1
    }

    try:
        subscription = razorpay_client.subscription.create(subscription_data)
        subscription_id = subscription['id']

        # Save in database
        cursor.execute("""
            INSERT INTO users (name, email, phone, seat, plan_months, subscription_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, phone, seat, plan, subscription_id, "created"))
        db.commit()

        return jsonify({"id": subscription_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/success')
def success():
    return "<h1>Thank you for subscribing!</h1>"

if __name__ == '__main__':
    app.run(port=5500)

@app.route('/')
def home():
    ip = get_client_ip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE ip_address = %s AND status = 'active'", (ip,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        message = f"👋 Welcome back, {user['name']}! Your subscription is active."
    else:
        message = "Welcome! Please subscribe to access the library."

    return render_template('home.html', message=message)

@app.route('/terms')
def terms():
    return render_template("terms.html")

@app.route('/privacy')
def privacy():
    return render_template("privacy.html")

@app.route('/refund')
def refund():
    return render_template("refund.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")
