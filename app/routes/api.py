
from flask import Blueprint, request, jsonify
from flask import g
from app.services.user_service import (
    register_user, login_user, get_user_logs
)
from app.services.record_service import (
    upload_record, share_with_user, download_record
)
from app.services.document_services import (
    list_users,
    list_my_documents,
    list_documents_shared_with_me
)

from app.utils.auth import token_required

api = Blueprint("api", __name__)

@api.route("/register", methods=["POST"])
def register():
    data = request.json
    return register_user(data)

@api.route("/login", methods=["POST"])
def login():
    data = request.json
    return login_user(data)

@api.route("/upload", methods=["POST"])
@token_required
def upload():
    file = request.files.get("file")
    filename = request.form.get("filename")
    note = request.form.get("note", "")

    user = g.username 

    if not file or not filename:
        return jsonify({"error": "Missing file or filename"}), 400

    success, message = upload_record(user, file, filename, note)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 500


@api.route("/share", methods=["POST"])
@token_required
def share():
    return share_with_user()

@api.route("/download/<owner>", methods=["POST"])
@token_required
def download(owner):
    return download_record(owner)

@api.route("/logs", methods=["GET"])
@token_required
def logs():
    return get_user_logs()
@api.route("/users", methods=["GET"])
@token_required
def get_users():
    return list_users()

@api.route("/mydocs", methods=["GET"])
@token_required
def my_documents():
    return list_my_documents()

@api.route("/shared-with-me", methods=["GET"])
@token_required
def shared_with_me():
    return list_documents_shared_with_me()
