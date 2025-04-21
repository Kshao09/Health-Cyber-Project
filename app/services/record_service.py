
from flask import request, jsonify, session
from app.utils.db import get_db, log_action
from app.utils.crypto import encrypt_data, decrypt_data
import json, os
from datetime import datetime
from werkzeug.utils import secure_filename
import base64
from flask import g

RECORDS_DIR = "records/"
os.makedirs(RECORDS_DIR, exist_ok=True)

def upload_record(user, file, original_filename, note):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (user,))
    user_id = cur.fetchone()["id"]

    os.makedirs(RECORDS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{secure_filename(user)}_{timestamp}.enc"
    path = os.path.join(RECORDS_DIR, filename)

    encrypted = file.read()  # already encrypted by client
    with open(path, "wb") as f:
        f.write(encrypted)

    cur.execute("INSERT INTO records (user_id, file_path, original_filename, note) VALUES (?, ?, ?, ?)", (user_id, path, original_filename, note))
    db.commit()
    log_action(user_id, "upload", filename)
    return True, "Record saved"

def share_with_user():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    record_path = data.get("record_path")
    target_user = data.get("target")

    db = get_db()
    cur = db.cursor()

    # Obtener IDs necesarios
    cur.execute("SELECT id FROM users WHERE username = ?", (g.username,))
    owner_id = cur.fetchone()["id"]

    cur.execute("SELECT id FROM users WHERE username = ?", (target_user,))
    target = cur.fetchone()
    if not target:
        return jsonify({"error": "Target user not found"}), 404
    target_id = target["id"]

    # Obtener ID del documento
    cur.execute("""
        SELECT id FROM records WHERE user_id = ? AND file_path = ?
    """, (owner_id, record_path))
    record = cur.fetchone()
    if not record:
        return jsonify({"error": "Document not found"}), 404
    record_id = record["id"]

    # Verificar si ya fue compartido
    cur.execute("""
        SELECT 1 FROM shares
        WHERE owner_id = ? AND shared_with_id = ? AND record_id = ?
    """, (owner_id, target_id, record_id))
    if cur.fetchone():
        return jsonify({"message": "Already shared"}), 200

    # Insertar nuevo permiso de compartición
    cur.execute("""
        INSERT INTO shares (owner_id, shared_with_id, record_id)
        VALUES (?, ?, ?)
    """, (owner_id, target_id, record_id))
    db.commit()
    db.close()
    log_action(owner_id, "share", target_user)
    db
    return jsonify({"message": "Shared successfully"}), 200

def download_record(owner):
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT id FROM users WHERE username = ?", (owner,))
    owner_id_row = cur.fetchone()
    if not owner_id_row:
        return jsonify({"error": "Owner not found"}), 404

    cur.execute(
        """SELECT file_path, original_filename FROM records
           WHERE user_id = ?
           ORDER BY id DESC LIMIT 1""",
        (owner_id_row["id"],)
    )
    row = cur.fetchone()
    if not row:
        return jsonify({"error": "No record found"}), 404

    with open(row["file_path"], "rb") as f:
        encrypted_bytes = f.read()
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode("utf-8")
    db.close()
    return jsonify({
        "record": encrypted_b64,
        "original_filename": row["original_filename"]
    }), 200