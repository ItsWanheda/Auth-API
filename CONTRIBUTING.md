# Contributing Guide

Thank you for contributing to Auth API.

## Development Setup

1. Fork repository

2. Clone:

```bash
git clone https://github.com/username/auth-api.git
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env`

```bash
cp .env.example .env
```
---

## Branch Naming
Use:

```text
feature/add-google-auth
bugfix/fix-login-error
docs/update-readme
```

---

## Commit Style
Use conventional commits:

```text
feat: add refresh token rotation

fix: resolve jwt validation issue

docs: update installation guide
```

---

## Pull Requests
Before submitting:
* Run tests
* Format code
* Update documentation
* Explain your changes