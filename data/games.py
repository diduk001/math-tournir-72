import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

class Game(SqlAlchemyBase):
    __tablename__ = 'games'
    # id игры
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # Название, класс, тип игры(домино, пенальти и т.п., время начала, время конца, формат(командная/личная),
    # приватность(закрытая/открытая), информация об игре, количество задач, максимальный размер команды,
    # минимальный размер команды, путь к файлу с решениями, id авторов и проверяющих соответсвенно
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    grade = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    start_time = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    end_time = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    format = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    privacy = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    info = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    task_number = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    sets_number = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    min_team_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    max_team_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    solutions = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    authors = sqlalchemy.Column("User", secondary='games_to_users')
    checkers = orm.relation("User",
                            secondary='games_to_users')