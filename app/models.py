from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    boards = db.relationship(
        'Board', backref='owner', lazy=True, cascade='all, delete-orphan'
    )


class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    color = db.Column(db.String(7), nullable=False, default='#6366f1')
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship(
        'Item', backref='board', lazy=True,
        cascade='all, delete-orphan',
        order_by='Item.position'
    )
    columns = db.relationship(
        'Column', backref='board', lazy=True,
        cascade='all, delete-orphan',
        order_by='Column.position'
    )


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    name = db.Column(db.String(300), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cells = db.relationship(
        'CellValue', backref='item', lazy=True, cascade='all, delete-orphan'
    )


class Column(db.Model):
    __tablename__ = 'columns'

    VALID_TYPES = ('status', 'person', 'date', 'priority', 'text', 'number')

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    col_type = db.Column(db.String(20), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cells = db.relationship(
        'CellValue', backref='column', lazy=True, cascade='all, delete-orphan'
    )


class CellValue(db.Model):
    __tablename__ = 'cell_values'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    column_id = db.Column(db.Integer, db.ForeignKey('columns.id'), nullable=False)
    value = db.Column(db.String(500), nullable=False, default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('item_id', 'column_id', name='uq_item_column'),
    )
