from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp


class StockSearchForm(FlaskForm):
    stockid = StringField('查询股票', validators = [
        DataRequired(), Regexp('^((sh6)|(sz3)|(sz0)){1}[0-9]{5}$', 0, '再检查一下股票代码')])
    submit = SubmitField('Search')


class EditProfileForm(FlaskForm):
    pass