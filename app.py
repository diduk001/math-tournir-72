import datetime
import json
import os
import os.path
from hashlib import md5

import requests
from flask import Flask, render_template, redirect, request, send_file
from flask_login import LoginManager, logout_user, login_required, login_user, current_user

from api import api_blueprint, TOTALLY_RIGHT_APIKEY, VALID_DOMINO_TASKS_NUMBERS, \
    VALID_PENALTY_TASKS_NUMBERS
from config import SERVER_URL, SignUpForm, LoginForm, ForgotPassword, AddTaskForm, BanTeamForm, \
    StartEndTimeForm, PardonTeamForm
from db_interface import *


# Класс конфигурации

class ConfigClass(object):
    SECRET_KEY = "0d645377e31ab6b5847ec817bac4aaf8"
    USER_ENABLE_EMAIL = False
    USER_ENABLE_USERNAME = True
    UPLOAD_FOLDER = ['.', 'static', 'img', 'uploads']


# Создание приложения

app = Flask(__name__)

# конфигурация
app.config.from_object(__name__ + '.ConfigClass')
db_session.global_init("db/login_data_members_data_session.sqlite")
app.register_blueprint(api_blueprint)

# Создание и инициализация менеджера входа

login_manager = LoginManager()
login_manager.init_app(app)

# set с допущенными расширениями

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', "gif"}


# Вызов обработчика базового шаблона base.html
# Это только для дебага, удалите в релизе

@app.route("/base")
@app.route("/base.html")
def base():
    params = dict()
    params["title"] = "base html"
    params["block"] = ""
    return render_template("base.html", **params)


# Главная страница

@app.route("/")
def index():
    params = dict()
    params["title"] = "ТЮМ 72"
    return render_template("index.html", **params)


# Вход и профиль (профиль открывается только тогда, когда пользователь авторизован)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    # Переменная для отладки, значения:
    # 0 - сценарий для релиза
    # 1 - открывает "Вход"
    # 2 - открывает "Профиль"

    debug_var = 0
    if debug_var == 0:
        if is_auth():
            # Если мы забанили команду
            if is_banned():
                return render_template("you_are_banned.html", title="Вас дисквалифицировали")

            return render_template("profile.html", **(get_cur_user().__dict__()))
        else:

            # Иначе переправляем на вход
            return redirect("/login")
    elif debug_var == 1:
        return redirect("/login")


# Страница для забывчивых

@app.route('/forgot_password', methods=['GET', 'POST'])
def recover_password():
    if request.method == "GET":
        form = ForgotPassword()
        params = dict()
        params["form"] = form
        return render_template("forgot_password.html", **params)
    else:
        email = request.form.get("email")
        return "иванован доделай это"

        # Тут иванован должен дописать


# Изменить состояние задачи

def update(table, task, state, team, grade):
    con = sqlite3.connect(os.path.join("db", "tasks.db"))
    cur = con.cursor()
    que = f"UPDATE {table + str(grade)}\n"
    que += f"SET {task} = '{state}'\n"
    que += f"WHERE title = '{team}'"
    cur.execute(que)
    con.commit()
    con.close()


# Получить состояние задачи

def get(table, task, team, grade):
    con = sqlite3.connect(os.path.join("db", "tasks.db"))
    cur = con.cursor()
    que = f"SELECT {task} FROM {table + str(grade)} WHERE title='{team}'"
    result = cur.execute(que).fetchone()[0]
    con.close()
    return result


# Изменить таблицу результатов
def update_results(table, points, team, grade):
    con = sqlite3.connect(os.path.join("db", "tasks.db"))
    cur = con.cursor()
    current = cur.execute(f"SELECT sum FROM {table + str(grade)} WHERE title='{team}'").fetchone()[0]
    que = f"UPDATE {table + str(grade)}\n"
    que += f"SET sum = '{current + int(points)}'\n"
    que += f"WHERE title = '{team}'"
    cur.execute(que)
    con.commit()
    con.close()


