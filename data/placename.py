import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class PlaceName(SqlAlchemyBase):
    __tablename__ = 'place_name'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    place = orm.relationship("Place", back_populates='place_name')
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)