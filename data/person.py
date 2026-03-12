import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Person(SqlAlchemyBase):
    __tablename__ = 'person'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    pet_person = orm.relationship("PetPerson", back_populates='person')
    place_person = orm.relationship("PlacePerson", back_populates='person')
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    region = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
