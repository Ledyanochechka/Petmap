from flask import Flask, render_template, redirect, request
from d import db_session
from forms.reset_passw import ResetForm
from forms.register_form import RegisterForm
from d.person import Person

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
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db_sess = db_session.create_session()

        person = db_sess.query(Person).filter(Person.email == email).first()

        if not person:
            return render_template("login.html", message="Пользователь не найден")

        if not person.check_password(password):
            return render_template("login.html", message="Неверный пароль")

        return redirect('/map')

    return render_template("login.html")

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        new_password_again = request.form['new_password_again']

        if new_password != new_password_again:
            return render_template('reset.html', message="Пароли не совпадают")

        db_sess = db_session.create_session()
        person = db_sess.query(Person).filter(Person.email == email).first()

        if not person:
            return render_template('reset.html', message="Пользователь не найден")

        person.set_password(new_password)
        db_sess.commit()

        return render_template('reset.html', message="Пароль успешно изменён")

    return render_template('reset.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/new_pet')
def new_pet():
    return render_template('new_pet.html')


@app.route('/edit_pet')
def edit_pet():
    return render_template('edit_pet.html')

@app.route('/')
def index():
    return redirect('/login')


@app.route('/edit_prof')
def edit_prof():
    return render_template('edit_prof.html')



if __name__ == '__main__':
    main()