from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

BOARD_COLORS = [
    '#6366f1',  # indigo
    '#8b5cf6',  # violet
    '#ec4899',  # pink
    '#ef4444',  # red
    '#f97316',  # orange
    '#eab308',  # yellow
    '#22c55e',  # green
    '#06b6d4',  # cyan
]


class BoardForm(FlaskForm):
    name = StringField('Board name', validators=[DataRequired(), Length(min=1, max=150)])
    color = StringField('Color', validators=[DataRequired()])
    submit = SubmitField('Create board')


class ItemForm(FlaskForm):
    name = StringField('Item name', validators=[DataRequired(), Length(min=1, max=300)])
    submit = SubmitField('Add')