# Регистрация
@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    sign_up_form = SignUpForm()
    params = dict()
    params["title"] = "Регистрация"
    params["form"] = sign_up_form

    # Проверяем, правильно ли заполнена форма

    if sign_up_form.validate_on_submit():

        # Если мы нажали на кнопку "регистриция", то выходим из аккаунта
        if is_auth():
            logout_user()

            # Проверяем, не использован ли логин и пароль

        is_login_used = login_used(request.form.get("team-login"))
        is_team_name_used = team_name_used(request.form.get("team-team_name"))
        if is_team_name_used or is_login_used:
            if login_used:
                params["login_used"] = True

            if team_name_used:
                params["team_name_used"] = True

            return render_template("sign_up.html", **params)

        # Создания объека User

        user = User(
            login=request.form.get("team-login"),
            team_name=request.form.get("team-team_name"),
            email=request.form.get("team-email"),
            grade=int(request.form.get("team-grade")),

            member1=(request.form.get("member1-name_field"),
                     request.form.get("member1-surname"),
                     request.form.get("member1-school")),

            member2=(request.form.get("member2-name_field"),
                     request.form.get("member2-surname"),
                     request.form.get("member2-school")),

            member3=(request.form.get("member3-name_field"),
                     request.form.get("member3-surname"),
                     request.form.get("member3-school")),

            member4=(request.form.get("member4-name_field"),
                     request.form.get("member4-surname"),
                     request.form.get("member4-school"))
        )

        user.set_password(request.form.get("team-password"))

        # Добавление пользователя в базы данных
        con = sqlite3.connect((os.path.join("db", "tasks.db")))
        cur = con.cursor()
        domino_table = 'domino_tasks' + str(user.grade)
        penalty_table = 'penalty_tasks' + str(user.grade)
        cur.execute(f"INSERT into {domino_table}(title) values (?)", (user.team_name,))
        cur.execute(f"INSERT into {penalty_table}(title) values (?)", (user.team_name,))
        con.commit()
        con.close()
        add_user(user)

        return redirect("/login")

    return render_template("sign_up.html", **params)


# Страница с правилами

@app.route('/rules')
def rules():
    params = dict()
    params["title"] = "Правила"
    return render_template("rules.html", **params)


# Допуск к кабинету админа

@app.route('/admin', methods=['GET', 'POST'])
def admin_pass():
    if request.method == "GET":
        return send_file("./templates/admin_pass.html")
    elif request.method == "POST":
        password = request.form.get("password")
        password = password.strip()
        if hash_md5(password) == "8d5a568735a2195fbdcd900507c48c6d":  # hash_md5(";353!tyum")
            return redirect("/52df6a777d579a6fc8b787b049824b41")
        return "Пароль неправильный! <br> <a " \
               "href=\"./21232f297a57a5a743894a0e4a801fc3\">Вернуться обратно</a>"


# Пункт управления для админов

@app.route('/52df6a777d579a6fc8b787b049824b41', methods=['GET'])
def admin_room():
    params = dict()
    params["add_task_form"] = AddTaskForm()
    params["start_end_time_form"] = StartEndTimeForm()
    params["ban_team_form"] = BanTeamForm()
    params["pardon_team_form"] = PardonTeamForm()
    return render_template("admin_room.html", **params)


# Страничка с результатом добавления задачи

@app.route('/cdb63e6a1a08307c6c44354aa37972b7', methods=['POST'])
def add_task():
    task = request.form.get("task")
    grade = request.form.get("grade")
    game_type = request.form.get("game_type")
    answer = request.form.get("answer")
    if game_type == "domino" and task not in VALID_DOMINO_TASKS_NUMBERS:
        return """номер задачи и тип игры не совпадают 
                  <a href="/52df6a777d579a6fc8b787b049824b41"> вернуться обратно</a>"""
    if game_type == "penalty" and task not in VALID_PENALTY_TASKS_NUMBERS:
        return """номер задачи и тип игры не совпадают
                  <a href="/52df6a777d579a6fc8b787b049824b41"> вернуться обратно</a>"""
    file = request.files.get('info')

    if file and allowed_file(file.filename):
        filename = task + '.' + get_extension(file.filename)
        file.save(os.path.join(*app.config['UPLOAD_FOLDER'], filename))
        info = os.path.join(*app.config['UPLOAD_FOLDER'], filename)
        url = SERVER_URL + '/api'
        params = {"apikey": TOTALLY_RIGHT_APIKEY,
                  "request_type": "add_task",
                  "game_type": game_type,
                  "grade": grade,
                  "task": task,
                  "answer": answer,
                  "info": info}
        print(url)
        r = requests.get(url, params=params)
        print(r.content)
        print(r.url)
        # print(requests.get(url, params=params))
        # print(requests.get(url, params=params).content)

        return """задача добавлена <a href="/52df6a777d579a6fc8b787b049824b41"> вернуться 
        обратно</a>"""
    else:
        return """файл не прошёл проверку <a href="/52df6a777d579a6fc8b787b049824b41">
                  вернуться обратно</a>"""


