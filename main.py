from flask import Flask, render_template, redirect, request, session, jsonify, url_for
import os
import requests
import uuid
import urllib.parse
from data import db_session
from forms.register_form import RegisterForm
from data.pet import Pet
from data.person import Person
from data.pettype import PetType
from data.petperson import PetPerson
from forms.pet_form import PetForm
from data.place import Place
from data.placeperson import PlacePerson
from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Bogdan_Lox'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'pets')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['AVATAR_FOLDER'] = os.path.join('static', 'uploads', 'avatars')
os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def main():
    db_session.global_init("db/main_db.db")
    #app.run()
    serve(app, host='0.0.0.0', port=5000)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    if 'user_id' not in session:
        return redirect('/login')

    db_sess = db_session.create_session()
    person = db_sess.query(Person).get(session['user_id'])

    return render_template("map.html",
                           yandex_api_key="ce4a66e0-6376-464a-8cfa-1c686e8a4299",
                           person=person)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    db_sess = db_session.create_session()
    person = db_sess.query(Person).filter(Person.id == session['user_id']).first()

    pets = []
    fav_places = []
    user_city = "неизвестно"

    if person:
        if person.address and person.address != "не указан":
            parts = [p.strip() for p in person.address.split(',')]
            if "обл." in parts[1] or "автономный" in parts[1].lower():
                user_city = parts[2] if len(parts) > 2 else parts[1]
            else:
                user_city = parts[0]
        else:
            user_city = "неизвестно"
        relations = db_sess.query(PetPerson).filter(PetPerson.id_person == person.id).all()
        pet_ids = [rel.id_animal for rel in relations]
        pets = db_sess.query(Pet).filter(Pet.id.in_(pet_ids)).all()

        raw_places = db_sess.query(Place).join(PlacePerson).filter(
            PlacePerson.id_person == person.id
        ).all()

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

                response = requests.get(
                    "https://geocode-maps.yandex.ru/1.x/",
                    params=params
                )

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

    return render_template(
        'profile.html',
        pets=pets,
        person=person,
        fav_places=fav_places,
        user_city=user_city
    )


