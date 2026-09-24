# 🔐 Auth API

### Production-ready authentication service built with FastAPI, PostgreSQL, and JWT

![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Modern_API-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge\&logo=jsonwebtokens\&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?style=for-the-badge\&logo=docker\&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-F5C518?style=for-the-badge)

> A secure, scalable authentication REST API designed with modern backend engineering and security practices.

**Auth API** provides a complete identity and authentication backend for modern applications, including JWT authentication, refresh-token rotation, password security, email verification, password recovery, session management, and a clean layered architecture.

---

## ✨ Highlights

* 🔐 JWT-based authentication
* 🔄 Refresh-token rotation and revocation
* 🛡️ Argon2 password hashing
* 📧 Email verification and password recovery
* 👤 User and session management
* 🧱 Layered service-oriented architecture
* ⚡ Fully asynchronous database operations
* 🗄️ PostgreSQL + SQLAlchemy
* 🧪 Automated testing
* 🐳 Docker-ready deployment
* 📚 Automatic OpenAPI / Swagger documentation
* 🚦 Rate limiting and security middleware
* ⚙️ Environment-based configuration

---

## 🚀 Why Auth API?

Authentication is one of the most security-sensitive parts of an application.

Instead of embedding authentication logic directly inside route handlers, Auth API separates responsibilities into dedicated layers:

```text
                    ┌──────────────────────┐
                    │      HTTP Client     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Router Layer     │
                    │  HTTP / Validation   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Service Layer    │
                    │    Business Logic    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Repository Layer   │
                    │   Data Operations    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    PostgreSQL DB     │
                    └──────────────────────┘
```

This makes the system easier to:

* Test
* Maintain
* Extend
* Secure
* Scale
* Integrate into other applications

---

# ✨ Features

## 🔐 Authentication

| Feature                | Status |
| ---------------------- | :----: |
| User registration      |    ✅   |
| Secure login           |    ✅   |
| JWT access tokens      |    ✅   |
| Refresh tokens         |    ✅   |
| Refresh-token rotation |    ✅   |
| Token revocation       |    ✅   |
| Session logout         |    ✅   |
| Logout all sessions    |    ✅   |
| Protected routes       |    ✅   |

---

## 👤 User Management

* User profile retrieval
* Profile updates
* Password changes
* Account management
* UUID-based user identities
* Session-aware authentication

---

## 🛡️ Security

Security is a first-class concern throughout the application.

* **Argon2** password hashing
* JWT signing and validation
* Short-lived access tokens
* Refresh-token rotation
* Token revocation
* Password strength validation
* Request validation with Pydantic
* SQL injection protection through ORM/query parameterization
* CORS configuration
* Security headers
* Rate limiting
* Environment-based secrets
* Centralized exception handling

> ⚠️ Production deployments should additionally configure HTTPS, secure secret storage, trusted CORS origins, email infrastructure, monitoring, and appropriate reverse-proxy settings.

---

## 📧 Email & Account Recovery

The authentication system supports:

* Email verification
* Verification tokens
* Password reset requests
* Password reset tokens
* Secure account recovery workflows

---

## 🧑‍💻 Developer Experience

* Automatic Swagger documentation
* ReDoc documentation
* Async database support
* Dependency injection
* Repository pattern
* Service layer architecture
* Structured logging
* Custom exception handling
* Docker support
* Alembic migrations
* Automated tests
* Environment-based configuration

---

# 🏗️ Architecture

Auth API follows a layered backend architecture.

```text
app/
│
├── routers/
│       ↓
│   HTTP layer
│
├── services/
│       ↓
│   Business logic
│
├── repositories/
│       ↓
│   Data access
│
└── database/
        ↓
    PostgreSQL
```

### Router Layer

Responsible for:

* HTTP requests
* Request validation
* Authentication dependencies
* Response serialization
* API routing

```text
app/routers/
```

### Service Layer

Contains application and business logic:

* Authentication workflows
* User management
* Token handling
* Email workflows

```text
app/services/
```

### Repository Layer

Responsible for persistence:

* CRUD operations
* Database queries
* User persistence
* Token persistence

```text
app/repositories/
```

### Security Layer

Contains security-sensitive functionality:

* Password hashing
* JWT handling
* Token generation
* Token validation

```text
app/security/
```

---

# 📂 Project Structure

```text
auth-api/
│
├── app/
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── core/
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   │
│   ├── models/
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── refresh_token.py
│   │   ├── password_reset_token.py
│   │   └── email_verification_token.py
│   │
│   ├── schemas/
│   │   ├── common.py
│   │   ├── user.py
│   │   └── auth.py
│   │
│   ├── repositories/
│   │   ├── base.py
│   │   ├── user.py
│   │   └── token.py
│   │
│   ├── services/
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── token.py
│   │   └── email.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── health.py
│   │
│   ├── dependencies/
│   │   ├── auth.py
│   │   ├── database.py
│   │   └── services.py
│   │
│   ├── security/
│   │   ├── password.py
│   │   ├── jwt.py
│   │   └── tokens.py
│   │
│   ├── middleware/
│   │   ├── logging.py
│   │   ├── rate_limit.py
│   │   └── security_headers.py
│   │
│   ├── utils/
│   │   ├── validators.py
│   │   └── helpers.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_user.py
│   │   └── test_validators.py
│   │
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

# 🔄 Authentication Flow

```text
┌──────────────┐
│    Register  │
└──────┬───────┘
       │
       ▼
