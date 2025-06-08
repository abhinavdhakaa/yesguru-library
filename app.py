from flask import Flask, request, render_template, jsonify
import psycopg2
import razorpay

app = Flask(__name__)

# -------------------- Database Config --------------------
def get_db_connection():
    return psycopg2.connect(
        host="dpg-d12gu1mmcj7s73fblae0-a.oregon-postgres.render.com",
        database="yesguru_db",
        user="yesguru_admin",
        password="t8PL0yKLPiRNlUVdNlgoPLPa23YTvhiu",
        port=5432
    )

# -------------------- Razorpay Setup --------------------
RAZORPAY_KEY_ID = "rzp_test_KhHe2W8qafLz6Q"
RAZORPAY_KEY_SECRET = "TCdhjXche8HiPI6VTsSmzp7z"
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# -------------------- Routes --------------------
@app.route('/')
def home():
    ip = request.remote_addr
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE ip_address = %s AND status = 'active'", (ip,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        message = f"👋 Welcome back, {user[0]}! Your subscription is active."
    else:
        message = "Welcome! Please subscribe to access the library."
    return render_template("home.html", message=message)

@app.route('/dbtime')
def dbtime():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT NOW();')
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return f"Database time is: {result[0]}"

@app.route('/add_user')
def add_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ('Abhinav', 'abhinav@example.com'))
    conn.commit()
    cursor.close()
    conn.close()
    return "User added successfully!"

@app.route('/create-subscription', methods=['POST'])
def create_subscription():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    seat = data.get("seat")
    plan = int(data.get("plan"))
    ip = request.remote_addr

    plan_id = {
        3: 'plan_Qdx1SqDRLXuoSs',
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

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, phone, seat, plan_months, subscription_id, status, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, email, phone, seat, plan, subscription_id, "created", ip))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"id": subscription_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/success')
def success():
    return "<h1>Thank you for subscribing!</h1>"

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

# -------------------- Main --------------------
if __name__ == '__main__':
    app.run(debug=True, port=5500)
