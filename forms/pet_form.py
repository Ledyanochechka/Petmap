from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class PetForm(FlaskForm):
    name = StringField('Имя питомца', validators=[DataRequired()])
    pet_type = SelectField('Тип питомца', coerce=int, validators=[DataRequired()])
    breed = StringField('Порода')
    submit = SubmitField('Сохранить питомца')