"""
Run once to populate the database with demo data.
Usage (from project-manager/ with venv active):
    python seed.py
"""
from app import create_app, db, bcrypt
from app.models import User, Board, Item


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        pw_hash = bcrypt.generate_password_hash('demo1234').decode('utf-8')
        demo = User(email='demo@example.com', password_hash=pw_hash, full_name='Demo User')
        db.session.add(demo)
        db.session.flush()

        boards_data = [
            {
                'name': 'Q2 Marketing Campaign',
                'color': '#6366f1',
                'items': [
                    'Draft campaign brief',
                    'Design social media assets',
                    'Write email newsletter copy',
                    'Set up A/B testing framework',
                    'Review analytics dashboard',
                    'Coordinate with agency on creatives',
                ],
            },
            {
                'name': 'Website Redesign',
                'color': '#22c55e',
                'items': [
                    'Conduct stakeholder interviews',
                    'Create information architecture',
                    'Design homepage wireframe',
                    'Build component library',
                    'Implement responsive layout',
                    'Performance audit',
                    'Cross-browser testing',
                ],
            },
            {
                'name': 'Product Launch — v2.0',
                'color': '#f97316',
                'items': [
                    'Finalise feature requirements',
                    'Write press release draft',
                    'Prepare demo environment',
                    'Train support team',
                    'Schedule launch webinar',
                    'Update pricing page',
                    'Coordinate with sales',
                    'Post-launch retrospective template',
                ],
            },
        ]

        for bd in boards_data:
            board = Board(name=bd['name'], color=bd['color'], owner_id=demo.id)
            db.session.add(board)
            db.session.flush()
            for pos, name in enumerate(bd['items']):
                db.session.add(Item(board_id=board.id, name=name, position=pos))

        db.session.commit()
        print("Seed complete.")
        print("Login: demo@example.com / demo1234")


if __name__ == '__main__':
    seed()
