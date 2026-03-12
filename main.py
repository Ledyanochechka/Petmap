from flask import Flask
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Bogdan_Lox'


def main():
    db_session.global_init("db/main_db.db")
    app.run()


if __name__ == '__main__':
    main()