"""
Run once to populate the database with demo data.
Usage (from project-manager/ with venv active):
    python seed.py
"""
from app import create_app, db, bcrypt
from app.models import User, Board, Item, Column, CellValue, Group


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        pw_hash = bcrypt.generate_password_hash('demo1234').decode('utf-8')
        demo = User(email='demo@example.com', password_hash=pw_hash, full_name='Demo User')
        db.session.add(demo)
        db.session.flush()

        # ── Board 1: Claude Rollout Campaign ──────────────────────────────────
        b1 = Board(name='Claude Rollout Campaign', color='#ff1d58', owner_id=demo.id)
        db.session.add(b1)
        db.session.flush()

        b1_cols = [
            Column(board_id=b1.id, name='Status',   col_type='status',   position=0),
            Column(board_id=b1.id, name='Owner',    col_type='person',   position=1),
            Column(board_id=b1.id, name='Due date', col_type='date',     position=2),
            Column(board_id=b1.id, name='Priority', col_type='priority', position=3),
        ]
        for c in b1_cols:
            db.session.add(c)
        db.session.flush()
        s, o, d, p = b1_cols

        # Three groups: To Do / In Progress / Done
        b1_g1 = Group(board_id=b1.id, name='To Do',       color='#9db0c8', position=0)
        b1_g2 = Group(board_id=b1.id, name='In Progress', color='#0049b7', position=1)
        b1_g3 = Group(board_id=b1.id, name='Done',        color='#00c875', position=2)
        for g in [b1_g1, b1_g2, b1_g3]:
            db.session.add(g)
        db.session.flush()

        def add_item(board_id, group, name, pos, cells):
            item = Item(board_id=board_id, group_id=group.id, name=name, position=pos)
            db.session.add(item)
            db.session.flush()
            for col, val in cells:
                db.session.add(CellValue(item_id=item.id, column_id=col.id, value=val))

        # To Do
        add_item(b1.id, b1_g1, 'Draft customer announcement email', 0,
                 [(s, 'Not started'), (o, 'Demo User'), (d, '2026-06-05'), (p, 'Medium')])
        add_item(b1.id, b1_g1, 'Stakeholder demo rehearsal', 1,
                 [(s, 'Not started'), (o, 'James Liu'), (d, '2026-06-10'), (p, 'Low')])
        # In Progress
        add_item(b1.id, b1_g2, 'Design prompt engineering guide', 0,
                 [(s, 'Working on it'), (o, 'Demo User'), (d, '2026-05-22'), (p, 'High')])
        add_item(b1.id, b1_g2, 'Build API integration demo', 1,
                 [(s, 'Working on it'), (o, 'James Liu'), (d, '2026-05-28'), (p, 'Critical')])
        add_item(b1.id, b1_g2, 'Set up evaluation pipeline', 2,
                 [(s, 'Stuck'), (o, 'Alex Chen'), (d, '2026-05-20'), (p, 'Critical')])
        # Done
        add_item(b1.id, b1_g3, 'Write model capability summary', 0,
                 [(s, 'Done'), (o, 'Alex Chen'), (d, '2026-05-10'), (p, 'High')])

        # ── Board 2: Website Redesign ─────────────────────────────────────────
        b2 = Board(name='Corporate Website Redesign Q3', color='#00c875', owner_id=demo.id)
        db.session.add(b2)
        db.session.flush()

        b2_cols = [
            Column(board_id=b2.id, name='Status',   col_type='status', position=0),
            Column(board_id=b2.id, name='Assignee', col_type='person', position=1),
            Column(board_id=b2.id, name='Due',      col_type='date',   position=2),
        ]
        for c in b2_cols:
            db.session.add(c)
        db.session.flush()
        s2, a2, d2 = b2_cols

        b2_g1 = Group(board_id=b2.id, name='Discovery & IA', color='#00c875', position=0)
        b2_g2 = Group(board_id=b2.id, name='Design & Build', color='#0049b7', position=1)
        b2_g3 = Group(board_id=b2.id, name='QA & Launch',    color='#fdab3d', position=2)
        for g in [b2_g1, b2_g2, b2_g3]:
            db.session.add(g)
        db.session.flush()

        add_item(b2.id, b2_g1, 'Stakeholder discovery interviews', 0,
                 [(s2, 'Done'), (a2, 'Priya Singh'), (d2, '2026-04-30')])
        add_item(b2.id, b2_g1, 'Information architecture', 1,
                 [(s2, 'Done'), (a2, 'Priya Singh'), (d2, '2026-05-08')])
        add_item(b2.id, b2_g2, 'Homepage wireframes', 0,
                 [(s2, 'Done'), (a2, 'Tom Bradley'), (d2, '2026-05-14')])
        add_item(b2.id, b2_g2, 'Component library build', 1,
                 [(s2, 'Working on it'), (a2, 'Demo User'), (d2, '2026-05-26')])
        add_item(b2.id, b2_g2, 'Responsive layout implementation', 2,
                 [(s2, 'Working on it'), (a2, 'Demo User'), (d2, '2026-06-02')])
        add_item(b2.id, b2_g3, 'Accessibility audit', 0,
                 [(s2, 'Not started'), (a2, 'Tom Bradley'), (d2, '2026-06-09')])
        add_item(b2.id, b2_g3, 'Cross-browser QA', 1,
                 [(s2, 'Not started'), (a2, ''), (d2, '2026-06-16')])

        # ── Board 3: Product Launch v2.0 ──────────────────────────────────────
        b3 = Board(name='Product Launch — Apex v2.0', color='#fdab3d', owner_id=demo.id)
        db.session.add(b3)
        db.session.flush()

        b3_cols = [
            Column(board_id=b3.id, name='Status',   col_type='status',   position=0),
            Column(board_id=b3.id, name='Owner',    col_type='person',   position=1),
            Column(board_id=b3.id, name='Priority', col_type='priority', position=2),
        ]
        for c in b3_cols:
            db.session.add(c)
        db.session.flush()
        s3, o3, p3 = b3_cols

        b3_g1 = Group(board_id=b3.id, name='Launch Tasks', color='#0049b7', position=0)
        db.session.add(b3_g1)
        db.session.flush()

        for pos, (name, status, owner, priority) in enumerate([
            ('Finalise feature requirements',  'Done',          'Maya Patel', 'High'),
            ('Write press release',            'Working on it', 'Lena Kovac', 'Medium'),
            ('Prepare demo environment',       'Working on it', 'Maya Patel', 'Critical'),
            ('Train support team',             'Not started',   'Lena Kovac', 'High'),
            ('Schedule launch webinar',        'Not started',   'Maya Patel', 'Medium'),
            ('Update pricing page',            'Stuck',         '',           'High'),
            ('Coordinate with sales',          'Not started',   'Lena Kovac', 'Low'),
            ('Post-launch retro template',     'Not started',   '',           'Low'),
        ]):
            add_item(b3.id, b3_g1, name, pos,
                     [(s3, status), (o3, owner), (p3, priority)])

        db.session.commit()
        print('Seed complete.')
        print('Login: demo@example.com / demo1234')


if __name__ == '__main__':
    seed()