@app.route('/api/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    file = request.files.get('avatar')
    if file and allowed_file(file.filename):
        db_sess = db_session.create_session()
        user = db_sess.query(Person).get(session['user_id'])
        _, ext = os.path.splitext(file.filename)
        filename = f"avatar_{user.id}_{uuid.uuid4().hex}{ext.lower()}"
        file.save(os.path.join(app.config['AVATAR_FOLDER'], filename))
        user.avatar = filename
        db_sess.commit()

        return jsonify({"status": "ok", "url": url_for('static', filename='uploads/avatars/' + filename)})

    return jsonify({"status": "error", "message": "Invalid file"}), 400

@app.route('/api/save_user_address', methods=['POST'])
def save_user_address():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    address = data.get('address')

    db_sess = db_session.create_session()
    user = db_sess.query(Person).get(session['user_id'])

    if user:
        user.address = address
        db_sess.commit()
        return jsonify({"status": "ok"})
    return jsonify({"error": "User not found"}), 404


@app.route('/new_pet', methods=['GET', 'POST'])
def new_pet():
    if 'user_id' not in session:
        return redirect('/login')

    db_sess = db_session.create_session()
    all_types = db_sess.query(PetType).all()

    form = PetForm()
    form.pet_type.choices = [(t.id, t.name) for t in all_types]

    if form.validate_on_submit():
        type_id = form.pet_type.data
        pet_type = db_sess.query(PetType).filter(PetType.id == type_id).first()

        if not pet_type:
            return render_template(
                'new_pet.html',
                form=form,
                message="Выбранный тип не найден"
            )

        photo = request.files.get('photo')
        photo_filename = None

        if photo and photo.filename:
            if allowed_file(photo.filename):
                _, ext = os.path.splitext(photo.filename)
                photo_filename = f"{uuid.uuid4().hex}{ext.lower()}"
                path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
                photo.seek(0)
                photo.save(path)
            else:
                return render_template(
                    'new_pet.html',
                    form=form,
                    message='Можно загружать только изображения: png, jpg, jpeg, gif, webp'
                )

        new_pet_obj = Pet(
            name=form.name.data,
            type_id=pet_type.id,
            breed=form.breed.data,
            photo=photo_filename
        )

        db_sess.add(new_pet_obj)
        db_sess.flush()

        relation = PetPerson(
            id_animal=new_pet_obj.id,
            id_person=session['user_id']
        )

        db_sess.add(relation)
        db_sess.commit()

        return redirect('/profile')

    return render_template('new_pet.html', form=form, pet=None)


@app.route('/delete_pet/<int:id>', methods=['POST'])
def delete_pet(id):
    if 'user_id' not in session:
        return redirect('/login')

    db_sess = db_session.create_session()
    pet = db_sess.query(Pet).filter(Pet.id == id).first()

    if pet:
        db_sess.query(PetPerson).filter(PetPerson.id_animal == id).delete()
        db_sess.delete(pet)
        db_sess.commit()

    return redirect('/profile')


@app.route('/edit_pet/<int:id>', methods=['GET', 'POST'])
def edit_pet(id):
    if 'user_id' not in session:
        return redirect('/login')

    db_sess = db_session.create_session()
    pet = db_sess.query(Pet).filter(Pet.id == id).first()

    if not pet:
        return redirect('/profile')

    all_types = db_sess.query(PetType).all()
    form = PetForm()
    form.pet_type.choices = [(t.id, t.name) for t in all_types]

    if request.method == "GET":
        form.name.data = pet.name
        form.breed.data = pet.breed
        form.pet_type.data = int(pet.type_id)

        for choice in form.pet_type.choices:
            if choice[0] == int(pet.type_id):
                form.pet_type.process_data(choice[0])
                break

    if form.validate_on_submit():
        pet.name = form.name.data
        pet.breed = form.breed.data
        pet.type_id = form.pet_type.data

        photo = request.files.get('photo')
        if photo and photo.filename:
            _, ext = os.path.splitext(photo.filename)
            filename = f"{uuid.uuid4().hex}{ext.lower()}"
            photo.seek(0)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pet.photo = filename

        db_sess.commit()
        return redirect('/profile')

    return render_template('new_pet.html', form=form, pet=pet)



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

    place = db_sess.query(Place).filter(
        Place.coordinates == coords
    ).first()

    if not place and request.method == 'POST':
        place = Place(
            name=request.json.get('name', 'Метка'),
            coordinates=coords
        )
        db_sess.add(place)
        db_sess.flush()

    fav = None

    if place:
        fav = db_sess.query(PlacePerson).filter(
            PlacePerson.id_place == place.id,
            PlacePerson.id_person == session['user_id']
        ).first()

    if request.method == 'POST':
        if fav:
            db_sess.delete(fav)
            res = {
                "action": "removed",
                "is_fav": False
            }
        else:
            db_sess.add(
                PlacePerson(
                    id_place=place.id,
                    id_person=session['user_id']
                )
            )
            res = {
                "action": "added",
                "is_fav": True
            }

        db_sess.commit()
        return jsonify(res)

    return jsonify({"is_fav": bool(fav)})


@app.route('/api/get_favorites')
def get_favorites():
    if 'user_id' not in session:
        return jsonify([])

    db_sess = db_session.create_session()

    places = db_sess.query(Place).join(
        PlacePerson
    ).filter(
        PlacePerson.id_person == session['user_id']
    ).all()

    return jsonify([
        {
            "lat": float(p.coordinates.split(',')[0]),
            "lon": float(p.coordinates.split(',')[1]),
            "name": p.name
        }
        for p in places
    ])

@app.route('/api/save_favorites', methods=['POST'])
def save_favorites():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    db_sess = db_session.create_session()
    data = request.json
    markers = data.get('markers', [])
    added_count = 0

    for m in markers:
        lat = m.get('lat')
        lon = m.get('lon')
        name = m.get('name', 'Избранное место')
        coords = f"{lat}, {lon}"
        place = db_sess.query(Place).filter(Place.coordinates == coords).first()
        if not place:
            place = Place(name=name, coordinates=coords)
            db_sess.add(place)
            db_sess.flush()
        existing_fav = db_sess.query(PlacePerson).filter(
            PlacePerson.id_place == place.id,
            PlacePerson.id_person == session['user_id']
        ).first()

        if not existing_fav:
            new_fav = PlacePerson(id_place=place.id, id_person=session['user_id'])
            db_sess.add(new_fav)
            added_count += 1

    db_sess.commit()
    return jsonify({"status": "success", "added_count": added_count})


@app.route('/remove_favorite/<int:id>', methods=['POST'])
def remove_favorite(id):
    if 'user_id' not in session:
        return redirect('/login')

    db_sess = db_session.create_session()
    fav = db_sess.query(PlacePerson).filter(
        PlacePerson.id_place == id,
        PlacePerson.id_person == session['user_id']
    ).first()

    if fav:
        db_sess.delete(fav)
        db_sess.commit()

    return redirect('/profile')


@app.route('/api/get_pois')
def get_pois():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    text_query = "зоотовары | ветеринарные услуги | площадка для собак"

    encoded_query = urllib.parse.quote(text_query)
    search_api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    url = f"https://search-maps.yandex.ru/v1/?text={encoded_query}&ll={lon},{lat}&spn=0.2,0.2&lang=ru_RU&apikey={search_api_key}&results=100"

    try:
        response = requests.get(url)
        data = response.json()
        results = []

        if 'features' in data:
            for feat in data['features']:
                meta = feat.get('properties', {}).get('CompanyMetaData', {})
                cats = [c['name'] for c in meta.get('Categories', [])]

                results.append({
                    'lat': feat['geometry']['coordinates'][1],
                    'lon': feat['geometry']['coordinates'][0],
                    'name': meta.get('name', 'Без названия'),
                    'category': cats[0] if cats else 'Зоо'
                })

        print(f"Поиск в центре: {lat}, {lon}. Найдено объектов: {len(results)}")
        return jsonify(results)
    except Exception as e:
        return jsonify([])
if __name__ == '__main__':
    main()