
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pyodbc
import hashlib
import re

app = Flask(__name__)
app.secret_key = 'nexus-secret-key-2024'


CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

def get_conn():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=ANIKO;"                 
        "DATABASE=AutomationDB;"          
        "Trusted_Connection=yes;"
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    return "Nexus API is running perfectly!"

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "მონაცემები არ არის გამოგზავნილი."}), 400

        username = data.get('username', '').strip()
        email    = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not username or not email or not password:
            return jsonify({"success": False, "message": "გთხოვთ შეავსოთ ყველა ველი."}), 400

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({"success": False, "message": "ელ-ფოსტის ფორმატი არასწორია (მაგ: user@example.com)."}), 400

        if len(password) < 6:
            return jsonify({"success": False, "message": "პაროლი უნდა შედგებოდეს მინიმუმ 6 სიმბოლოსგან."}), 400

        conn   = get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM Users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "ეს ელ-ფოსტა უკვე რეგისტრირებულია."}), 409

        hashed = hash_password(password)
        cursor.execute(
            "INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed)
        )
        conn.commit()

        cursor.execute("SELECT id, username, email FROM Users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id']  = user[0]
            session['username'] = user[1]
            session['email']    = user[2]

            return jsonify({
                "success": True,
                "message": "რეგისტრაცია წარმატებით დასრულდა!",
                "user": {"id": user[0], "username": user[1], "email": user[2]}
            })
        
        return jsonify({"success": False, "message": "მომხმარებლის შექმნის შეცდომა."}), 500

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"success": False, "message": f"სერვერის შეცდომა: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data     = request.json
        email    = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({"success": False, "message": "შეიყვანეთ ელ-ფოსტა და პაროლი."}), 400

        hashed = hash_password(password)
        conn   = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, username, email FROM Users WHERE email = ? AND password = ?",
            (email, hashed)
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"success": False, "message": "ელ-ფოსტა ან პაროლი არასწორია."}), 401

        session['user_id']  = user[0]
        session['username'] = user[1]
        session['email']    = user[2]

        return jsonify({
            "success": True,
            "message": "ავტორიზაცია წარმატებულია!",
            "user": {"id": user[0], "username": user[1], "email": user[2]}
        })

    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"success": False, "message": f"სერვერის შეცდომა: {str(e)}"}), 500


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "სესია დაიხურა."})

@app.route('/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "ავტორიზაცია არ არის გავლილი."}), 401
    return jsonify({
        "success": True,
        "user": {
            "id":       session['user_id'],
            "username": session['username'],
            "email":    session['email']
        }
    })

@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn   = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM Users ORDER BY id DESC")
        rows   = cursor.fetchall()
        conn.close()
        
        users  = [{"id": r[0], "username": r[1], "email": r[2]} for r in rows]
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)