# Страничка с результатом изменением времени соревнований

@app.route('/8770a9a6c5ab1b00a4e0293d9ebd7bec', methods=['POST'])
def start_end_time():
    global domino_start_time, domino_end_time, penalty_start_time, penalty_end_time

    try:
        game_type = request.form.get("game_type")
        time_start = request.form.get("time_start")
        time_end = request.form.get("time_end")
        time_format = "%d.%m.%Y %H:%M:%S"
    except Exception as e:
        return "Произошла ошибка:  " + str(e) + """ <a href="/52df6a777d579a6fc8b787b049824b41">
                вернуться обратно</a>"""

    try:
        datetime_start = datetime.datetime.strptime(time_start, time_format)
        datetime_end = datetime.datetime.strptime(time_end, time_format)
    except ValueError:
        return """Время не соответствует формату <a href="/52df6a777d579a6fc8b787b049824b41"> 
                  вернуться обратно</a>"""

    if game_type == "domino":
        domino_start_time = datetime_start
        domino_end_time = datetime_end
    elif game_type == "penalty":
        penalty_start_time = datetime_start
        penalty_end_time = datetime_end

    return """Вы установили время и дату соревнования (если я не ошибся). <a href="/52df6a777d579a6fc8b787b049824b41"> вернуться 
        обратно</a>"""


# Страничка с результатом бана команды

@app.route('/1551c97a3794c5257e7ed3c5b816a825', methods=['POST'])
def ban_team():
    team_name = request.form.get("team_name")
    if not team_name_used(team_name):
        return f"""Команды {repr(team_name)} существует. Пожалуйста, проверьте, всё ли правильно вы
               ввели <a href="/52df6a777d579a6fc8b787b049824b41"> вернуться обратно</a>"""

    session = db_session.create_session()

    try:
        team_id = session.query(UserMemberData).filter(UserMemberData.team_name ==
                                                       team_name).first().id
        login_data = session.query(UserLoginData).filter(UserLoginData.id == team_id).first()
        login_data.is_banned = True
        session.commit()

        return f"""Команда {team_name} отправилась в бан <a 
                href="/52df6a777d579a6fc8b787b049824b41"> вернуться обратно</a>"""
    except Exception as e:
        return f"""Произошла ошибка: {e} \n <a href="/52df6a777d579a6fc8b787b049824b41"> 
                вернуться обратно</a>"""


# Прощение (ну то есть прощают типа как бан но наоборот)

@app.route('/7717fdf71bcc8418fb7fabcb5b9c46d2', methods=['POST'])
def pardon():
    team_name = request.form.get("team_name")
    if not team_name_used(team_name):
        return f"""Команды {repr(team_name)} существует. Пожалуйста, проверьте, всё ли правильно вы
                   ввели <a href="/52df6a777d579a6fc8b787b049824b41"> вернуться обратно</a>"""

    session = db_session.create_session()
    team_id = session.query(UserMemberData).filter(UserMemberData.team_name ==
                                                   team_name).first().id
    banned = session.query(UserLoginData).filter(UserLoginData.id == team_id).first().is_banned

    if not banned:
        return f"""Команда {repr(team_name)} не дисквалифицирована. 
                <a href="/52df6a777d579a6fc8b787b049824b41"> вернуться обратно</a>"""

    try:
        login_data = session.query(UserLoginData).filter(UserLoginData.id == team_id).first()
        login_data.is_banned = False
        session.commit()

        return f"""Команда {repr(team_name)} прощена. <a href="/52df6a777d579a6fc8b787b049824b41">
                вернуться обратно</a>"""
    except Exception as e:
        return f"""Произошла ошибка: {e} \n <a href="/52df6a777d579a6fc8b787b049824b41"> 
                        вернуться обратно</a>"""


