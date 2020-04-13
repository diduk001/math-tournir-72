# Файл, содержащий функции для работы с базами данных

from data import db_session, users_login_data, users_members_data
from forms import check_type
from user import User

# Назначение классов для того, чтобы не писать длинные пути

UserLoginData = users_login_data.UserLoginData
UserMemberData = users_members_data.UserMembersData


# Функция добавления пользователя в базы данных
# На вход принимается user - объект класса User из модуля
def add_user(user):
    # Проверка типа аргумента
    check_type("user", user, User)

    # Заполнение данных для входа

    login_data = users_login_data.UserLoginData()

    login_data.login = user.login
    login_data.hashed_password = user.hashed_password

    # Заполнение данных о составе

    member_data = users_members_data.UserMembersData()

    member_data.team_name = user.team_name
    member_data.grade = user.grade

    member_data.member1_name, member_data.member1_surname, member_data.member1_school = user.member1
    member_data.member2_name, member_data.member2_surname, member_data.member2_school = user.member2
    member_data.member3_name, member_data.member3_surname, member_data.member3_school = user.member3
    member_data.member4_name, member_data.member4_surname, member_data.member4_school = user.member4

    session = db_session.create_session()
    session.add(login_data)
    session.commit()
    session.add(member_data)
    session.commit()


# Функця для изменения записи
# user_id - int, id пользователя
# users_login_table - bool, если True,то данные изменяются в таблицу users_login_data,
# иначе в таблицу users_members_data
# verbose - bool, выводить ли ошибку (если она будет)
# kwargs - именованные аргументы, те значения, которые нужно изменить
def change_val(user_id, users_login_table, verbose=False, **kwargs):
    session = db_session.create_session()
    if users_login_table:
        user = session.query(UserLoginData).filter(UserLoginData.id == user_id).first()
        for key, val in kwargs:
            try:
                user.key = val
                session.commit()
            except Exception as e:
                if verbose:
                    print(e)
            else:
                if verbose:
                    print(f"SUCCESS UserLoginData.{key}={val}")
    else:
        user = session.query(UserMemberData).filter(UserMemberData.id == user_id).first()
        for key, val in kwargs:
            try:
                user.key = val
                session.commit()
            except Exception as e:
                if verbose:
                    print(e)
            else:
                if verbose:
                    print(f"SUCCESS UserLoginData.{key}={val}")
    if verbose:
        print("END")
    return


# Функция проверки логина на уникальность
# Если логин существует в базе, возвращаем False
def check_login(login):
    session = db_session.create_session()
    return session.query(UserLoginData).filter(UserLoginData.login == login).first()
