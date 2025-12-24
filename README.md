# 🔐 Securo — Secure Password Manager (FastAPI)

[![Python](https://img.shields.io/badge/Python-3.12-%230377e6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-00FFAB?style=for-the-badge&logo=fastapi&logoColor=black)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-%23FF00FF?style=for-the-badge)](https://github.com/ApurveKaranwal/Securo/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/badge/Stars-🔥%20%20%20%20%20-blue?style=for-the-badge)](https://github.com/ApurveKaranwal/Securo/stargazers)
[![GitHub Issues](https://img.shields.io/badge/Issues-🛠%20%20%20%20%20-red?style=for-the-badge)](https://github.com/ApurveKaranwal/Securo/issues)
[![GitHub Last Commit](https://img.shields.io/badge/Last%20Commit-💾%20%20%20%20%20-green?style=for-the-badge)](https://github.com/ApurveKaranwal/Securo/commits/main)
[![Code Size](https://img.shields.io/badge/Code%20Size-🖥%20%20%20%20%20-yellow?style=for-the-badge)](https://github.com/ApurveKaranwal/Securo)


Securo is a **secure, backend-driven password manager** built using **FastAPI**, focused on **encryption, password safety, and real-world security features**.  
It demonstrates core backend security concepts such as encryption, hashing, password rotation, audit logging, and secure exports.

---

## 🚀 Features

- 🔑 **Master Password Protection**  
  Single master password secures all stored credentials.  
  Hashed using **SHA-256 + bcrypt (72-byte safe)**.

- 🔐 **Strong Encryption**  
  All passwords encrypted using **Fernet (symmetric encryption)**.  
  Encryption key is securely managed via `.env`.

- 🔄 **Password Rotation**  
  Instantly rotate stored passwords to reduce credential exposure.

- 🆘 **Emergency Password Generator**  
  Generate strong passwords instantly when needed.

- 📤 **Export Passwords**  
  Export all saved credentials in **JSON** format (useful for backups or migration).

- 🔍 **Search & List Entries**  
  Search saved passwords by service name or list all stored services with metadata.

- 📊 **Password Strength Scoring**  
  Scores passwords based on length and complexity.

- 🕵️ **Access Logging**  
  Tracks password access events for auditing and activity monitoring.

---

## 🛠 Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend** | FastAPI |
| **Database** | SQLite + SQLAlchemy ORM |
| **Security** | bcrypt (<4.0), SHA-256, Fernet Encryption |
| **Env Management** | python-dotenv |
| **API Docs** | Swagger UI (auto-generated) |

---

## 📂 Project Structure
```bash
backend/
│── main.py # FastAPI application
│── database.py # Database connection
│── models.py # SQLAlchemy models
│── .env # Environment variables (not committed)
│── requirements.txt
```

---

## ⚙️ Setup & Run Locally

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/securo.git
cd securo/backend
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate # Windows

source venv/bin/activate # Linux/Mac
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Create `.env` file

Create a `.env` file in the root directory and add your Fernet key:
```bash
FERNET_KEY=your_generated_fernet_key_here
```

To generate a key:
```bash
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### 5️⃣ Run the server

```bash
uvicorn main:app --reload
Server URL: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
```
---

## 🔌 API Endpoints Overview

### 🔐 Security
- `POST /set-master` → Set master password  

### 🔑 Password Management
- `POST /add` → Add new password  
- `GET /retrieve` → Retrieve password (master protected)  
- `PUT /rotate` → Rotate password  
- `DELETE /delete` → Delete password  

### 🧰 Utilities
- `GET /list` → List all services  
- `GET /search` → Search services  
- `GET /export` → Export passwords (JSON)  
- `GET /health` → Health check  

---

## 🔒 Security Notes

- Master password is **never stored in plain text**.  
- Passwords are **encrypted at rest** using Fernet.  
- bcrypt version is **pinned (<4.0)** for compatibility.  
- `.env` file is **excluded** from GitHub commits for safety.

---

## 📸 Demo & Screenshots

Feature walkthroughs and short demos are available on LinkedIn:
- Password creation  
- Secure generation  
- Master password flow  
- JSON export  
- Password rotation  
- Backend code snippets  

---

## 📌 Why This Project?

Securo was built to:
- Practice **real-world backend security** techniques.  
- Understand **hashing, encryption**, and secure password handling.  
- Build a **production-style FastAPI app**.  
- Showcase backend skills for **internships and developer roles**.

---

## 🤝 Contributions

Contributions, suggestions, and pull requests are welcome.  
Feel free to **fork**, improve, and build on top of this project.

---

## 👤 Author

**Apurve Karanwal**  
Backend Developer | FastAPI | Security Enthusiast  

[LinkedIn](https://www.linkedin.com/in/apurvekaranwal) • [GitHub](https://github.com/ApurveKaranwal)

---

### 🛡️ License

This project is distributed under the **MIT License** — feel free to use and modify with attribution.
