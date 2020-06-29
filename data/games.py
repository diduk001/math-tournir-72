import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

games_to_users = sqlalchemy.Table('games_to_users', SqlAlchemyBase.metadata,
    sqlalchemy.Column('games', sqlalchemy.Integer, sqlalchemy.ForeignKey('games.id')),
   sqlalchemy.Column('users', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
)

class Game(SqlAlchemyBase):
    __tablename__ = 'games'
    # id игры
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # Название, класс, тип игры(домино, пенальти и т.п., время начала, время конца, формат(командная/личная),
    # приватность(закрытая/открытая), информация об игре, количество задач, максимальный размер команды,
    # минимальный размер команды, путь к файлу с решениями, id авторов и проверяющих соответсвенно
    title = sqlalchemy.Column(sqlalchemy.String)
    grade = sqlalchemy.Column(sqlalchemy.Integer)
    type = sqlalchemy.Column(sqlalchemy.String)
    start_time = sqlalchemy.Column(sqlalchemy.String)
    end_time = sqlalchemy.Column(sqlalchemy.String)
    format = sqlalchemy.Column(sqlalchemy.String)
    privacy = sqlalchemy.Column(sqlalchemy.String)
    info = sqlalchemy.Column(sqlalchemy.Text)
    tasks_number = sqlalchemy.Column(sqlalchemy.Integer)
    sets_number = sqlalchemy.Column(sqlalchemy.Integer)
    min_team_size = sqlalchemy.Column(sqlalchemy.Integer)
    max_team_size = sqlalchemy.Column(sqlalchemy.Integer)
    solutions = sqlalchemy.Column(sqlalchemy.String)
    authors = orm.relation("User", secondary='games_to_users')
    checkers = orm.relation("User", secondary='games_to_users')