from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class PetForm(FlaskForm):
    name = StringField('Имя питомца', validators=[DataRequired()])
    pet_type = SelectField(
        'Вид питомца',
        choices=[
            ('Собака', 'Собака'),
            ('Кошка', 'Кошка')
        ],
        validators=[DataRequired()]
    )
    breed = StringField('Порода')
    submit = SubmitField('Сохранить')