# Функция хэширования

def hash_md5(s):
    h = md5(bytes(s, encoding="utf-8"))
    return h.hexdigest()


# всё что нужно для игр

def get_point(string):
    return string[:-2]


def get_state(string):
    return string[-2:]


# Всё что нужно для домино
domino_start_time = datetime.datetime(2020, 4, 19, 21, 14, 30)
domino_end_time = datetime.datetime(2020, 4, 19, 21, 15, 30)
domino_keys = list(map(str, range(1, 29)))
domino_tasks_names = {'0-0': '1', '0-1': '2', '0-2': '3', '0-3': '4', '0-4': '5', '0-5': '6',
                      '0-6': '7', '1-1': '8', '1-2': '9',
                      '1-3': '10', '1-4': '11', '1-5': '12', '1-6': '13', '2-2': '14', '2-3': '15',
                      '2-4': '16', '2-5': '17',
                      '2-6': '18', '3-3': '19', '3-4': '20', '3-5': '21', '3-6': '22', '4-4': '23',
                      '4-5': '24', '4-6': '25',
                      '5-5': '26', '5-6': '27', '6-6': '28'}
domino_messages = {'full': "Вы уже взяли 2 задачи", 'af': 'Вы уже решили эту задачу',
                   'as': 'Вы уже решили эту задачу',
                   'fs': 'У Вас закончились попытки на сдачу этой задачи',
                   'absent': 'На данный момент задачи с этим номером отсутсвуют',
                   'hand': 'Вы уже взяли эту задачу'}
with open("domino_tasks.json", 'rt') as f:
    domino_info = json.load(f)
number_of_domino_task = 5
for grade in ['5', '6', '7']:
    for key in domino_keys:
        domino_info[grade][key]['number'] = number_of_domino_task


# Страница домино

