from flask import Flask, render_template, redirect, request, session
from data import db_session
from forms.register_form import RegisterForm
from data.pet import Pet
from data.person import Person
from data.pettype import PetType
from data.petperson import PetPerson
from forms.pet_form import PetForm

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

        session['user_id'] = person.id
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
    return render_template("map.html", yandex_api_key="ce4a66e0-6376-464a-8cfa-1c686e8a4299")


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')  # Если нет, отправляем логиниться

    db_sess = db_session.create_session()
    person = db_sess.query(Person).filter(Person.id == session['user_id']).first()
    pets = []
    if person:
        relations = db_sess.query(PetPerson).filter(PetPerson.id_person == person.id).all()
        pet_ids = [rel.id_animal for rel in relations]
        pets = db_sess.query(Pet).filter(Pet.id.in_(pet_ids)).all()

    return render_template('profile.html', pets=pets, person=person)


@app.route('/new_pet', methods=['GET', 'POST'])
def new_pet():
    if 'user_id' not in session:
        return redirect('/login')

    form = PetForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        type_name = form.pet_type.data.strip()
        pet_type = db_sess.query(PetType).filter(PetType.name == type_name).first()

        if not pet_type:
            pet_type = PetType(name=type_name)
            db_sess.add(pet_type)
            db_sess.flush()
        new_pet_obj = Pet(
            name=form.name.data,
            type_id=pet_type.id
        )
        db_sess.add(new_pet_obj)
        db_sess.flush()

        relation = PetPerson(
            id_animal=new_pet_obj.id,
            id_person=session['user_id']
        )
        db_sess.add(relation)

        db_sess.commit()  # Сохраняем всё в БД
        return redirect('/profile')

    return render_template('new_pet.html', form=form)


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
