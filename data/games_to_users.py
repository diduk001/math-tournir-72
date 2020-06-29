import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class GamesToUsers(SqlAlchemyBase):
    __tablename__ = 'games_to_users'
    id = sqlalchemy.Column()
    game = sqlalchemy.Column('games', sqlalchemy.Integer, sqlalchemy.ForeignKey('games.id'))
    user = sqlalchemy.Column('users', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
