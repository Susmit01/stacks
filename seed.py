"""
Run once to populate the database with demo data.
Usage (from project-manager/ with venv active):
    python seed.py
"""
from app import create_app, db, bcrypt
from app.models import User, Board, Item, Column, CellValue


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
        b1 = Board(name='Claude Rollout Campaign', color='#6366f1', owner_id=demo.id)
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

        b1_items = [
            ('Write model capability summary',    'Done',           'Alex Chen',   '2026-05-10', 'High'),
            ('Design prompt engineering guide',   'Working on it',  'Sarah Okafor', '2026-05-22', 'High'),
            ('Build API integration demo',        'Working on it',  'James Liu',   '2026-05-28', 'Critical'),
            ('Draft customer announcement email', 'Not started',    'Sarah Okafor', '2026-06-05', 'Medium'),
            ('Set up evaluation pipeline',        'Stuck',          'Alex Chen',   '2026-05-20', 'Critical'),
            ('Stakeholder demo rehearsal',        'Not started',    'James Liu',   '2026-06-10', 'Low'),
        ]
        for pos, (name, status, owner, due, priority) in enumerate(b1_items):
            item = Item(board_id=b1.id, name=name, position=pos)
            db.session.add(item)
            db.session.flush()
            db.session.add(CellValue(item_id=item.id, column_id=s.id, value=status))
            db.session.add(CellValue(item_id=item.id, column_id=o.id, value=owner))
            db.session.add(CellValue(item_id=item.id, column_id=d.id, value=due))
            db.session.add(CellValue(item_id=item.id, column_id=p.id, value=priority))

        # ── Board 2: Website Redesign ─────────────────────────────────────────
        b2 = Board(name='Corporate Website Redesign Q3', color='#22c55e', owner_id=demo.id)
        db.session.add(b2)
        db.session.flush()

        b2_cols = [
            Column(board_id=b2.id, name='Status',    col_type='status',   position=0),
            Column(board_id=b2.id, name='Assignee',  col_type='person',   position=1),
            Column(board_id=b2.id, name='Due',       col_type='date',     position=2),
        ]
        for c in b2_cols:
            db.session.add(c)
        db.session.flush()
        s2, a2, d2 = b2_cols

        b2_items = [
            ('Stakeholder discovery interviews', 'Done',          'Priya Singh',  '2026-04-30'),
            ('Information architecture',         'Done',          'Priya Singh',  '2026-05-08'),
            ('Homepage wireframes',              'Done',          'Tom Bradley',  '2026-05-14'),
            ('Component library build',          'Working on it', 'Tom Bradley',  '2026-05-26'),
            ('Responsive layout implementation', 'Working on it', 'Priya Singh',  '2026-06-02'),
            ('Accessibility audit',              'Not started',   'Tom Bradley',  '2026-06-09'),
            ('Cross-browser QA',                 'Not started',   '',             '2026-06-16'),
        ]
        for pos, row in enumerate(b2_items):
            name, status, assignee, due = row
            item = Item(board_id=b2.id, name=name, position=pos)
            db.session.add(item)
            db.session.flush()
            db.session.add(CellValue(item_id=item.id, column_id=s2.id, value=status))
            db.session.add(CellValue(item_id=item.id, column_id=a2.id, value=assignee))
            db.session.add(CellValue(item_id=item.id, column_id=d2.id, value=due))

        # ── Board 3: Product Launch v2.0 ──────────────────────────────────────
        b3 = Board(name='Product Launch — Apex v2.0', color='#f97316', owner_id=demo.id)
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

        b3_items = [
            ('Finalise feature requirements',   'Done',          'Maya Patel',   'High'),
            ('Write press release',             'Working on it', 'Lena Kovac',   'Medium'),
            ('Prepare demo environment',        'Working on it', 'Maya Patel',   'Critical'),
            ('Train support team',              'Not started',   'Lena Kovac',   'High'),
            ('Schedule launch webinar',         'Not started',   'Maya Patel',   'Medium'),
            ('Update pricing page',             'Stuck',         '',             'High'),
            ('Coordinate with sales',           'Not started',   'Lena Kovac',   'Low'),
            ('Post-launch retro template',      'Not started',   '',             'Low'),
        ]
        for pos, (name, status, owner, priority) in enumerate(b3_items):
            item = Item(board_id=b3.id, name=name, position=pos)
            db.session.add(item)
            db.session.flush()
            db.session.add(CellValue(item_id=item.id, column_id=s3.id, value=status))
            db.session.add(CellValue(item_id=item.id, column_id=o3.id, value=owner))
            db.session.add(CellValue(item_id=item.id, column_id=p3.id, value=priority))

        db.session.commit()
        print('Seed complete.')
        print('Login: demo@example.com / demo1234')


if __name__ == '__main__':
    seed()
