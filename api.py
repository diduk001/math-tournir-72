from flask import Blueprint, request, jsonify
import os.path
import db_interface

blueprint = Blueprint('tasks_api', __name__, template_folder='templates')

# Ключ для API

TOTALLY_RIGHT_APIKEY = "01a2f11083248dd087f371518c37a0be2e340abe62c61dc5fcccd1dab1539fe0"

# Кортежи, в которых указаны валидные данные

VALID_REQUEST_TYPES = ("check_task", "get_task", "add_task")
VALID_GAME_TYPES = ("domino", "penalty")
VALID_GRADES = (5, 6, 7)
VALID_PENALTY_TASKS_NUMBERS = tuple([str(i) for i in range(1, 15)])
VALID_DOMINO_TASKS_NUMBERS = tuple([f"{i}-{j}" for i in range(7) for j in range(i, 7)])

# База данных с условиями и ответами

TASKS_INFO_DATABASE = os.path.join("db", "tasks_info.db")


@blueprint.route('/api')
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
        return jsonify({'error': 'Wrong task number. Must be i where 1 <= i <= 14'})

    if request_type == "check_task":
        answer = request.args.get("answer", default='', type=str)
        return check_task(game_type, grade, task, answer)

    if request_type == "get_task":
        return get_task(game_type, grade, task)

    if request_type == "add_task":
        answer = request.args.get("answer", default='', type=str)
        info = request.args.get("info", default='', type=str)
        return add_task(game_type, grade, task, answer, info)


# Проверка ответа

def check_task(game_type, grade, task, user_answer):
    """
    Проверить ответ на задачу
    :param game_type: str, Тип игры (domino/penalty)
    :param grade: str/int, Параллель, для которой добавляется задача
    :param task: str/int, Номер задачи в соответствии с типом игры
    :param user_answer: str, Ответ пользователя
    :return: True или False
    """
    table = f"{game_type}_{grade}_info"
    condition = f"task={task}"
    correct_answer = db_interface.get_data(TASKS_INFO_DATABASE, table, "answer", condition)
    return hash(user_answer) == correct_answer


# Вернуть условие задачи

def get_task(game_type, grade, task):
    """
    Возвращение условия задачи по типу игры, классу, номеру задачи
    :param game_type: str, Тип игры (domino/penalty)
    :param grade: str/int, Параллель, для которой добавляется задача
    :param task: str/int, Номер задачи в соответствии с типом игры
    :return: str, Условие ззадачи
    """
    table = f"{game_type}_{grade}_info"
    condition = f"task={task}"
    info = db_interface.get_data(TASKS_INFO_DATABASE, table, "info", condition)
    return info


def add_task(game_type, grade, task, ans, info):
    """
    Добавление условия для задачи
    :param game_type: str, Тип игры (domino/penalty)
    :param grade: str/int, Параллель, для которой добавляется задача
    :param task: str/int, Номер задачи в соответствии с типом игры
    :param ans: str, Правильный ответ
    :param info: str, Условие
    :return: None
    """
    table = f"{game_type}_{grade}_info"

    if db_interface.data_exists(TASKS_INFO_DATABASE, table, "task", task):
        db_interface.update_data(TASKS_INFO_DATABASE, table, {"answer": ans, "info": info},
                                 f"task={task}")
    else:
        db_interface.insert_data(TASKS_INFO_DATABASE, table, ("task", "answer", "info"),
                                 (task, hash(ans), info))


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
            sql_request = f"CREATE TABLE IF NOT EXISTS {table_name} ("
            sql_request += "task text PRIMARY KEY,"  # Номер задачи
            sql_request += "answer text,"  # Хэшированный ответ
            sql_request += "info text);"  # Условие
            db_interface.execute(TASKS_INFO_DATABASE, sql_request)


if __name__ == '__main__':
    setup()
