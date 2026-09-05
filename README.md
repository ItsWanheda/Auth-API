# 🔐 Auth API — Production Ready Authentication Service

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Modern%20API-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)
![JWT](https://img.shields.io/badge/Auth-JWT-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A secure, scalable, and production-ready **Authentication REST API** built with **FastAPI** following modern backend architecture principles.

The project provides a complete authentication system with JWT-based authentication, refresh token management, password security, email verification, password recovery, and a clean service-oriented architecture.

---

# 🚀 Overview

Modern applications require secure identity management. This project provides a complete authentication backend that can be integrated into:

* Web applications
* Mobile applications
* SaaS platforms
* Internal enterprise systems
* Microservice architectures

The API focuses on:

✅ Security
✅ Scalability
✅ Maintainability
✅ Clean architecture
✅ Developer experience

---

# ✨ Features

## Authentication

* User registration
* Secure login
* JWT Access Token authentication
* Refresh Token authentication
* Token rotation
* Token revocation
* Logout current session
* Logout all sessions
* Protected routes

---

## User Management

* User profile retrieval
* Profile update
* Password change
* Account management
* UUID-based user identities

---

## Security

* Argon2 password hashing
* JWT token signing
* Secure token expiration
* Password strength validation
* SQL injection protection
* Input validation
* CORS configuration
* Security headers
* Rate limiting
* Environment-based configuration

---

## Email System

* Email verification
* Verification tokens
* Password reset emails
* Secure recovery flow

---

## Developer Features

* Automatic Swagger documentation
* Async database support
* Repository pattern
* Service layer architecture
* Dependency injection
* Structured logging
* Custom exception handling
* Docker support
* Automated testing

---

# 🏗️ Architecture

The application follows a layered architecture:

```text
Router Layer
      |
      ↓
Service Layer
      |
      ↓
Repository Layer
      |
      ↓
Database Layer
```

### Router Layer

Handles:

* HTTP requests
* Request validation
* Response formatting

Location:

```
app/routers/
```

---

### Service Layer

Contains business logic:

* Authentication workflow
* User management
* Token generation
* Email handling

Location:

```
app/services/
```

---

### Repository Layer

Handles database operations:

* CRUD operations
* Queries
* Data persistence

Location:

```
app/repositories/
```

---

# 📂 Project Structure

```text
auth-api/
│
├── app/
│
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│
│   ├── core/
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   └── logging.py
│
│   ├── models/
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── refresh_token.py
│   │   ├── password_reset_token.py
│   │   └── email_verification_token.py
│
│   ├── schemas/
│   │   ├── common.py
│   │   ├── user.py
│   │   └── auth.py
│
│   ├── repositories/
│   │   ├── base.py
│   │   ├── user.py
│   │   └── token.py
│
│   ├── services/
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── token.py
│   │   └── email.py
│
│   ├── routers/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── health.py
│
│   ├── dependencies/
│   │   ├── auth.py
│   │   ├── database.py
│   │   └── services.py
│
│   ├── security/
│   │   ├── password.py
│   │   ├── jwt.py
│   │   └── tokens.py
│
│   ├── middleware/
│   │   ├── logging.py
│   │   ├── rate_limit.py
│   │   └── security_headers.py
│
│   ├── utils/
│   │   ├── validators.py
│   │   └── helpers.py
│
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_user.py
│   │   └── test_validators.py
│
│   └── main.py
│
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── alembic.ini
├── Makefile
└── README.md
```

---

# 🔐 Authentication Flow

```text
                Register
                   |
                   ↓
          Password Hash (Argon2)
                   |
                   ↓
             Store User
                   |
                   ↓
          Email Verification
                   |
                   ↓
                Login
                   |
                   ↓
       Generate JWT Access Token
       Generate Refresh Token
                   |
                   ↓
          Access Protected APIs
```

---

# 🔑 Token Strategy

## Access Token

Used for API authentication.

Example:

```
Authorization: Bearer <access_token>
```

Recommended lifetime:

```
15 minutes
```

---

## Refresh Token

Used to generate new access tokens.

Features:

* Database stored
* Revocable
* Rotated after usage
* Device/session based

Recommended lifetime:

```
30 days
```

---

# 📡 API Endpoints

## Authentication

| Method | Endpoint                | Description            |
| ------ | ----------------------- | ---------------------- |
| POST   | `/auth/register`        | Create account         |
| POST   | `/auth/login`           | Login                  |
| POST   | `/auth/refresh`         | Refresh token          |
| POST   | `/auth/logout`          | Logout session         |
| POST   | `/auth/logout-all`      | Logout all devices     |
| POST   | `/auth/verify-email`    | Verify email           |
| POST   | `/auth/forgot-password` | Request password reset |
| POST   | `/auth/reset-password`  | Reset password         |

---

## User

| Method | Endpoint          | Description     |
| ------ | ----------------- | --------------- |
| GET    | `/users/me`       | Current user    |
| PATCH  | `/users/me`       | Update profile  |
| PATCH  | `/users/password` | Change password |

---

## System

| Method | Endpoint  |
| ------ | --------- |
| GET    | `/health` |

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/ItsWanheda/auth-api.git

cd auth-api
```

---

# 🐍 Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

Linux:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

---

# 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔧 Environment Setup

Copy:

```bash
cp .env.example .env
```

Example:

```env
DATABASE_URL=postgresql://user:password@localhost/authdb

JWT_SECRET_KEY=your_secret_key

ACCESS_TOKEN_EXPIRE_MINUTES=15

REFRESH_TOKEN_EXPIRE_DAYS=30

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
```

---

# 🗄️ Database Migration

Run:

```bash
alembic upgrade head
```

Create migration:

```bash
alembic revision --autogenerate -m "migration_name"
```

---

# ▶️ Running Development Server

```bash
uvicorn app.main:app --reload
```

Server:

```
http://localhost:8000
```

---

# 📚 API Documentation

Swagger:

```
http://localhost:8000/docs
```

ReDoc:

```
http://localhost:8000/redoc
```

---

# 🐳 Docker Deployment

Build:

```bash
docker compose build
```

Run:

```bash
docker compose up
```

Production:

```bash
docker compose up -d
```

---

# 🧪 Testing

Run tests:

```bash
pytest
```

Coverage:

```bash
pytest --cov=app
```

---

# 🛠️ Development Commands

Using Makefile:

```bash
make install
```

```bash
make test
```

```bash
make format
```

```bash
make lint
```

---

# 📈 Future Roadmap

## Authentication

* OAuth2 login
* Google authentication
* GitHub authentication
* Discord authentication
* Two-factor authentication
* WebAuthn / Passkeys

## Security

* Device management
* Login history
* Suspicious login detection
* Advanced rate limiting
* Audit logs

## Platform

* Admin dashboard
* User roles
* Permissions system
* API keys
* Microservice support

---

# 🤝 Contribution

Contributions are welcome.

Steps:

1. Fork repository
2. Create feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit changes

```bash
git commit -m "Add new feature"
```

4. Push changes

```bash
git push origin feature/new-feature
```

5. Open Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# ⭐ Author

Built with ❤️ by ItsWanheda using:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Modern Backend Architecture

---

If this project helped you, consider giving it a ⭐ on GitHub.
