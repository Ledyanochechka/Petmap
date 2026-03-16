import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Place(SqlAlchemyBase):
    __tablename__ = 'place'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    place_person = orm.relationship("PlacePerson", back_populates='place')
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    coordinates = sqlalchemy.Column(sqlalchemy.Numeric, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey("place_name.id"))
    place_name = orm.relationship('PlaceName')