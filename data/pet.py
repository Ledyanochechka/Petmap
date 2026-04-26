import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Pet(SqlAlchemyBase):
    __tablename__ = 'pet'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    pet_person = orm.relationship("PetPerson", back_populates='pet')

    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    breed = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("pet_type.id"))
    photo = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    pet_type = orm.relationship('PetType', back_populates='pets')