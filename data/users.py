import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table(
                    'authors_to_games', SqlAlchemyBase.metadata,
                    sqlalchemy.Column('authoring_games', sqlalchemy.ForeignKey('games.id'), primary_key=True),
                    sqlalchemy.Column('authors', sqlalchemy.ForeignKey('users.id'), primary_key=True)
)

second_association_table = sqlalchemy.Table(
                    'checkers_to_games', SqlAlchemyBase.metadata,
                    sqlalchemy.Column('checking_games', sqlalchemy.ForeignKey('games.id'), primary_key=True),
                    sqlalchemy.Column('checkers', sqlalchemy.ForeignKey('users.id'), primary_key = True)
)


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    # id в бд
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, index=True)
    # Информация которую о себе вводит пользователь:
    # Имя, Фамилия, класс, школа, учителя математики, информация о себе, электонная почта, её хеш,
    # логин, хеш пароля соответсвенно
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    grade = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    school = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    teachers = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    info = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    hashed_email = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # Системная информация о пользователе:
    # права, команды, в которых состоит, команды, в которые приглашён,
    # потверждена ли почта, заблокирован ли соответсвенно
    rights = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='user')
    authoring = orm.relationship('Game',
                                 secondary='authors_to_games',
                                 backref="authoring_games")
    checkering = orm.relationship('Game', secondary='checkers_to_games',
                                  backref='checking_games')
    teams = sqlalchemy.Column(sqlalchemy.Text, default='')
    invitation = sqlalchemy.Column(sqlalchemy.Text, default='')
    is_approved = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_banned = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_authenticated = True

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def set_email(self, email):
        self.email = email
        self.hashed_email = generate_password_hash(email)

    def __init__(self, login, name, surname, grade, school, teachers, info):
        self.login = login
        self.name = name
        self.surname = surname
        self.grade = grade
        self.school = school
        self.teachers = teachers
        self.info = info