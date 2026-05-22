from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.boards import boards_bp
from app.boards.forms import BoardForm, ItemForm, BOARD_COLORS
from app.models import Board, Item, Column, CellValue


# ── Page routes ───────────────────────────────────────────────────────────────

@boards_bp.route('/')
@login_required
def index():
    boards = Board.query.filter_by(owner_id=current_user.id)\
        .order_by(Board.created_at.desc()).all()
    form = BoardForm()
    return render_template('boards/index.html', boards=boards, form=form, colors=BOARD_COLORS)


@boards_bp.route('/boards/create', methods=['POST'])
@login_required
def create_board():
    form = BoardForm()
    if form.validate_on_submit():
        board = Board(
            name=form.name.data.strip(),
            color=form.color.data,
            owner_id=current_user.id,
        )
        db.session.add(board)
        db.session.commit()
    else:
        flash('Board name is required.', 'error')
    return redirect(url_for('boards.index'))


@boards_bp.route('/boards/<int:board_id>')
@login_required
def view_board(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    columns = Column.query.filter_by(board_id=board.id).order_by(Column.position).all()

    cells = {item.id: {} for item in board.items}
    if columns:
        cvs = CellValue.query.filter(
            CellValue.column_id.in_([c.id for c in columns])
        ).all()
        for cv in cvs:
            if cv.item_id in cells:
                cells[cv.item_id][cv.column_id] = cv.value

    form = ItemForm()
    return render_template(
        'boards/view.html', board=board, columns=columns, cells=cells, form=form
    )


@boards_bp.route('/boards/<int:board_id>/items/add', methods=['POST'])
@login_required
def add_item(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    form = ItemForm()
    if form.validate_on_submit():
        max_pos = db.session.query(db.func.max(Item.position))\
            .filter_by(board_id=board.id).scalar() or 0
        item = Item(
            board_id=board.id,
            name=form.name.data.strip(),
            position=max_pos + 1,
        )
        db.session.add(item)
        db.session.commit()
    return redirect(url_for('boards.view_board', board_id=board_id))


@boards_bp.route('/boards/<int:board_id>/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(board_id, item_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    item = Item.query.filter_by(id=item_id, board_id=board.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('boards.view_board', board_id=board_id))


@boards_bp.route('/boards/<int:board_id>/delete', methods=['POST'])
@login_required
def delete_board(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    db.session.delete(board)
    db.session.commit()
    return redirect(url_for('boards.index'))


# ── Column AJAX API ───────────────────────────────────────────────────────────

@boards_bp.route('/boards/<int:board_id>/columns', methods=['POST'])
@login_required
def add_column(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or {}
    col_type = data.get('type', '').strip()
    name = data.get('name', '').strip()
    if not name or col_type not in Column.VALID_TYPES:
        return jsonify({'error': 'Invalid input'}), 400
    max_pos = db.session.query(db.func.max(Column.position))\
        .filter_by(board_id=board.id).scalar() or 0
    col = Column(board_id=board.id, name=name, col_type=col_type, position=max_pos + 1)
    db.session.add(col)
    db.session.commit()
    return jsonify({'id': col.id, 'name': col.name, 'col_type': col.col_type, 'position': col.position})


@boards_bp.route('/boards/<int:board_id>/columns/<int:col_id>/rename', methods=['PATCH'])
@login_required
def rename_column(board_id, col_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    col = Column.query.filter_by(id=col_id, board_id=board.id).first_or_404()
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    col.name = name
    db.session.commit()
    return jsonify({'id': col.id, 'name': col.name})


@boards_bp.route('/boards/<int:board_id>/columns/<int:col_id>', methods=['DELETE'])
@login_required
def delete_column(board_id, col_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    col = Column.query.filter_by(id=col_id, board_id=board.id).first_or_404()
    db.session.delete(col)
    db.session.commit()
    return jsonify({'ok': True})


@boards_bp.route('/boards/<int:board_id>/columns/reorder', methods=['POST'])
@login_required
def reorder_columns(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or {}
    order = data.get('order', [])
    col_map = {c.id: c for c in Column.query.filter_by(board_id=board.id).all()}
    for pos, col_id in enumerate(order):
        if col_id in col_map:
            col_map[col_id].position = pos
    db.session.commit()
    return jsonify({'ok': True})


# ── Item AJAX API ─────────────────────────────────────────────────────────────

@boards_bp.route('/boards/<int:board_id>/items/<int:item_id>/name', methods=['PATCH'])
@login_required
def rename_item(board_id, item_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    item = Item.query.filter_by(id=item_id, board_id=board.id).first_or_404()
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    item.name = name
    db.session.commit()
    return jsonify({'id': item.id, 'name': item.name})


@boards_bp.route('/boards/<int:board_id>/items/<int:item_id>/cells/<int:col_id>', methods=['PATCH'])
@login_required
def upsert_cell(board_id, item_id, col_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    item = Item.query.filter_by(id=item_id, board_id=board.id).first_or_404()
    col = Column.query.filter_by(id=col_id, board_id=board.id).first_or_404()
    data = request.get_json(silent=True) or {}
    value = data.get('value', '')
    cell = CellValue.query.filter_by(item_id=item.id, column_id=col.id).first()
    if cell:
        cell.value = value
    else:
        cell = CellValue(item_id=item.id, column_id=col.id, value=value)
        db.session.add(cell)
    db.session.commit()
    return jsonify({'item_id': item.id, 'column_id': col.id, 'value': value})
