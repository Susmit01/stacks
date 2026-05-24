from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.boards import boards_bp
from app.boards.forms import BoardForm, ItemForm, BOARD_COLORS
from app.models import Board, Item, Column, CellValue, Group


# ── Page routes ───────────────────────────────────────────────────────────────

@boards_bp.route('/dashboard')
@login_required
def dashboard():
    boards = Board.query.filter_by(owner_id=current_user.id)\
        .order_by(Board.updated_at.desc()).all()

    form = BoardForm()
    if not boards:
        return render_template('boards/dashboard.html',
            boards=[], total_items=0, assigned_to_me=0,
            status_counts={}, priority_counts={},
            form=form, colors=BOARD_COLORS)

    board_ids = [b.id for b in boards]

    total_items = db.session.query(db.func.count(Item.id))\
        .filter(Item.board_id.in_(board_ids)).scalar() or 0

    # Items assigned to current user via any person column
    person_col_ids = [c.id for c in Column.query.filter(
        Column.board_id.in_(board_ids), Column.col_type == 'person').all()]
    assigned_to_me = 0
    if person_col_ids:
        assigned_to_me = db.session.query(db.func.count(CellValue.id)).filter(
            CellValue.column_id.in_(person_col_ids),
            CellValue.value == current_user.full_name
        ).scalar() or 0

    # Status distribution
    status_counts = {'Not started': 0, 'Working on it': 0, 'Stuck': 0, 'Done': 0}
    status_col_ids = [c.id for c in Column.query.filter(
        Column.board_id.in_(board_ids), Column.col_type == 'status').all()]
    if status_col_ids:
        for cv in CellValue.query.filter(
                CellValue.column_id.in_(status_col_ids), CellValue.value != '').all():
            if cv.value in status_counts:
                status_counts[cv.value] += 1

    # Priority distribution
    priority_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
    priority_col_ids = [c.id for c in Column.query.filter(
        Column.board_id.in_(board_ids), Column.col_type == 'priority').all()]
    if priority_col_ids:
        for cv in CellValue.query.filter(
                CellValue.column_id.in_(priority_col_ids), CellValue.value != '').all():
            if cv.value in priority_counts:
                priority_counts[cv.value] += 1

    return render_template('boards/dashboard.html',
        boards=boards, total_items=total_items, assigned_to_me=assigned_to_me,
        status_counts=status_counts, priority_counts=priority_counts,
        form=form, colors=BOARD_COLORS)


@boards_bp.route('/')
@login_required
def root():
    return redirect(url_for('boards.dashboard'))


@boards_bp.route('/about')
def about():
    return render_template('boards/about.html')


@boards_bp.route('/boards')
@login_required
def index():
    boards = Board.query.filter_by(owner_id=current_user.id)\
        .order_by(Board.created_at.desc()).all()
    item_counts = {
        b.id: db.session.query(db.func.count(Item.id))
              .filter_by(board_id=b.id).scalar() or 0
        for b in boards
    }
    form = BoardForm()
    return render_template(
        'boards/index.html', boards=boards, item_counts=item_counts,
        form=form, colors=BOARD_COLORS
    )


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
        db.session.flush()
        group = Group(board_id=board.id, name='Items', color='#0049b7', position=0)
        db.session.add(group)
        db.session.commit()
    else:
        flash('Board name is required.', 'error')
    return redirect(url_for('boards.index'))


