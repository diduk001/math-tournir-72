import sqlalchemy
from sqlalchemy import orm

class GamesToUsers():
    __tablename__ = 'games_to_users'
    game = sqlalchemy.Column('games', sqlalchemy.Integer, sqlalchemy.ForeignKey('games.id'))
    user = sqlalchemy.Column('users', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
