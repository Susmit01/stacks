# Stacks

A full-stack project management platform inspired by Monday.com — built with Claude Code in a single weekend, with zero manual coding.

**Stack:** Flask · SQLAlchemy · Alpine.js · Tailwind CSS · SortableJS · Chart.js

**Demo login:** `demo@example.com` / `demo1234`

---

## Deploying to Render

### 1. Push to GitHub

Make sure the `project-manager/` folder is committed and pushed to a GitHub repository.

### 2. Create a PostgreSQL database on Render

In the Render dashboard, create a new **PostgreSQL** instance (free tier is fine). Once it's ready, copy the **Internal Database URL**.

### 3. Create a new Web Service on Render

- Connect your GitHub repository
- **Root Directory:** `project-manager`
- **Runtime:** Python
- **Build Command:** `pip install -r requirements.txt && flask db upgrade`
- **Start Command:** *(leave blank — Procfile is used automatically)*

### 4. Set environment variables

Add these in the Render service's **Environment** tab:

| Variable | Value |
|---|---|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `b3f8a2c1e9d047f6b5a4c8e2d1f0a3b7c6e5d4f8a1b2c3d4e5f6a7b8c9d0e1f2` |
| `DATABASE_URL` | *(Internal Database URL from step 2)* |

### 5. Seed demo data

After the first successful deploy, open a **Render Shell** for the service and run:

```
python seed.py
```

This creates the demo user and populates three sample boards. **Running it again wipes all data and resets from scratch.**

---

## Required environment variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Long random string used to sign session cookies |
| `DATABASE_URL` | PostgreSQL connection string (provided by Render) |
| `FLASK_ENV` | Set to `production` to enable secure HTTPS-only cookies |

---

## Running locally

```powershell
cd project-manager
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask db upgrade
python seed.py        # optional — loads demo data
flask run
```

The app runs at `http://127.0.0.1:5000`. A local SQLite database is created automatically at `app.db`.

---

## Demo credentials

| | |
|---|---|
| Email | `demo@example.com` |
| Password | `demo1234` |

Anyone can sign up with their own account. New accounts start with an empty workspace and cannot see the demo user's boards or data.

> Demo data does not auto-reset. Re-run `python seed.py` to reset — this drops and recreates all tables.

---

## Running tests

```powershell
pytest tests/ -v
```

---

## Project structure

```
project-manager/
├── app/
│   ├── __init__.py        # App factory + error handlers
│   ├── models.py          # User, Board, Group, Item, Column, CellValue
│   ├── auth/              # Signup · login · logout
│   ├── boards/            # All board, group, item, column routes
│   └── templates/
├── migrations/            # Alembic migration history
├── tests/
├── config.py
├── run.py
├── seed.py
├── Procfile               # gunicorn for Render
├── runtime.txt            # Python version pin
├── requirements.txt
└── .env.example
```
