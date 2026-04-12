from flask import Flask, render_template, redirect, request, session
import requests
from data import db_session
from flask import jsonify
from forms.register_form import RegisterForm
from data.pet import Pet
from data.person import Person
from data.pettype import PetType
from data.petperson import PetPerson
from forms.pet_form import PetForm
from data.place import Place
from data.placeperson import PlacePerson

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
        return redirect('/login')

    db_sess = db_session.create_session()
    person = db_sess.query(Person).filter(Person.id == session['user_id']).first()

    pets = []
    fav_places = []

    if person:
        relations = db_sess.query(PetPerson).filter(PetPerson.id_person == person.id).all()
        pet_ids = [rel.id_animal for rel in relations]
        pets = db_sess.query(Pet).filter(Pet.id.in_(pet_ids)).all()

        raw_places = db_sess.query(Place).join(PlacePerson).filter(PlacePerson.id_person == person.id).all()

        for p in raw_places:
            try:
                lat, lon = p.coordinates.split(',')
                formatted_coords = f"{lon.strip()},{lat.strip()}"

                params = {
                    "apikey": "ce4a66e0-6376-464a-8cfa-1c686e8a4299",
                    "geocode": formatted_coords,
                    "format": "json",
                    "results": 1
                }
                response = requests.get("https://geocode-maps.yandex.ru/1.x/", params=params)

                if response.ok:
                    data = response.json()
                    feature_member = data["response"]["GeoObjectCollection"]["featureMember"]
                    if feature_member:
                        p.address = feature_member[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
                    else:
                        p.address = "Адрес не найден"
                else:
                    p.address = f"Ошибка API: {response.status_code}"
            except Exception as e:
                print(f"Ошибка геокодинга: {e}")
                p.address = "Ошибка загрузки адреса"

            fav_places.append(p)

    return render_template('profile.html', pets=pets, person=person, fav_places=fav_places)
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


@app.route('/api/toggle_favorite', methods=['GET', 'POST'])
def handle_favorite():
    if 'user_id' not in session:
        return jsonify({"is_fav": False, "status": "error"}), 403

    db_sess = db_session.create_session()
    lat = request.args.get('lat') or request.json.get('lat')
    lon = request.args.get('lon') or request.json.get('lon')
    coords = f"{lat}, {lon}"
    place = db_sess.query(Place).filter(Place.coordinates == coords).first()
    if not place and request.method == 'POST':
        place = Place(name=request.json.get('name', 'Метка'), coordinates=coords)
        db_sess.add(place)
        db_sess.flush()

    fav = None
    if place:
        fav = db_sess.query(PlacePerson).filter(
            PlacePerson.id_place == place.id, PlacePerson.id_person == session['user_id']
        ).first()

    if request.method == 'POST':
        if fav:
            db_sess.delete(fav)
            res = {"action": "removed", "is_fav": False}
        else:
            db_sess.add(PlacePerson(id_place=place.id, id_person=session['user_id']))
            res = {"action": "added", "is_fav": True}
        db_sess.commit()
        return jsonify(res)

    return jsonify({"is_fav": bool(fav)})


@app.route('/api/get_favorites')
def get_favorites():
    if 'user_id' not in session:
        return jsonify([])

    db_sess = db_session.create_session()
    places = db_sess.query(Place).join(PlacePerson).filter(PlacePerson.id_person == session['user_id']).all()

    return jsonify([{
        "lat": float(p.coordinates.split(',')[0]),
        "lon": float(p.coordinates.split(',')[1]),
        "name": p.name
    } for p in places])


if __name__ == '__main__':
    main()
