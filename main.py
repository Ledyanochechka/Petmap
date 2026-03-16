from flask import Flask, render_template, redirect
from data import db_session
from forms.register_form import RegisterForm
from data.person import Person

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Bogdan_Lox'


def main():
    db_session.global_init("db/main_db.db")
    app.run()


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                'register.html',
                title='Регистрация',
                form=form,
                message="Пароли не совпадают"
            )

        db_sess = db_session.create_session()

        existing_user = db_sess.query(Person).filter(Person.email == form.email.data).first()
        if existing_user:
            return render_template(
                'register.html',
                title='Регистрация',
                form=form,
                message="Такой пользователь уже есть"
            )

        person = Person(
            name=form.login.data,
            email=form.email.data
        )
        person.set_password(form.password.data)

        db_sess.add(person)
        db_sess.commit()

        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


if __name__ == '__main__':
    main()