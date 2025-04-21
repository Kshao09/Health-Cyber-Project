
from flask import request, jsonify, session
from app.utils.db import get_db, log_action
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from app.utils.auth import token_required

SECRET_KEY = "cybersecurity"

def register_user(data):
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                    (data["username"], generate_password_hash(data["password"])))
        db.commit()
        return jsonify({"message": "Registered"}), 200
    except:
        return jsonify({"error": "User exists"}), 400
    finally:
        db.close()

def login_user(data):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (data["username"],))
    user = cur.fetchone()
    if user and check_password_hash(user["password_hash"], data["password"]):
        log_action(user["id"], "login")
        
        token = jwt.encode({
            "user_id": user["id"],
            "username": user["username"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "message": "Login successful",
            "token": token
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401

@token_required
def get_user_logs():
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT id FROM users WHERE username = ?", (g.username,))
    row = cur.fetchone()
    if not row:
        return jsonify({"error": "User not found"}), 404

    user_id = row["id"]

    cur.execute("""
        SELECT action, target, timestamp
        FROM access_logs
        WHERE user_id = ? OR (action = 'download' AND target = ?)
        ORDER BY timestamp DESC
    """, (user_id, g.username))

    logs = [dict(row) for row in cur.fetchall()]
    db.close()
    return jsonify({"logs": logs}), 200
