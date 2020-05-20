import os.path
from hashlib import md5

from flask import Blueprint, request, jsonify

import db_interface
from config import VALID_REQUEST_TYPES, VALID_GAME_TYPES, VALID_GRADES, \
    VALID_DOMINO_TASKS_NUMBERS, VALID_PENALTY_TASKS_NUMBERS

api_blueprint = Blueprint('api', __name__, template_folder='templates')

# Ключ для API

TOTALLY_RIGHT_APIKEY = "01a2f11083248dd087f371518c37a0be2e340abe62c61dc5fcccd1dab1539fe0"

# База данных с условиями и ответами

TASKS_INFO_DATABASE = os.path.join("db", "tasks_info.db")


@api_blueprint.route('/api')
def api():
    """
    Функция для обработки запросов с url параметрами
    :return: None
    """

    apikey = request.args.get("apikey", default='', type=str)
    if not check_apikey(apikey):
        return jsonify({'error': 'Wrong api key'})

    request_type = request.args.get("request_type", default='', type=str)
    if request_type not in VALID_REQUEST_TYPES:
        return jsonify({'error': f'Invalid request type. Must be in {VALID_REQUEST_TYPES}'})

    game_type = request.args.get("game_type", default='', type=str)
    if game_type not in VALID_GAME_TYPES:
        return jsonify({'error': f'Invalid game type. Must be in {VALID_GAME_TYPES}'})

    grade = request.args.get("grade", default=-1, type=int)
    if grade not in VALID_GRADES:
        return jsonify({'error': f'Invalid grade. Must be in {VALID_GRADES}'})

    task = request.args.get("task", default='', type=str)

    if game_type == "domino":
        if task not in VALID_DOMINO_TASKS_NUMBERS:
            return jsonify({'error': 'Wrong task number. Must be {i}-{j} where 0 <= i <= 6 and i '
                                     '<= j <= 6'})

    if game_type == "penalty":
        if task not in VALID_PENALTY_TASKS_NUMBERS:
            return jsonify({'error': 'Wrong task number. Must be i where 1 <= i <= 16'})

    if request_type == "check_task":
        answer = request.args.get("answer", default='', type=str)
        return check_task(game_type, grade, task, answer)

    if request_type == "get_task":
        return get_task(game_type, grade, task)

    if request_type == "add_task":
        answer = request.args.get("answer", default='', type=str)
        info = request.args.get("info", default='', type=str)
        manual_check = request.args.get("manual_check", default=False, type=bool)
        ans_picture = request.args.get("ans_picture", default=False, type=bool)
        return add_task(game_type, grade, task, answer, info, manual_check, ans_picture)


# Проверка ответа

def check_task(game_type, grade, task, user_answer):
    """
    Проверить ответ на задачу
    :param game_type: str, Тип игры (domino/penalty)
    :param grade: str/int, Параллель, для которой добавляется задача
    :param task: str/int, Номер задачи в соответствии с типом игры
    :param user_answer: str, Ответ пользователя
    :return: str, True или False
    """
    table = f"{game_type}_{grade}_info"
    correct_answer = db_interface.get_data(TASKS_INFO_DATABASE, table, "task", task)[1]
    return str(hash_md5(user_answer) in correct_answer)


# Вернуть условие задачи

def get_task(game_type, grade, task):
    """
    Возвращение условия задачи по типу игры, классу, номеру задачи
    :param game_type: str, Тип игры (domino/penalty)
    :param grade: str/int, Параллель, для которой добавляется задача
    :param task: str/int, Номер задачи в соответствии с типом игры
    :return: str, Условие задачи
    """
    table = f"{game_type}_{grade}_info"
    info = db_interface.get_data(TASKS_INFO_DATABASE, table, "task", task)[2]
    return info


def add_task(game_type, grade, task, ans, info, manual_check, ans_picture):
    """
    Добавление условия для задачи
    :param game_type: str, Тип игры (domino/penalty)
    :param grade: str/int, Параллель, для которой добавляется задача
    :param task: str/int, Номер задачи в соответствии с типом игры
    :param ans: str, Правильный ответ
    :param info: str, Условие
    :param manual_check: bool, Флаг ручной проверки
    :param ans_picture: bool, Флаг ответа-картинки
    :return: None
    """
    hashed_ans = ""
    for possible_ans in ans.split('!'):  # Перебираем возможные ответы
        hashed_ans += '|' + hash_md5(possible_ans) + '|'  # То, что хранится в табличке -
        # |md5(ans1)||md5(ans2)||...|

    table = f"{game_type}_{grade}_info"
    try:
        if db_interface.data_exists(TASKS_INFO_DATABASE, table, "task", task):
            db_interface.update_data(TASKS_INFO_DATABASE, table, ("answer", "info",
                                                                  "manual_check", "ans_picture"),
                                     (hashed_ans, info, manual_check, ans_picture), "task", task)
        else:
            db_interface.insert_data(TASKS_INFO_DATABASE, table, (task, hashed_ans, info,
                                                                  manual_check, ans_picture))
    except Exception as e:
        return jsonify({"error": str(e)})
    return "ok!"


def check_apikey(apikey):
    """
    Проверка ключа apikey на правильность
    :param apikey: str, предложенный ключ
    :return: True или False
    """
    return apikey == TOTALLY_RIGHT_APIKEY


def setup():
    """
    Наполнение базы данных таблицами со стоблцами task, answer, text
    :return: None
    """

    for game_type in VALID_GAME_TYPES:
        for grade in VALID_GRADES:
            table_name = f"{game_type}_{grade}_info"
            sql_request_delete = f"DROP TABLE IF EXISTS {table_name}"
            db_interface.execute(TASKS_INFO_DATABASE, sql_request_delete)

            sql_request = f"CREATE TABLE IF NOT EXISTS {table_name} ("
            sql_request += "task TEXT PRIMARY KEY,"  # Номер задачи
            sql_request += "answer TEXT,"  # Хэшированный ответ
            sql_request += "info TEXT,"  # Условие
            sql_request += "manual_check BOOLEAN,"  # Флаг ручной проверки
            sql_request += "ans_picture BOOLEAN"  # Флаг сдачи ответа в виде картинки
            sql_request += ");"  # Условие
            db_interface.execute(TASKS_INFO_DATABASE, sql_request)


# Функция хэширования

def hash_md5(s):
    h = md5(bytes(s, encoding="utf-8"))
    return h.hexdigest()


if __name__ == '__main__':
    setup()
