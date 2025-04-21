from flask import session, jsonify
from app.utils.db import get_db
from app.utils.auth import token_required
from flask import g

def list_users():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT username FROM users WHERE username != ?", (g.username,))
    users = [row["username"] for row in cur.fetchall()]
    db.close()
    return jsonify({"users": users}), 200

def list_my_documents():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT r.id, r.file_path, r.original_filename, r.note, r.created_at
        FROM records r
        JOIN users u ON r.user_id = u.id
        WHERE u.username = ?
    """, (g.username,))
    docs = [dict(row) for row in cur.fetchall()]
    db.close()
    return jsonify({"documents": docs}), 200

def list_documents_shared_with_me():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT id FROM users WHERE username = ?", (g.username,))
    my_id = cur.fetchone()["id"]

    cur.execute("""
        SELECT DISTINCT u.username AS owner, r.file_path, r.original_filename, r.note, r.created_at
        FROM shares s
        JOIN records r ON s.record_id = r.id
        JOIN users u ON r.user_id = u.id
        WHERE s.shared_with_id = ?
    """, (my_id,))
    shared_docs = [dict(row) for row in cur.fetchall()]
    db.close()
    return jsonify({"documents": shared_docs}), 200
