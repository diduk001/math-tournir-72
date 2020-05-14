import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class UserLoginData(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users_login_data'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, index=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = orm.relation("UserMembersData", back_populates='user')

    email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_approved = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)

    is_banned = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)

    is_authenticated = True

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def set_email(self, email):
        self.email = email
        self.hashed_email = generate_password_hash(email)
