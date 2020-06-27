import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


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
    # user_id, права, команды, в которых состоит, команды, в которые приглашён,
    # потверждена ли почта, заблокирован ли соответсвенно
    user_id = orm.relation("UserMembersData", back_populates='user')
    rights = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='user')
    checking = orm.relation('Game',
                            secondary='games_to_users')
    authoring = orm.relation('Game',
                             secondary='games_to_users')
    teams = sqlalchemy.Column(sqlalchemy.Text, nullable=True, default='')
    invitation = sqlalchemy.Column(sqlalchemy.Text, nullabe=True, default='')
    is_approved = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
    is_banned = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=True)
    is_authenticated = True

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def set_email(self, email):
        self.email = email
        self.hashed_email = generate_password_hash(email)
