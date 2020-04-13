import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class UserLoginData(SqlAlchemyBase):
    __tablename__ = 'users_login_data'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, index=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = orm.relation("UserMembersData", back_populates='user')
