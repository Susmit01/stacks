from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.boards import boards_bp
from app.boards.forms import BoardForm, ItemForm, BOARD_COLORS
from app.models import Board, Item


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
    form = ItemForm()
    return render_template('boards/view.html', board=board, form=form)


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
