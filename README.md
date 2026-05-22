# ProjectFlow

A Monday.com-style project management app. Stage 1 covers user authentication, boards, and items.

**Stack:** Python 3 · Flask · SQLite · SQLAlchemy · Flask-Migrate · Tailwind CSS · Alpine.js

---

## Setup (Windows PowerShell)

Run every command from inside the `project-manager\` folder.

### 1. Create and activate the virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If you get an execution policy error, first run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Initialise the database

```powershell
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

### 4. Seed demo data

```powershell
python seed.py
```

### 5. Run the app

```powershell
flask run
```

Open **http://127.0.0.1:5000** in your browser.

---

## Demo login

| Field    | Value              |
|----------|--------------------|
| Email    | demo@example.com   |
| Password | demo1234           |

The demo account has 3 boards pre-loaded with sample items.

---

## Running tests

```powershell
pytest tests/ -v
```

---

## Features (Stage 1)

- Sign up, log in, log out
- Create boards with a name and colour
- View a board and its items
- Add items to a board
- Delete items (with browser confirmation)
- Delete a board (with inline confirmation)
- All data scoped to the logged-in user — users cannot see or modify each other's boards

---

## Project structure

```
project-manager/
├── app/
│   ├── __init__.py        # App factory
│   ├── models.py          # User, Board, Item
│   ├── auth/              # Signup · login · logout
│   ├── boards/            # Board + item routes
│   ├── templates/
│   └── static/
├── migrations/
├── tests/
├── config.py
├── run.py
├── seed.py
├── requirements.txt
└── .env.example
```