@app.route("/domino", methods=["GET", "POST"])
def domino():
    # Необходимые штуки
    global domino_keys, domino_messages, domino_tasks_names, domino_info

    # Если мы забанили команду

    if get_cur_user().is_banned:
        return render_template("you_are_banned.html", title="Вас дисквалифицировали")

    team = current_user.team_name
    grade = str(current_user.grade)
    time = datetime.datetime.now()
    if domino_start_time > time:
        start_time = f"{domino_start_time.month} {domino_start_time.day} {domino_start_time.year} "
        start_time += f"{domino_start_time.hour}:{domino_start_time.minute}:{domino_start_time.second}"
        return render_template("domino.html", title="Домино ТЮМ72", state='not started',
                               start_time=start_time)
    elif time > domino_end_time:
        return render_template("domino.html", title="Домино ТЮМ72", state='ended')
    else:
        end_time = f"{domino_end_time.month} {domino_end_time.day} {domino_end_time.year}"
        end_time += f"{domino_end_time.hour}:{domino_end_time.minute}:{domino_end_time.second}"
        state = 'in progress'
        tasks = {}
        for key in domino_keys:
            tasks[key] = {'name': domino_info[grade][key]['name'],
                          'state': get('domino_tasks', 't' + key, team, grade)}
        for key in domino_keys:
            if get_state(tasks[key]['state']) == 'ok' and domino_info[grade][key]['number'] == 0:
                tasks[key]['state'] = '0bo'
            elif get_state(tasks[key]['state']) == 'ff' and domino_info[grade][key]['number'] == 0:
                tasks[key]['state'] = '0bf'
            elif get_state(tasks[key]['state']) == 'bo' and domino_info[grade][key]['number'] > 0:
                tasks[key]['state'] = '0ok'
            elif get_state(tasks[key]['state']) == 'bf' and domino_info[grade][key]['number'] > 0:
                tasks[key]['state'] = '0ff'
        print(tasks)
        picked_tasks = get('domino_tasks', 'picked_tasks', team, grade).split()
        if request.method == "GET":
            return render_template("domino.html", title="Домино ТЮМ72", block="", tasks=tasks,
                                   keys=domino_keys,
                                   picked_tasks=picked_tasks, message=False, info=domino_info[grade],
                                   state=state, end_time=end_time)
        elif request.method == "POST":
            message = False
            if request.form.get("picked"):
                key = domino_tasks_names[request.form.get("picked")]
                number_of_picked_task = len(picked_tasks)
                if number_of_picked_task == 2:
                    message = domino_messages['full']
                elif 't' + key in picked_tasks:
                    message = domino_messages['hand']
                elif get_state(tasks[key]['state']) in ['ff', 'ok']:
                    picked_tasks.append('t' + key)
                    domino_info[grade][key]['number'] -= 1
                else:
                    message = domino_messages[get_state(tasks[key]['state'])]
            elif request.form.get('answer'):
                key = domino_tasks_names[request.form.get('name')]
                verdicts = ['ok', 'ff', 'fs']
                if domino_info[grade][key]['answer'] == request.form.get('answer') and get_state(
                        tasks[key]['state']) == 'ok':
                    tasks[key]['state'] = str(
                        sum(map(int, domino_info[grade][key]['name'].split('-')))) + 'af'
                elif domino_info[grade][key]['answer'] == request.form.get('answer'):
                    tasks[key]['state'] = str(
                        max(map(int, domino_info[grade][key]['name'].split('-')))) + 'as'
                else:
                    tasks[key]['state'] = verdicts[
                        verdicts.index(get_state(tasks[key]['state'])) + 1]
                    if tasks[key]['state'] == 'ff':
                        tasks[key]['state'] = '0ff'
                    else:
                        tasks[key]['state'] = str(
                            -min(map(int, domino_info[grade][key]['name'].split('-')))) + 'fs'
                update_results('domino_tasks', get_point(tasks[key]['state']), team, grade)
                picked_tasks.remove('t' + key)
                domino_info[grade][key]['number'] += 1
            update('domino_tasks', 'picked_tasks', " ".join(picked_tasks), team, grade)
            update('domino_tasks', 't' + key, tasks[key]['state'], team, grade)
            return render_template("domino.html", title="Домино ТЮМ72", block="", tasks=tasks,
                                   keys=domino_keys, picked_tasks=picked_tasks, message=message,
                                   info=domino_info[grade], state=state, end_time=end_time)


# Всё что нужно для пенальти

penalty_keys = list(map(str, range(1, 15)))
penalty_info = {}
penalty_start_time = datetime.datetime(2020, 4, 18, 12, 8, 30)
penalty_end_time = datetime.datetime(2020, 4, 18, 12, 9, 30)
for grade in ['5', '6', '7']:
    penalty_info[grade] = {}
    for key in penalty_keys:
        penalty_info[grade][key] = {'name': key, 'cost': 15, 'answer': '0',
                                    'content': '/static/img/sample1.png'}
penalty_messages = {'accepted': 'Вы уже решили эту задачу',
                    'failed': 'У вас закончились попытки на сдачу этой задачи'}


# Страница пенальти


