from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, ValidationError

class RegisterForm(FlaskForm):
    login = StringField('Имя пользователя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, field):
        allowed_domains = ["gmail.com", "yandex.ru", "mail.ru"]
        try:
            domain = field.data.split("@")[1]
        except IndexError:
            raise ValidationError("Неверный формат ввода почты, убедитесь в правильности написания.")

        if domain not in allowed_domains:
            raise ValidationError("Неверный формат ввода почты, убедитесь в правильности написания.")