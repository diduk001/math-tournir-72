import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class UserMembersData(SqlAlchemyBase):
    __tablename__ = 'users-members-data'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    team_name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    grade = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    member1_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    member1_surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    member1_school = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    member2_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    member2_surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    member2_school = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    member3_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    member3_surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    member3_school = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    member4_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    member4_surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    member4_school = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users_login_data.id"))

    user = orm.relation('UserLoginData')

    is_authenticated = True