@app.route('/penalty', methods=["GET", "POST"])
def penalty():
    global penalty_info

    # Если мы забанили команду

    if get_cur_user().is_banned:
        return render_template("you_are_banned.html", title="Вас дисквалифицровали")

    team = current_user.team_name
    grade = str(current_user.grade)
    time = datetime.datetime.now()
    if penalty_start_time > time:
        start_time = f"{penalty_start_time.month} {penalty_start_time.day} {penalty_start_time.year} "
        start_time += f"{penalty_start_time.hour}:{penalty_start_time.minute}:{penalty_start_time.second}"
        return render_template("penalty.html", title="Пенальти ТЮМ72", state='not started',
                               start_time=start_time)
    elif time > penalty_end_time:
        return render_template("penalty.html", title="Пенальти ТЮМ72", state='ended')
    else:
        end_time = f"{penalty_end_time.month} {penalty_end_time.day} {penalty_end_time.year} "
        end_time += f"{penalty_end_time.hour}:{penalty_end_time.minute}:{penalty_end_time.second}"
        state = 'in progress'
        tasks = {}
        for key in penalty_keys:
            tasks[key] = {'name': key, 'state': get('penalty_tasks', 't' + key, team, grade)}
        if request.method == "POST":
            key = request.form.get('name')
            verdicts = ['ok', 'ff', 'fs']
            if penalty_info[grade][key]['answer'] == request.form.get('answer'):
                if get_state(tasks[key]['state']) == 'ok':
                    tasks[key]['state'] = str(penalty_info[grade][key]['cost']) + 'af'
                    if penalty_info[grade][key]['cost'] > 5:
                        penalty_info[grade][key]['cost'] -= 1
                else:
                    tasks[key]['state'] = '3' + 'as'
            else:
                tasks[key]['state'] = verdicts[verdicts.index(get_state(tasks[key]['state'])) + 1]
                if tasks[key]['state'] == 'ff':
                    tasks[key]['state'] = '0' + 'ff'
                else:
                    tasks[key]['state'] = '-2' + 'fs'
            update_results('penalty_tasks', get_point(tasks[key]['state']), team, grade)
            update('penalty_tasks', 't' + key, tasks[key]['state'], team, grade)
        return render_template("penalty.html", title="Пенальти ТЮМ72", tasks=tasks,
                               keys=penalty_keys,
                               info=penalty_info[grade], state=state, end_time=end_time)


# Результаты

@app.route('/results/<game>/<grade>')
def results(game, grade):
    grade = str(grade)
    team = ''
    if is_auth() and str(current_user.grade) == str(grade):
        team = current_user.team_name
    titles = {'domino': 'Домино', 'penalty': 'Пенальти'}
    if game == 'domino':
        info = domino_info
        number = 28
        keys = domino_keys
    else:
        info = penalty_info
        number = 14
        keys = penalty_keys
    table = game + '_tasks' + str(grade)
    con = sqlite3.connect(os.path.join("db", "tasks.db"))
    cur = con.cursor()
    results = cur.execute(f"SELECT * from {table} ORDER BY sum").fetchall()
    con.close()
    team_num = len(results)
    return render_template("results.html", team=team, results=results, title=titles[game],
                           grade=grade,
                           info=info, number=number, team_num=team_num, keys=keys)


# Страница для авторизации

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    params = dict()
    params["title"] = "Вход"
    params["form"] = form
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(UserLoginData).filter(UserLoginData.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect("/")
        return render_template('login.html',
                               invalid_parameters=True,
                               form=form)
    return render_template("login.html", **params)


# Выход из аккаунта

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Функция загрузки данных пользователя из базы данных
# user_id - id команды
# login_data - bool, если True, то загружает данные авторизации, иначе данные о членах команды

def load_user(user_id, login_data):
    if login_data:
        load_user_login_data(user_id)
    else:
        load_user_members_data(user_id)


# Функция для получения данных авторизации пользователя по id

@login_manager.user_loader
def load_user_login_data(user_id):
    session = db_session.create_session()
    return session.query(UserLoginData).get(user_id)


# Функция для получения данных о команде по id

@login_manager.user_loader
def load_user_members_data(user_id):
    session = db_session.create_session()
    return session.query(UserMemberData).get(user_id)


# Функция возвращает True если пользователь авторизован, иначе False

def is_auth():
    return current_user.is_authenticated


# Возвращает объект класса User если произошла авторизация
# Иначе None

def get_cur_user():
    if is_auth():
        return get_user_from_id(current_user.id)


#  Проверка на то, разрешено ли загружать такой файл

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Получить расширение по типу файла

def get_extension(filename):
    if '.' not in filename:
        return None
    return filename.rsplit('.', 1)[1]


# Проверка на то, забанен ли юзер

def is_banned():
    cur_user = get_cur_user()
    if cur_user:
        session = db_session.create_session()
        login_data = session.query(UserLoginData).filter(UserLoginData.id == cur_user.id).first()
        return login_data.is_banned
    return None


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
