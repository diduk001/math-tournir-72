# Файл, содержащий функции для работы с базами данных

import sqlite3
from sqlite3 import Error

from config import User
from config import check_type
from data import db_session, users_login_data, users_members_data

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

    login_data.email = user.email
    login_data.hashed_email = user.email

    login_data.is_approved = user.is_approved
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
    if verbose:
        print("END")
    return


# Функция проверки логина на уникальность
# Если логин существует в базе, возвращаем False

def check_login(login):
    session = db_session.create_session()
    return session.query(UserLoginData).filter(UserLoginData.login == login).first()


def get_user_from_id(user_id):
    session = db_session.create_session()
    login_data = session.query(UserLoginData).get(user_id)
    members_data = session.query(UserMemberData).get(user_id)
    user = User(login_data.login,
                login_data.email,
                members_data.team_name,
                members_data.grade,

                (members_data.member1_name,
                 members_data.member1_surname,
                 members_data.member1_school),

                (members_data.member2_name,
                 members_data.member2_surname,
                 members_data.member2_school),

                (members_data.member3_name,
                 members_data.member3_surname,
                 members_data.member3_school),

                (members_data.member4_name,
                 members_data.member4_surname,
                 members_data.member4_school))

    user.id = login_data.id
    user.hashed_password = login_data.hashed_password

    return user


def create_connection(db_file):
    """
    Создать подключение к файлу базы данных
    :param db_file: str, Путь к файлу базы данных
    :return: Connection object/None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print("Creating connection SQL Error:", e)

    return None


def execute(db_file, request):
    """
    Выполнить запрос к таблице
    :param db_file: str, Путь к файлу базы данных
    :param request: str, Запрос к файлу в синтаксисе SQLite
    :return: None
    """
    conn = create_connection(db_file)
    try:
        c = conn.cursor()
        c.execute(request)
    except Error as e:
        print("Executing command SQL Error:", e)
        print(request)
    finally:
        conn.commit()
        conn.close()


def get_data(db_file, table, condition_col, condition_val):
    """
    Получить значение из столбца
    :param db_file: str, Путь к файлу базы данных
    :param table: str, Название таблицы
    :param condition_col: str, Столбец, по которому ищем строку
    :param condition_val: Значение, по которому ищем строку
    :return: tuple, Кортеж со строкой, для которой выполняется условие
    """
    command = f"SELECT * FROM {table} WHERE {condition_col}=(?)"
    conn = create_connection(db_file)
    try:
        cur = conn.cursor()
        cur.execute(command, (condition_val,))
        row = cur.fetchone()
        return row
    except Error as e:
        print("Get Data SQL Error:", e)
        print(command)
    finally:
        conn.commit()
        conn.close()

    return None


def data_exists(db_file, table, col, value):
    """
    Проверка на то, существует ли значение в столбце
    :param db_file: str, Путь к файлу базы данных
    :param table: str, Название таблицы
    :param col: str, Столбец, значение в котором надо проверить
    :param value: Значение, существование которого можно проверить
    :return: True или False
    """
    data = get_data(db_file, table, col, value)
    return bool(data)


def update_data(db_file, table, columns, values, condition_col, condition_val):
    """
    Обновление существующих значений
    :param db_file: str, Путь к файлу базы данных
    :param table: str, Название таблицы
    :param columns: iterable, столбцы, значения в которых надо заменить
    :param values: iterable, значения, на которые надо заменить
    :param condition_col: str, Столбец, по которому нужно найти строку
    :param condition_val: Значение, по которому можно найти строку
    :return: None
    """

    command = f"UPDATE {table} SET {','.join([col + ' = ?' for col in columns])} WHERE " \
              f"{condition_col}=(?)"
    print(command)
    print(table)
    print(values)
    conn = create_connection(db_file)
    try:
        cur = conn.cursor()
        cur.execute(command, (*values, condition_val))
    except Error as e:
        print("Update Data SQL Error:", e)
        print(command)
    conn.commit()
    conn.close()


def insert_data(db_file, table, values):
    """
    Вставка строки в таблицы
    :param db_file: str, Путь к файлу базы данных
    :param table: str, Название таблицы
    :param values: iterable, Значения, которые надо вставить в соответствующие столбцы
    :return: None
    """

    command = f"INSERT INTO {table} VALUES ( {','.join(['?' for _ in range(len(values))])} )"
    conn = create_connection(db_file)
    try:
        cur = conn.cursor()
        cur.execute(command, values)
    except Error as e:
        print("Insert Data SQL Error:", e)
        print(command)
    finally:
        conn.commit()
        conn.close()

    return None
