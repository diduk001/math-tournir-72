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
    authors = orm.relation("User",
                           secondary='authors_to_games',
                           backref='authors')
    checkers = orm.relation("User",
                            secondary='checkers_to_games',
                            backref='checkers')

    def __init__(self, title, grade, game_type, start_time, end_time, format,  privacy, info, author,
                task_number, min_team_size, max_team_size, sets_number):
        self.title = title
        self.grade = grade
        self.type = game_type
        self.start_time = start_time
        self.end_time = end_time
        self.format = format
        self.privacy = privacy
        self.info = info
        self.authors.append(author)
        self.tasks_number = task_number
        self.min_team_size = min_team_size
        self.max_team_size = max_team_size
        self.sets_number = sets_number