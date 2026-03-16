import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class PlacePerson(SqlAlchemyBase):
    __tablename__ = 'place_person'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    id_place = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("place.id"))
    place = orm.relationship('Place', back_populates='place_person')

    id_person = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("person.id"))
    person = orm.relationship('Person', back_populates='place_person')