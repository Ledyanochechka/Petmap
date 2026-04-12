from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class PetForm(FlaskForm):
    name = StringField('Имя питомца', validators=[DataRequired()])
    pet_type = StringField('Порода/Тип', validators=[DataRequired()])
    submit = SubmitField('Сохранить питомца')