# Health-Cyber-Project

Final Project for Cybersecurity

# Secure Document Sharing Platform

A lightweight web app that allows users to:

- Register and log in
- Upload encrypted documents (AES)
- Share documents with other users
- Download documents shared with them
- View activity history (logs)

---

# Requirements

- Python 3.7+
- pip (Python package installer)

---

# Installation

1. **Clone the repository:**

```bash
git clone https://github.com/Kshao09/Health-Cyber-Project.git
cd Health-Cyber-Project/app
```

2. **Install dependencies:**

```bash
pip install flask flask-cors pycryptodome
```

---

# Run the App

```bash
python app.py
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

# Project Structure

```
app/
├── app.py                  # Flask entry point
├── routes/
│   └── api.py              # API routes
├── services/
│   ├── user_service.py     # Registration, login, logs
│   └── record_service.py   # Upload, share, download
└── utils/
    ├── db.py               # SQLite database and logging
    └── crypto.py           # AES encryption utilities
records/                    # Folder to store encrypted documents
app.db                      # SQLite database (auto-created)
```

---

# API Endpoints

- `POST /register` – Register a new user
- `POST /login` – Log in a user
- `POST /upload` – Upload encrypted document
- `POST /share` – Share document with another user
- `POST /download/<owner>` – Download document from another user
- `GET /logs` – View user’s action logs

---

# Security

- Files are encrypted using **AES-256 CBC**
- Encryption keys are provided by users and never stored
- Passwords are hashed with SHA256 and salt (`werkzeug.security`)

---
