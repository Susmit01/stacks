from app.models import Board, Item
from tests.conftest import make_user


def register(client, email='test@example.com', name='Test User', password='password1'):
    return client.post('/auth/signup', data={
        'email': email,
        'full_name': name,
        'password': password,
    }, follow_redirects=True)


def login(client, email='test@example.com', password='password1'):
    return client.post('/auth/login', data={
        'email': email,
        'password': password,
    }, follow_redirects=True)


def logout(client):
    return client.get('/auth/logout', follow_redirects=True)


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_signup_creates_account_and_redirects(client):
    rv = register(client)
    assert rv.status_code == 200
    assert b'My Boards' in rv.data


def test_login_with_valid_credentials(client, db):
    register(client)           # creates account and auto-logs in
    client.get('/auth/logout') # log out
    rv = login(client)         # log back in
    assert rv.status_code == 200
    assert b'My Boards' in rv.data


def test_login_with_bad_password_shows_error(client, db):
    make_user(db)
    rv = login(client, password='wrongpass')
    assert b'Invalid email or password' in rv.data


# ── Boards ────────────────────────────────────────────────────────────────────

def test_board_creation(client, db, app):
    register(client)
    client.post('/boards/create', data={'name': 'My Board', 'color': '#6366f1'})
    with app.app_context():
        board = Board.query.filter_by(name='My Board').first()
        assert board is not None
        assert board.color == '#6366f1'


def test_item_creation(client, db, app):
    register(client)
    client.post('/boards/create', data={'name': 'Test Board', 'color': '#6366f1'})
    with app.app_context():
        board_id = Board.query.first().id

    client.post(f'/boards/{board_id}/items/add', data={'name': 'My Item'})
    with app.app_context():
        item = Item.query.filter_by(name='My Item').first()
        assert item is not None
        assert item.board_id == board_id


# ── Permission boundary ───────────────────────────────────────────────────────

def test_user_cannot_view_another_users_board(client, db, app):
    # User A creates a board
    register(client, email='usera@example.com')
    client.post('/boards/create', data={'name': 'Private Board', 'color': '#6366f1'})
    with app.app_context():
        board_id = Board.query.first().id
    logout(client)

    # User B tries to access it
    register(client, email='userb@example.com')
    rv = client.get(f'/boards/{board_id}')
    assert rv.status_code == 404


def test_user_cannot_delete_another_users_board(client, db, app):
    register(client, email='usera@example.com')
    client.post('/boards/create', data={'name': 'Private Board', 'color': '#6366f1'})
    with app.app_context():
        board_id = Board.query.first().id
    logout(client)

    register(client, email='userb@example.com')
    rv = client.post(f'/boards/{board_id}/delete')
    assert rv.status_code == 404
    with app.app_context():
        from app import db
    assert db.session.get(Board, board_id) is not None
