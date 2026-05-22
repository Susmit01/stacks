from flask import Blueprint

boards_bp = Blueprint('boards', __name__)

from app.boards import routes  # noqa: F401, E402
