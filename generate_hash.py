from werkzeug.security import generate_password_hash

password = 'admin123'  # Replace with your desired admin password
hashed_password = generate_password_hash(password)

print(hashed_password)