┌────────────────────┐
│ Hash Password      │
│      Argon2        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Store User         │
│   PostgreSQL       │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Email Verification │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│       Login        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────────────┐
│ Generate Access + Refresh  │
│          Tokens            │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│     Protected APIs         │
└────────────────────────────┘
```

---

# 🔑 Token Strategy

## Access Token

Access tokens authenticate API requests.

```http
Authorization: Bearer <access_token>
```

Recommended lifetime:

```text
15 minutes
```

Short-lived access tokens reduce the impact of token compromise.

---

## Refresh Token

Refresh tokens are used to obtain new access tokens without requiring the user to log in again.

Auth API supports:

* Database persistence
* Token rotation
* Token revocation
* Session/device association
* Expiration
* Logout invalidation

Recommended lifetime:

```text
30 days
```

### Refresh Flow

```text
Client
  │
  │ Refresh Token
  ▼
/auth/refresh
  │
  ├── Validate token
  ├── Check expiration
  ├── Check revocation
  ├── Rotate token
  │
  ▼
New Access Token
+
New Refresh Token
```

---

# 📡 API Reference

## Authentication

| Method | Endpoint                | Description            |
| :----: | ----------------------- | ---------------------- |
| `POST` | `/auth/register`        | Create a new account   |
| `POST` | `/auth/login`           | Authenticate user      |
| `POST` | `/auth/refresh`         | Refresh access token   |
| `POST` | `/auth/logout`          | Logout current session |
| `POST` | `/auth/logout-all`      | Logout all sessions    |
| `POST` | `/auth/verify-email`    | Verify email address   |
| `POST` | `/auth/forgot-password` | Request password reset |
| `POST` | `/auth/reset-password`  | Reset password         |

## User

|  Method | Endpoint          | Description      |
| :-----: | ----------------- | ---------------- |
|  `GET`  | `/users/me`       | Get current user |
| `PATCH` | `/users/me`       | Update profile   |
| `PATCH` | `/users/password` | Change password  |

## System

| Method | Endpoint  | Description  |
| :----: | --------- | ------------ |
|  `GET` | `/health` | Health check |

---

# ⚙️ Getting Started

## Requirements

Before running the project, make sure you have:

* Python **3.13+**
* PostgreSQL
* Git
* Docker *(optional)*

---

## 1. Clone the Repository

```bash
git clone https://github.com/ItsWanheda/auth-api.git

cd auth-api
```

---

## 2. Create a Virtual Environment

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment

Create your environment file:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Example configuration:

```env
DATABASE_URL=postgresql://user:password@localhost/authdb

JWT_SECRET_KEY=change_this_in_production

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
```

> 🔒 Never commit `.env` or production secrets to version control.

---

# 🗄️ Database

Run the database migrations:

```bash
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "add_new_feature"
```

---

# ▶️ Run the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

---

# 📚 API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

```text
http://localhost:8000/docs
```

### ReDoc

```text
http://localhost:8000/redoc
```

---

# 🐳 Docker

Build the containers:

```bash
docker compose build
```

Start the development environment:

```bash
docker compose up
```

Run in detached mode:

```bash
docker compose up -d
```

Stop the environment:

```bash
docker compose down
```

---

# 🧪 Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app
```

---

# 🛠️ Development Commands

If you use the included `Makefile`:

```bash
make install
make test
make format
make lint
```

---

# 🗺️ Roadmap

## Authentication

* [ ] OAuth2 / OpenID Connect
* [ ] Google authentication
* [ ] GitHub authentication
* [ ] Discord authentication
* [ ] Two-factor authentication
* [ ] WebAuthn / Passkeys

## Security

* [ ] Device management
* [ ] Login history
* [ ] Suspicious-login detection
* [ ] Advanced rate limiting
* [ ] Security audit logs

## Platform

* [ ] Admin dashboard
* [ ] Role-based access control
* [ ] Permission system
* [ ] API keys
* [ ] Multi-tenant support
* [ ] Microservice integration

---

# 🤝 Contributing

Contributions, bug reports, feature requests, and security improvements are welcome.

### Development workflow

```bash
# Fork the repository

git clone https://github.com/ItsWanheda/auth-api.git

cd auth-api

git checkout -b feature/my-feature
```

Make your changes, then:

```bash
git add .

git commit -m "feat: add my feature"

git push origin feature/my-feature
```

Finally, open a Pull Request.

### Contribution areas

* 🐛 Bug fixes
* 🔐 Security improvements
* ⚡ Performance
* 🧪 Tests
* 📚 Documentation
* ✨ New authentication features
* 🏗️ Architecture improvements

---

# 🔒 Security

If you discover a security vulnerability, please **do not open a public issue with sensitive details**.

Instead, report the vulnerability privately through the repository's available security reporting channel.

Security-related contributions are especially welcome.

---

# 📄 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Author

Built with ❤️ by **ItsWanheda**

### Stack

* 🐍 Python
* ⚡ FastAPI
* 🐘 PostgreSQL
* 🧩 SQLAlchemy
* 🔑 JWT
* 🛡️ Argon2
* 🐳 Docker
* 🔄 Alembic

---

<div align="center">

### 🔐 Secure identity. Clean architecture. Modern backend engineering.

If this project is useful to you, consider giving it a ⭐ on GitHub.

**Built for developers who care about security and maintainability.**

</div>
