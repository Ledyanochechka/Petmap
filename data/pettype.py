import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class PetType(SqlAlchemyBase):
    __tablename__ = 'pet_type'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    pet = orm.relationship("Pet", back_populates='pet_type')
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)