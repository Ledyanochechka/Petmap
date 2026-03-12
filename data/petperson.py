import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class PetPerson(SqlAlchemyBase):
    __tablename__ = 'pet_person'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    id_animal = sqlalchemy.Column(sqlalchemy.Integer,
                           sqlalchemy.ForeignKey("pet.id"))
    animal = orm.relationship('Pet')
    id_person = sqlalchemy.Column(sqlalchemy.Integer,
                           sqlalchemy.ForeignKey("person.id"))
    person = orm.relationship('Person')