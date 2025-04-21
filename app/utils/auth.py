
from functools import wraps
from flask import request, jsonify, g
import jwt
from app.utils.db import get_db

SECRET_KEY = "cybersecurity"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print("Authorization Header:", request.headers.get("Authorization"))
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            g.user_id = decoded["user_id"]
            g.username = decoded["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated

def get_current_user():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (g.user_id,))
    user = cur.fetchone()
    db.close()
    return dict(user) if user else None