def _render_board(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    columns = Column.query.filter_by(board_id=board.id).order_by(Column.position).all()
    groups = Group.query.filter_by(board_id=board.id).order_by(Group.position).all()

    all_item_ids = [item.id for g in groups for item in g.items]
    cells = {iid: {} for iid in all_item_ids}
    if columns and all_item_ids:
        cvs = CellValue.query.filter(
            CellValue.column_id.in_([c.id for c in columns]),
            CellValue.item_id.in_(all_item_ids)
        ).all()
        for cv in cvs:
            if cv.item_id in cells:
                cells[cv.item_id][cv.column_id] = cv.value

    groups_data = [{'id': g.id, 'name': g.name, 'count': len(g.items)} for g in groups]
    collapsed_group_ids = [g.id for g in groups if g.collapsed]

    form = ItemForm()
    return render_template(
        'boards/view.html',
        board=board, columns=columns, groups=groups, cells=cells, form=form,
        all_item_ids=all_item_ids, groups_data=groups_data,
        collapsed_group_ids=collapsed_group_ids,
        group_colors=Group.GROUP_COLORS,
    )


@boards_bp.route('/boards/<int:board_id>')
@login_required
def view_board(board_id):
    return _render_board(board_id)


@boards_bp.route('/boards/<int:board_id>/items/<int:item_id>')
@login_required
def view_board_item(board_id, item_id):
    # Verify item belongs to board; JS will open the panel from the URL
    Item.query.filter_by(id=item_id, board_id=board_id).first_or_404()
    return _render_board(board_id)


@boards_bp.route('/boards/<int:board_id>/items/<int:item_id>/detail')
@login_required
def item_detail(board_id, item_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    item = Item.query.filter_by(id=item_id, board_id=board.id).first_or_404()
    columns = Column.query.filter_by(board_id=board.id).order_by(Column.position).all()
    cv_map = {cv.column_id: cv.value for cv in item.cells}
    cells = [
        {'col_id': col.id, 'col_name': col.name, 'col_type': col.col_type,
         'value': cv_map.get(col.id, '')}
        for col in columns
    ]
    return jsonify({
        'id': item.id,
        'name': item.name,
        'description': item.description or '',
        'group_id': item.group_id,
        'group_name': item.group.name if item.group else '',
        'cells': cells,
    })


@boards_bp.route('/boards/<int:board_id>/items/<int:item_id>/description', methods=['PATCH'])
@login_required
def update_item_description(board_id, item_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    item = Item.query.filter_by(id=item_id, board_id=board.id).first_or_404()
    data = request.get_json(silent=True) or {}
    item.description = data.get('description', '')
    db.session.commit()
    return jsonify({'id': item.id, 'description': item.description})


@boards_bp.route('/boards/<int:board_id>/items/add', methods=['POST'])
@login_required
def add_item(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    form = ItemForm()
    if form.validate_on_submit():
        first_group = Group.query.filter_by(board_id=board.id).order_by(Group.position).first()
        if not first_group:
            flash('Create a group first.', 'error')
            return redirect(url_for('boards.view_board', board_id=board_id))
        max_pos = db.session.query(db.func.max(Item.position))\
            .filter_by(group_id=first_group.id).scalar() or 0
        item = Item(
            board_id=board.id, group_id=first_group.id,
            name=form.name.data.strip(), position=max_pos + 1,
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added.', 'success')
    return redirect(url_for('boards.view_board', board_id=board_id))


@boards_bp.route('/boards/<int:board_id>/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(board_id, item_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    item = Item.query.filter_by(id=item_id, board_id=board.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('boards.view_board', board_id=board_id))


@boards_bp.route('/boards/<int:board_id>/items/bulk-delete', methods=['POST'])
@login_required
def bulk_delete_items(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or {}
    item_ids = [int(i) for i in data.get('item_ids', []) if str(i).lstrip('-').isdigit()]
    if item_ids:
        Item.query.filter(
            Item.id.in_(item_ids),
            Item.board_id == board.id
        ).delete(synchronize_session='fetch')
        db.session.commit()
    return jsonify({'ok': True})


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


@boards_bp.route('/boards/<int:board_id>/items/reorder', methods=['POST'])
@login_required
def reorder_items(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or {}
    updates = data.get('order', [])
    if not updates:
        return jsonify({'ok': True})
    item_ids = [int(u['item_id']) for u in updates]
    items = {
        i.id: i for i in
        Item.query.filter(Item.id.in_(item_ids), Item.board_id == board.id).all()
    }
    valid_group_ids = {
        g.id for g in Group.query.filter_by(board_id=board.id).all()
    }
    for u in updates:
        item = items.get(int(u['item_id']))
        gid = int(u['group_id'])
        if item and gid in valid_group_ids:
            item.group_id = gid
            item.position = int(u['position'])
    db.session.commit()
    return jsonify({'ok': True})


# ── Group AJAX API ────────────────────────────────────────────────────────────

@boards_bp.route('/boards/<int:board_id>/groups', methods=['POST'])
@login_required
def add_group(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or 'New Group').strip()
    color = data.get('color', '#0049b7')
    if color not in Group.GROUP_COLORS:
        color = '#0049b7'
    max_pos = db.session.query(db.func.max(Group.position))\
        .filter_by(board_id=board.id).scalar() or 0
    group = Group(board_id=board.id, name=name, color=color, position=max_pos + 1)
    db.session.add(group)
    db.session.commit()
    return jsonify({'id': group.id, 'name': group.name, 'color': group.color})


@boards_bp.route('/boards/<int:board_id>/groups/<int:group_id>', methods=['PATCH'])
@login_required
def update_group(board_id, group_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    group = Group.query.filter_by(id=group_id, board_id=board.id).first_or_404()
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = str(data['name']).strip()
        if name:
            group.name = name
    if 'color' in data and data['color'] in Group.GROUP_COLORS:
        group.color = data['color']
    if 'collapsed' in data:
        group.collapsed = bool(data['collapsed'])
    db.session.commit()
    return jsonify({'id': group.id, 'name': group.name, 'color': group.color, 'collapsed': group.collapsed})


@boards_bp.route('/boards/<int:board_id>/groups/<int:group_id>', methods=['DELETE'])
@login_required
def delete_group(board_id, group_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    group_count = Group.query.filter_by(board_id=board.id).count()
    if group_count <= 1:
        return jsonify({'error': 'A board must have at least one group'}), 400
    group = Group.query.filter_by(id=group_id, board_id=board.id).first_or_404()
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'delete')
    if action == 'move':
        target_id = data.get('target_group_id')
        target = Group.query.filter_by(id=target_id, board_id=board.id).first_or_404()
        max_pos = db.session.query(db.func.max(Item.position))\
            .filter_by(group_id=target.id).scalar() or 0
        for i, item in enumerate(
            Item.query.filter_by(group_id=group.id).order_by(Item.position).all()
        ):
            item.group_id = target.id
            item.position = max_pos + i + 1
        db.session.flush()
    db.session.delete(group)
    db.session.commit()
    return jsonify({'ok': True})


@boards_bp.route('/boards/<int:board_id>/groups/apply-preset', methods=['POST'])
@login_required
def apply_group_preset(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or {}
    preset = data.get('preset', '')

    PRESETS = {
        'status': {
            'col_type': 'status',
            'groups': [
                {'name': 'Not started', 'color': '#9db0c8'},
                {'name': 'Working on it', 'color': '#0049b7'},
                {'name': 'Stuck', 'color': '#ff1d58'},
                {'name': 'Done', 'color': '#00c875'},
            ],
        },
        'priority': {
            'col_type': 'priority',
            'groups': [
                {'name': 'Low', 'color': '#00c875'},
                {'name': 'Medium', 'color': '#fdab3d'},
                {'name': 'High', 'color': '#ff642e'},
                {'name': 'Critical', 'color': '#ff1d58'},
            ],
        },
    }

    if preset not in PRESETS:
        return jsonify({'error': 'Invalid preset'}), 400

    config = PRESETS[preset]
    max_pos = db.session.query(db.func.max(Group.position)).filter_by(board_id=board.id).scalar() or 0

    # Create the preset groups
    created_groups = {}
    for i, gspec in enumerate(config['groups']):
        group = Group(board_id=board.id, name=gspec['name'], color=gspec['color'], position=max_pos + i + 1)
        db.session.add(group)
        db.session.flush()
        created_groups[gspec['name']] = group

    # Find the first column of matching type on this board
    col = Column.query.filter_by(board_id=board.id, col_type=config['col_type']).first()
    if col:
        # Track per-group position counter
        pos_counters = {name: 0 for name in created_groups}
        all_items = Item.query.join(Group, Item.group_id == Group.id)\
            .filter(Group.board_id == board.id).order_by(Item.position).all()
        for item in all_items:
            cell = CellValue.query.filter_by(item_id=item.id, column_id=col.id).first()
            if cell and cell.value and cell.value in created_groups:
                target = created_groups[cell.value]
                item.group_id = target.id
                item.position = pos_counters[cell.value]
                pos_counters[cell.value] += 1

    db.session.commit()
    return jsonify({'ok': True})


@boards_bp.route('/boards/<int:board_id>/groups/reorder', methods=['POST'])
@login_required
def reorder_groups(board_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or {}
    order = data.get('order', [])
    group_map = {g.id: g for g in Group.query.filter_by(board_id=board.id).all()}
    for pos, gid in enumerate(order):
        if gid in group_map:
            group_map[gid].position = pos
    db.session.commit()
    return jsonify({'ok': True})


@boards_bp.route('/boards/<int:board_id>/groups/<int:group_id>/items', methods=['POST'])
@login_required
def add_item_to_group(board_id, group_id):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first_or_404()
    group = Group.query.filter_by(id=group_id, board_id=board.id).first_or_404()
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    max_pos = db.session.query(db.func.max(Item.position))\
        .filter_by(group_id=group.id).scalar() or 0
    item = Item(board_id=board.id, group_id=group.id, name=name, position=max_pos + 1)
    db.session.add(item)
    db.session.commit()
    return jsonify({'id': item.id, 'name': item.name, 'group_id': group.id})
