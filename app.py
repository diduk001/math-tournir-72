import datetime
import json
import os
import os.path
from hashlib import md5

from data.users_login_data import User
import requests
from flask import Flask, render_template, redirect, request, jsonify, make_response, flash
from flask_login import LoginManager, logout_user, login_required, login_user, current_user
from data.db_session import global_init
import db_interface
from api import api_blueprint, TOTALLY_RIGHT_APIKEY, VALID_DOMINO_TASKS_NUMBERS, \
    VALID_PENALTY_TASKS_NUMBERS
from config import SERVER_URL, LoginForm, ForgotPassword, AddTaskForm, BanTeamForm, \
    StartEndTimeForm, PardonTeamForm, SignUpUserForm, GradeGameForm, create_user
from db_interface import *


# Класс конфигурации

class ConfigClass(object):
    SECRET_KEY = "0d645377e31ab6b5847ec817bac4aaf8"
    USER_ENABLE_EMAIL = False
    USER_ENABLE_USERNAME = True
    UPLOAD_FOLDER = os.path.join('static', 'img', 'uploads')


# флаги для того, показывать ли тестовых юзеров и команд с 0 очков

RESULTS_SHOW_ZERO = 0
RESULTS_SHOW_TEST = 0

# Создание приложения

app = Flask(__name__)

# Инициализация бд
global_init('main_bd')

# конфигурация
app.config.from_object(__name__ + '.ConfigClass')
db_session.global_init(os.path.join("db", "login_data_members_data_session.sqlite"))
app.register_blueprint(api_blueprint)

# Создание и инициализация менеджера входа

login_manager = LoginManager()
login_manager.init_app(app)

# set с допущенными расширениями

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', "gif", "PNG", "JPG", "JPEG", "GIF"}


for grade in range(5, 8):
    file_for_gauch = open(f'file_for_gauch_{grade}.txt', 'w')
    file_for_gauch.write("ВРЕМЯ \t\t\t | КОМАНДА \t\t\t\t | ЗАДАЧА \t\t | ОТВЕТ \t\t\t")
    file_for_gauch.close()

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

            is_player = ~bool(current_user.member2_name)
            team = current_user.team_name
            grade = current_user.grade
            domino_place = get_place(team, 'domino', grade)
            penalty_place = get_place(team, 'penalty', grade)
            if is_player:
                return render_template("profile.html", domino_place=domino_place,
                                       penalty_place=penalty_place, **(get_cur_user().__dict__()),
                                       is_player=True)
            else:
                return render_template("profile.html", domino_place=domino_place,
                                       penalty_place=penalty_place, **(get_cur_user().__dict__()),
                                       is_player=False)
        else:
            # Иначе переправляем на вход
            return redirect("/login")
    elif debug_var == 1:
        return redirect("/login")


# Получить место команды в игре

def get_place(team, game, grade):
    con = sqlite3.connect(os.path.join("db", "tasks.db"))
    cur = con.cursor()
    table = f"{game}_tasks{grade}"
    results = list(
        map(lambda x: x[0], cur.execute(f"SELECT title from {table} ORDER BY sum DESC").fetchall()))
    con.close()
    return results.index(team) + 1


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

def get_task_state(table, task, team, grade):
    con = sqlite3.connect(os.path.join("db", "tasks.db"))
    cur = con.cursor()
    que = f"SELECT {task} FROM {table + str(grade)} WHERE title = '{team}'"
    result = cur.execute(que).fetchone()[0]
    con.close()
    if not result:
        return ""
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


# Получить состояние игры

def game_status(game, time):
    global domino_start_time, domino_end_time, penalty_start_time, penalty_end_time
    print(time)
    if game == 'domino':
        if domino_start_time > time:
            return 'not_started'
        elif domino_end_time < time:
            return 'ended'
        else:
            return 'in_progress'
    else:
        print(penalty_start_time)
        print(penalty_end_time)
        print(penalty_start_time > time)
        if penalty_start_time > time:
            return 'not_started'
        elif penalty_end_time < time:
            return 'ended'
        else:
            return 'in_progress'


# Возвращает время когда команда последний раз была на сайте

def get_last_time(team):
    con = sqlite3.connect(os.path.join("db", "tasks_info.db"))
    cur = con.cursor()
    print(f"SELECT time FROM about_teams WHERE title='{team}'")
    time = cur.execute(f"SELECT time FROM about_teams WHERE title='{team}'").fetchone()[0]
    con.close()
    return list(map(int, time.split()))


# Изменяет время когда команда последний раз была на сайте

def update_last_time(team, time):
    con = sqlite3.connect(os.path.join("db", "tasks_info.db"))
    cur = con.cursor()
    que = f'UPDATE about_teams\n'
    que += f"SET time = '{time}'\n"
    que += f"WHERE title = '{team}'"
    cur.execute(que)
    con.commit()
    con.close()


# Изменяет состояние честности команды

def update_cheater_status(team, game, grade):
    global domino_info
    con = sqlite3.connect(os.path.join("db", "tasks_info.db"))
    cur = con.cursor()
    que = f'UPDATE about_teams\n'
    print('inside')
    if game == 'domino':
        print('no')
        que += f"SET domino_cheater = 1\n"
        # Возвращаем задачи из рук на "игровой стол"
        keys_of_picked_tasks = get_task_state('domino_tasks', 'picked_tasks', team, grade).split()

        for key in keys_of_picked_tasks:
            domino_info[grade][key]['number'] += 1
        keys_of_picked_tasks = []
        update('domino_tasks', 'picked_tasks', " ".join(keys_of_picked_tasks), team, grade)
    else:
        print('yes')
        que += f"SET penalty_cheater = 1\n"
    que += f"WHERE title='{team}'"
    print(que)
    cur.execute(que)
    con.commit()
    con.close()


# Получить состояние честности

def get_cheater_status(team, game):
    con = sqlite3.connect(os.path.join("db", "tasks_info.db"))
    cur = con.cursor()
    if game == 'domino':
        que = f"SELECT domino_cheater FROM about_teams WHERE title=?"
    else:
        que = f"SELECT penalty_cheater FROM about_teams WHERE title=?"
    res = bool(cur.execute(que, (team,)).fetchone()[0])
    con.close()
    return res


# Получить посещал ли пользователь игру

def get_visited_status(team, game):
    con = sqlite3.connect(os.path.join("db", "tasks_info.db"))
    cur = con.cursor()
    que = f"SELECT {game}_visited FROM about_teams WHERE title=?"
    res = bool(cur.execute(que, (team,)).fetchone()[0])
    con.close()
    return res

# Обновить посещал ли пользователь игру

def update_visited_status(team, game):
    con = sqlite3.connect(os.path.join("db", "tasks_info.db"))
    cur = con.cursor()
    que = f'UPDATE about_teams\n'
    que += f"SET {game}_visited = 1\n"
    que += f"WHERE title='{team}'"
    cur.execute(que)
    con.commit()
    con.close()

# Проверка на честность

@app.route("/anti_cheat", methods=["POST"])
def anti_cheat():
    global domino_start_time, domino_end_time, penalty_start_time, penalty_end_time
    if is_auth():
        team = current_user.team_name
        grade = str(current_user.grade)
        cur_time = datetime.datetime.now()
        cur_time += datetime.timedelta(hours=5)
        last_time = datetime.datetime(*get_last_time(team))
        print(cur_time, last_time, 'cur_time')
        if cur_time - last_time > datetime.timedelta(minutes=6):
            print('oh no')
            print(last_time > penalty_start_time, penalty_start_time, 'last_time >')
            print('penalty', game_status('penalty',
                             cur_time), 'game_status')
            if game_status('domino', cur_time) == 'in_progress' and last_time > domino_start_time and \
               get_visited_status(team, 'domino'):
                update_cheater_status(team, 'domino', grade)
            if game_status('penalty', cur_time) == 'in_progress' and last_time > penalty_start_time and \
               get_visited_status(team, 'penalty'):
                print('bad bad cheater')
                update_cheater_status(team, 'penalty', grade)
        update_last_time(team, ' '.join(
            map(str, [cur_time.year, cur_time.month, cur_time.day, cur_time.hour,
                      cur_time.minute, cur_time.second])))
    return jsonify({'hah': 'hah'})


# Регистрация

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    global penalty_start_time, domino_start_time
    current_time = datetime.datetime.now() + datetime.timedelta(hours=5)
    start_time = datetime.datetime(2020, 5, 31, 14, 0, 0)
    end_time = datetime.datetime(2020, 6, 1, 22, 30, 0)
    if current_time < start_time:
        return render_template('registration_has_not_begin.html')
    elif current_time > end_time:
        return render_template("registration_is_closed.html")
    else:
        sign_up_form = SignUpUserForm()
        params = dict()
        params["title"] = "Регистрация"
        params["form"] = sign_up_form

        if sign_up_form.validate_on_submit():
            if is_auth():
                logout_user()

            is_login_used = login_used(request.form.get("team-login"))
            if is_login_used:
                if login_used:
                    params["login_used"] = True
                return render_template("sign_up_user.html", **params)

            # Создания объекта User

            user = create_user(
                request.form.get("login"),
                request.form.get("name"),
                request.form.get("surname"),
                request.form.get("email"),
                int(request.form.get("grade")),
                request.form.get("school"),
                request.form.get("teachers"),
                request.form.get("info"))

            user.set_password(request.form.get("password"))

            # Добавление пользователя в базы данных
            domino_table = 'domino_tasks' + str(user.grade)
            penalty_table = 'penalty_tasks' + str(user.grade)
            about_teams = "about_teams"
            time = datetime.datetime.now()
            time = ' '.join(
                map(str, [time.year, time.month, time.day, time.hour, time.minute, time.second]))

            db_interface.execute(os.path.join("db", "tasks.db"),
                                 f"INSERT into {domino_table}(title) values ("
                                 f"'{user.team_name}')")
            db_interface.execute(os.path.join("db", "tasks.db"),
                                 f"INSERT into {penalty_table}(title) values ('{user.team_name}')")
            db_interface.execute(os.path.join("db", "tasks_info.db"),
                                 f"INSERT into {about_teams}(title, time) values ("
                                 f"'{user.team_name}', '{time}')")

            add_user(user)

            return redirect("/login")

        return render_template("sign_up_user.html", **params)

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
        admin_cookie = request.cookies.get("ac3308b31764fc2774d1df8d3ba92f0d")  # Входили ли
        if admin_cookie and admin_cookie == "ddb5f9b4be9fa7bb3b16a6e3a19f237c":  # Если уже входили
            return admin_room()  # Возвращаем кабинет админа
        else:
            return render_template("admin_pass.html", title="Авторизуйтесь, пожалуйста")
    else:
        password = request.form.get("admin_pass")
        password = password.strip()
        if hash_md5(password) == "9ef668352a9addb7d462668c012602d5":  # hash_md5("IloveFmschool!")
            resp = make_response(admin_room())
            resp.set_cookie('ac3308b31764fc2774d1df8d3ba92f0d', 'ddb5f9b4be9fa7bb3b16a6e3a19f237c')
            return resp
        else:
            flash("Неправильный пароль!")
            return render_template("admin_pass.html", title="Авторизуйтесь, пожалуйста")


# Пункт управления для админов
def admin_room():
    params = dict()
    params["add_task_form"] = AddTaskForm()
    params["start_end_time_form"] = StartEndTimeForm()
    params["ban_team_form"] = BanTeamForm()
    params["pardon_team_form"] = PardonTeamForm()
    params["grade_game_form"] = GradeGameForm()
    return render_template("admin_room.html", **params)


# Страничка с результатом добавления задачи

@app.route('/cdb63e6a1a08307c6c44354aa37972b7', methods=['POST'])
def add_task():
    task = request.form.get("task")
    grade = request.form.get("grade")
    game_type = request.form.get("game_type")
    answer = request.form.get("answer")
    manual_check = bool(request.form.get("manual_check"))
    ans_picture = bool(request.form.get("ans_picture"))
    manual_check = ans_picture or manual_check

    if game_type == "domino" and task not in VALID_DOMINO_TASKS_NUMBERS:
        return """номер задачи и тип игры не совпадают 
                  <a href="/admin"> вернуться обратно</a>"""
    if game_type == "penalty" and task not in VALID_PENALTY_TASKS_NUMBERS:
        return """номер задачи и тип игры не совпадают
                  <a href="/admin"> вернуться обратно</a>"""
    file = request.files.get('info')

    if file and allowed_file(file.filename):
        filename = task + '-' + grade + '.' + get_extension(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        info = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        url = SERVER_URL + '/api'
        params = {"apikey": TOTALLY_RIGHT_APIKEY,
                  "request_type": "add_task",
                  "game_type": game_type,
                  "grade": grade,
                  "task": task,
                  "answer": answer,
                  "info": info,
                  "manual_check": manual_check,
                  "ans_picture": ans_picture}
        r = requests.get(url, params=params)

        return """задача добавлена <a href="/admin"> вернуться 
        обратно</a>"""
    else:
        return """файл не прошёл проверку <a href="/admin">
                  вернуться обратно</a>"""


# Страничка с результатом изменением времени соревнований

@app.route('/8770a9a6c5ab1b00a4e0293d9ebd7bec', methods=['POST'])
def start_end_time():
    global domino_start_time, domino_end_time, penalty_start_time, penalty_end_time

    try:
        print("time_start", "time_end")
        game_type = request.form.get("game_type")
        time_start = request.form.get("time_start")
        time_end = request.form.get("time_end")
        print(time_start)
        print(time_end)
        print('end')
    except Exception as e:
        return "Исключение: " + str(e)

    try:
        print('penalty_start_time')
        date, time = time_start.split()[0], time_start.split()[1]
        days, months, years = int(date.split('.')[0]), int(date.split('.')[1]), int(date.split('.')[2])
        hours, minutes, seconds = int(time.split(':')[0]), int(time.split(':')[1]), int(time.split(':')[2])
        datetime_start = datetime.datetime(years, months, days, hours, minutes, seconds)
        date, time = time_end.split()[0], time_end.split()[1]
        days, months, years = int(date.split('.')[0]), int(date.split('.')[1]), int(date.split('.')[2])
        hours, minutes, seconds = int(time.split(':')[0]), int(time.split(':')[1]), int(time.split(':')[2])
        datetime_end = datetime.datetime(years, months, days, hours, minutes, seconds)
        print(datetime_start, datetime_end)
    except ValueError:
        return """Время не соответствует формату <a href="/admin"> 
                  вернуться обратно</a>"""
    if game_type == "domino":
        domino_start_time = datetime_start
        domino_end_time = datetime_end
    elif game_type == "penalty":
        penalty_start_time = datetime_start
        penalty_end_time = datetime_end
    print(game_status(game_type, datetime.datetime.now() + datetime.timedelta(hours=5)))
    print(penalty_start_time)
    print(penalty_end_time)
    print('new_end')
    return """Вы установили время и дату соревнования (если я не ошибся). <a href="/admin"> вернуться 
        обратно</a>"""


# Страничка с результатом бана команды

@app.route('/1551c97a3794c5257e7ed3c5b816a825', methods=['POST'])
def ban_team():
    team_name = request.form.get("team_name")
    if not team_name_used(team_name):
        return f"""Команды {repr(team_name)} существует. Пожалуйста, проверьте, всё ли правильно вы
               ввели <a href="/admin"> вернуться обратно</a>"""

    session = db_session.create_session()

    try:
        team_id = session.query(UserMemberData).filter(UserMemberData.team_name ==
                                                       team_name).first().id
        login_data = session.query(User).filter(User.id == team_id).first()
        login_data.is_banned = True
        session.commit()

        return f"""Команда {team_name} отправилась в бан <a 
                href="/admin"> вернуться обратно</a>"""
    except Exception as e:
        return f"""Произошла ошибка: {e} \n <a href="/admin"> 
                вернуться обратно</a>"""


# Прощение (ну то есть прощают типа как бан но наоборот)

@app.route('/7717fdf71bcc8418fb7fabcb5b9c46d2', methods=['POST'])
def pardon():
    team_name = request.form.get("team_name")
    if not team_name_used(team_name):
        return f"""Команды {repr(team_name)} существует. Пожалуйста, проверьте, всё ли правильно вы
                   ввели <a href="/admin"> вернуться обратно</a>"""

    session = db_session.create_session()
    team_id = session.query(UserMemberData).filter(UserMemberData.team_name ==
                                                   team_name).first().id
    banned = session.query(User).filter(User.id == team_id).first().is_banned

    if not banned:
        return f"""Команда {repr(team_name)} не дисквалифицирована. 
                <a href="/admin"> вернуться обратно</a>"""

    try:
        login_data = session.query(User).filter(User.id == team_id).first()
        login_data.is_banned = False
        session.commit()

        return f"""Команда {repr(team_name)} прощена. <a href="/admin">
                вернуться обратно</a>"""
    except Exception as e:
        return f"""Произошла ошибка: {e} \n <a href="/admin"> 
                        вернуться обратно</a>"""


# Страница, которая переправляет админа на ручную проверку
# Ну или страница с ручной проверкой, я пока не решил

@app.route('/b1131abe22277e066731346d53b953f8', methods=['POST'])
def redirect_to_manual_check():
    grade = request.form.get("grade")
    game = request.form.get("game")
    return redirect(f"deb5b702b8e7cd15788ce1a96fa93e7c/{game}/{grade}")


# Функция хэширования

def hash_md5(s):
    h = md5(bytes(s, encoding="utf-8"))
    return h.hexdigest()


# всё что нужно для игр

def get_point(string):
    return string[:-2]


def get_state(string):
    return string[-2:]


# Ручная проверка
@app.route('/deb5b702b8e7cd15788ce1a96fa93e7c/<game>/<grade>', methods=["POST", "GET"])
def manual_checking(game, grade):
    if request.method == "GET":
        con = sqlite3.connect(os.path.join("db", "manual_check.db"))
        cur = con.cursor()
        table = f'{game}_{grade}'
        que = f"SELECT * from {table} ORDER BY id"
        task = cur.execute(que).fetchone()
        if task:
            team = task[1]
            task_name = task[2]
            task_result = task[4]

            ans_picture = get_ans_picture(game, grade, task_name)
            return render_template("manual_checking.html", team=team, task_name=task_name,
                                   task_result=task_result,
                                   game=game, grade=grade, not_task=False, ans_picture=ans_picture)
        else:
            return render_template("manual_checking.html", not_task=True)
    elif request.method == "POST":
        team = request.form['team']
        task = request.form['task']
        result = request.form['result']
        result = True if result == "true" else False
        verdicts = ['cf', 'ff', 'cs', 'fs']
        table = f"{game}_tasks"
        if game == 'domino':
            key = domino_tasks_keys_by_names[task]
            task = {"state": get_task_state("domino_tasks", key, team, grade), "name": task}
            if get_state(task['state']) in ['cf', 'cs']:
                if result and get_state(task['state']) == 'cf':
                    task['state'] = str(
                        sum(map(int, domino_info[grade][key]['name'].split('-')))) + 'af'
                    if task['name'] == '0-0':
                        task['state'] = '10af'
                # Если пользователь решил задачу со второй попытки
                elif result:
                    task['state'] = str(
                        max(map(int, domino_info[grade][key]['name'].split('-')))) + 'as'
                # Если пользователь решил задачу неправильно
                else:
                    task['state'] = verdicts[
                        verdicts.index(get_state(task['state'])) + 1]
                    if task['state'] == 'ff':
                        task['state'] = '0ff'
                    else:
                        task['state'] = str(
                            -min(map(int, domino_info[grade][key]['name'].split('-')))) + 'fs'
                    if task['name'] == '0-0':
                        task['state'] = '0fs'
                table = "domino_tasks"
        else:
            key = f"t{task}"
            task = {"state": get_task_state("penalty_tasks", key, team, grade), "name": task}
            table = f"{game}_tasks"
            if get_state(task['state']) in ['cf', 'cs']:
                # Если пользователь сдал задачу правильно
                if result:
                    # Если пользователь сдал задачу правильно с первой попытки
                    if get_state(task['state']) == 'cf':
                        task['state'] = str(penalty_info[grade][key]['cost']) + 'af'
                        penalty_info[grade][key]['number'] -= 1
                        if penalty_info[grade][key]['cost'] > 5:
                            if penalty_info[grade][key]['number'] == 0:
                                penalty_info[grade][key]['cost'] -= 1
                                penalty_info[grade][key]['number'] = NUMBER_OF_PENALTY_TASKS_SETS
                    # Если пользователь сдал задачу правильно со второй попытки
                    else:
                        task['state'] = '3' + 'as'
                # Если пользователь сдал задачу неправильно
                else:
                    task['state'] = verdicts[
                        verdicts.index(get_state(task['state'])) + 1]
                    if task['state'] == 'ff':
                        task['state'] = '0' + 'ff'
                    else:
                        task['state'] = '-2' + 'fs'
                table = 'penalty_tasks'
        # обновление бд
        update_results(table, get_point(task['state']), team, grade)
        update(table, key, task['state'], team, grade)
        con = sqlite3.connect(os.path.join("db", "manual_check.db"))
        cur = con.cursor()
        table = f'{game}_{grade}'
        que = f"DELETE FROM {table} WHERE (team = '{team}') AND (task = '{task['name']}')"
        cur.execute(que).fetchone()
        con.commit()
        con.close()
    return jsonify({'hah': 'hah'})


# Проверка задачи

def check_task(game, grade, task, user_answer):
    url = SERVER_URL + '/api'
    params = {"apikey": TOTALLY_RIGHT_APIKEY,
              "request_type": "check_task",
              "game_type": game,
              "grade": grade,
              "task": task,
              "answer": user_answer}
    r = requests.get(url, params=params)
    if r.content == b"True":
        return True
    elif r.content == b"False":
        return False
    else:
        raise Exception(r.content)


# Узнать проверяется ли задача в ручную

def get_manual_check(game, grade, task):
    con = sqlite3.connect(os.path.join("db", "tasks_info.db"))
    cur = con.cursor()
    table = f'{game}_{grade}_info'
    que = f"SELECT manual_check FROM {table} WHERE task=?"
    res = cur.execute(que, (task,)).fetchone()
    if res is not None:
        res = res[0]
        res = bool(res)
    con.close()
    return res


# Получение условия задачи

def get_task(game, grade, task):
    url = SERVER_URL + '/api'
    params = {"apikey": TOTALLY_RIGHT_APIKEY,
              "request_type": "get_task",
              "game_type": game,
              "grade": grade,
              "task": task}
    r = requests.get(url, params=params)
    print(r)
    d = json.loads(r.content)
    print(d)
    try:
        return d["info"]
    except Exception as e:
        return None


# Всё что нужно для домино

domino_start_time = datetime.datetime(2020, 6, 2, 10, 0, 30)
domino_end_time = datetime.datetime(2020, 6, 2, 13, 0, 30)
domino_keys = list(map(lambda x: 't' + str(x), range(1, 29)))
domino_tasks_keys_by_names = {'0-0': 't1', '0-1': 't2', '0-2': 't3', '0-3': 't4', '0-4': 't5',
                              '0-5': 't6',
                              '0-6': 't7', '1-1': 't8', '1-2': 't9', '1-3': 't10', '1-4': 't11',
                              '1-5': 't12',
                              '1-6': 't13', '2-2': 't14', '2-3': 't15', '2-4': 't16', '2-5': 't17',
                              '2-6': 't18',
                              '3-3': 't19', '3-4': 't20', '3-5': 't21', '3-6': 't22', '4-4': 't23',
                              '4-5': 't24',
                              '4-6': 't25', '5-5': 't26', '5-6': 't27', '6-6': 't28'}
domino_tasks_names_by_keys = {'t1': '0-0', 't2': '0-1', 't3': '0-2', 't4': '0-3', 't5': '0-4',
                              't6': '0-5',
                              't7': '0-6', 't8': '1-1', 't9': '1-2', 't10': '1-3', 't11': '1-4',
                              't12': '1-5',
                              't13': '1-6', 't14': '2-2', 't15': '2-3', 't16': '2-4', 't17': '2-5',
                              't18': '2-6',
                              't19': '3-3', 't20': '3-4', 't21': '3-5', 't22': '3-6', 't23': '4-4',
                              't24': '4-5',
                              't25': '4-6', 't26': '5-5', 't27': '5-6', 't28': '6-6'}
domino_messages = {'full': "Вы уже взяли 2 задачи", 'af': 'Вы уже решили эту задачу',
                   'as': 'Вы уже решили эту задачу',
                   'fs': 'У Вас закончились попытки на сдачу этой задачи',
                   'absent': 'На данный момент задачи с этим номером отсутсвуют',
                   'hand': 'Вы уже взяли эту задачу',
                   'cf': "Задача проверяется",
                   'cs': 'Задача проверяется'}

number_of_domino_task = 3
domino_info = {'5': {}, '6': {}, '7': {}}
for grade in ['5', '6', '7']:
    for i in range(1, 29):
        domino_info[grade][f't{i}'] = {'name': domino_tasks_names_by_keys[f't{i}'],
                                       'number': number_of_domino_task}


def get_ans_picture(game, grade, task):
    con = sqlite3.connect(os.path.join("db", "tasks_info.db"))
    cur = con.cursor()
    table = f'{game}_{grade}_info'
    que = f"SELECT ans_picture FROM {table} WHERE task=?"
    res = cur.execute(que, (task,)).fetchone()
    if res is not None:
        res = res[0]
        res = bool(res)
    con.close()
    return res


# Сдача задачи на ручную проверку
@app.route("/add_task_for_manual_checking", methods=["POST"])
def add_task_for_manual_checking():
    team = current_user.team_name
    grade = str(current_user.grade)
    game = request.form['game']
    task = request.form['task']
    if not get_cheater_status(team, game):
        time = datetime.datetime.now()
        time = ' '.join(map(str, [time.year, time.month, time.day, time.hour, time.minute, time.second]))
        if get_ans_picture(game, grade, task):
            result = request.form['result'][1:]
        else:
            result = request.form['result']
        con = sqlite3.connect(os.path.join("db", "manual_check.db"))
        cur = con.cursor()
        table = f'{game}_{grade}'
        que = f"INSERT INTO {table}(team, task, time, result) VALUES('{team}', '{task}', '{time}', '{result}')"
        cur.execute(que)
        con.commit()
        con.close()

        file_for_gauch = open(f'file_for_gauch_{grade}.txt', 'a')
        file_for_gauch.write(f"{time} \t\t\t | {team} \t\t\t\t | {task} \t\t | {result} \t\t\t \n")
        file_for_gauch.close()
        # Если Домино то возвращаем задачу на "игровой стол"
        if game == "domino":
            key = domino_tasks_keys_by_names[task]
            domino_info[str(grade)][key]['number'] += 1
            picked_tasks = get_task_state('domino_tasks', 'picked_tasks', team, grade).split()
            picked_tasks.remove(key)
            picked_tasks = ' '.join(picked_tasks)
            update('domino_tasks', 'picked_tasks', picked_tasks, team, grade)
        else:
            key = f"t{task}"
        # Отмечаем что задача проверяется
        table = f"{game}_tasks"
        state = get_task_state(table, key, team, grade)
        # Первая попытка сдачи задачи
        if get_state(state) == 'ok':
            state = '0cf'
        # Вторая попытка сдачи задачи
        else:
            state = '0cs'
        update(f'{game}_tasks', key, state, team, grade)
        return jsonify({'hah': 'hah'})


# Страница домино


@app.route("/domino", methods=["GET", "POST"])
def domino():
    # Необходимые штуки
    global domino_keys, domino_messages, domino_tasks_keys_by_names, domino_tasks_names_by_keys, domino_info

    # Если пользователь не вошёл в аккаунт команды/игрока, то мы сообщаем ему об этом

    if not is_auth():
        return render_template("not_authenticated.html")

    # Если пользователь нарушил правила, то мы сообщаем ему об этом

    if get_cheater_status(current_user.team_name, 'domino'):
        return render_template("cheater.html")
    # Если мы забанили команду

    if get_cur_user().is_banned:
        return render_template("you_are_banned.html", title="Вас дисквалифицировали")
    team = current_user.team_name
    grade = str(current_user.grade)
    time = datetime.datetime.now() + datetime.timedelta(hours=5)
    # Если игра ещё не началась, то мы показывает отсчёт до начала
    if game_status('domino', time) == 'not_started':
        start_time = f"{domino_start_time.month} {domino_start_time.day} {domino_start_time.year} "
        start_time += f"{domino_start_time.hour}:{domino_start_time.minute}:{domino_start_time.second}"
        now_time = f"{time.month} {time.day} {time.year} "
        now_time += f"{time.hour}:{time.minute}:{time.second}"
        return render_template("domino.html", title="Домино ТЮМ72", state='not started',
                               start_time=start_time, now_time=now_time)
    # Если игра уже закончилась то мы сообщаем об этом
    elif game_status('domino', time) == 'ended':
        return render_template("domino.html", title="Домино ТЮМ72", state='ended')
    # Иначе отображаем игру
    else:
        update_visited_status(team, 'domino')
        # Время окончание игры
        end_time = f"{domino_end_time.month} {domino_end_time.day} {domino_end_time.year} "
        end_time += f"{domino_end_time.hour}:{domino_end_time.minute}:{domino_end_time.second}"
        now_time = f"{time.month} {time.day} {time.year} "
        now_time += f"{time.hour}:{time.minute}:{time.second}"
        print(end_time, 'end_time')
        # Игра в процессе
        state = 'in progress'
        # Формируем информацию о состоянии задач у пользователя
        tasks = {}
        for key in domino_keys:
            tasks[key] = {'name': domino_info[grade][key]['name'],
                          'state': get_task_state('domino_tasks', key, team, grade),
                          'manual_check': get_manual_check('domino', grade,
                                                           domino_tasks_names_by_keys[key]),
                          'ans_picture': get_ans_picture('domino', grade,
                                                         domino_tasks_names_by_keys[key])}
        # Обновляем состояние задач, которые закончились/появились на "игровом столе"
        for key in domino_keys:
            if get_state(tasks[key]['state']) == 'ok' and domino_info[grade][key]['number'] == 0:
                tasks[key]['state'] = '0bo'
            elif get_state(tasks[key]['state']) == 'ff' and domino_info[grade][key]['number'] == 0:
                tasks[key]['state'] = '0bf'
            elif get_state(tasks[key]['state']) == 'bo' and domino_info[grade][key]['number'] > 0:
                tasks[key]['state'] = '0ok'
            elif get_state(tasks[key]['state']) == 'bf' and domino_info[grade][key]['number'] > 0:
                tasks[key]['state'] = '0ff'
        # Формируем информацию о задачах, которые сейчас "на руках" у пользователя
        keys_of_picked_tasks = get_task_state('domino_tasks', 'picked_tasks', team, grade).split()
        picked_tasks = []
        for key in keys_of_picked_tasks:
            picked_tasks.append(
                {'name': domino_tasks_names_by_keys[key],
                 'content': str(get_task('domino', int(grade), domino_tasks_names_by_keys[key])),
                 'manual_check': get_manual_check('domino', grade, domino_tasks_names_by_keys[key]),
                 'ans_picture': get_ans_picture('domino', grade, domino_tasks_names_by_keys[key])})
        print(picked_tasks)
        # Если пользователь просто загрузил страницу игры то показывает её ему
        if request.method == "GET":
            return render_template("domino.html", title="Домино ТЮМ72", block="", tasks=tasks,
                                   keys=domino_keys,
                                   picked_tasks=picked_tasks, message=False, info=domino_info[grade],
                                   state=state, end_time=end_time, now_time=now_time,
                                   number_of_picked_tasks=len(picked_tasks))
        # Иначе пользователь сдал или взял "на руки" задачу
        elif request.method == "POST":
            # Сообщение об ошибке
            # Если пользователь попытался взять задачу
            print(request.form)
            if request.form.get("picked"):
                print('whatwhat')
                key = domino_tasks_keys_by_names[request.form.get("picked")]
                number_of_picked_task = len(picked_tasks)
                # У пользователя уже 2 задачи "на руках", сообщаем, что больше взять нельзя
                if number_of_picked_task == 2:
                    message = domino_messages['full']
                # Выбранная задача уже "на руках" у пользователя, сообщаем об этом
                elif key in keys_of_picked_tasks:
                    message = domino_messages['hand']
                # Пользователь может взять задачу, выдаём её
                elif get_state(tasks[key]['state']) in ['ff', 'ok']:
                    picked_tasks.append(key)
                    keys_of_picked_tasks.append(key)
                    picked_tasks.append(
                        {'name': domino_tasks_names_by_keys[key],
                         'content': str(
                             get_task('domino', int(grade), domino_tasks_names_by_keys[key])),
                         'manual_check': get_manual_check('domino', grade,
                                                          domino_tasks_names_by_keys[key]),
                         'ans_picture': get_ans_picture('domino', grade,
                                                        domino_tasks_names_by_keys[key])})
                    domino_info[grade][key]['number'] -= 1
                # Пользователь не может взять задачу по другой причине, сообщаем причину
                else:
                    message = domino_messages[get_state(tasks[key]['state'])]
            # Пользователь сдаёт задачу
            elif request.form.get('answer'):
                key = domino_tasks_keys_by_names[request.form.get('name')]
                verdicts = ['ok', 'ff', 'fs']
                # Если всё нормально и пользователь не попытался багануть сайт
                if get_state(tasks[key]['state']) in ['ok', 'ff'] and key in keys_of_picked_tasks:
                    result = check_task('domino', grade, domino_tasks_names_by_keys[key], request.form.get('answer'))
                    # Если пользователь решил задачу с первой попытки
                    if result and get_state(tasks[key]['state']) == 'ok':
                        tasks[key]['state'] = str(
                            sum(map(int, domino_info[grade][key]['name'].split('-')))) + 'af'
                        if tasks[key]['name'] == '0-0':
                            tasks[key]['state'] = '10af'
                    # Если пользователь решил задачу со второй попытки
                    elif result:
                        tasks[key]['state'] = str(
                            max(map(int, domino_info[grade][key]['name'].split('-')))) + 'as'
                    # Если пользователь решил задачу неправильно
                    else:
                        tasks[key]['state'] = verdicts[
                            verdicts.index(get_state(tasks[key]['state'])) + 1]
                        if tasks[key]['state'] == 'ff':
                            tasks[key]['state'] = '0ff'
                        else:
                            tasks[key]['state'] = str(
                                -min(map(int, domino_info[grade][key]['name'].split('-')))) + 'fs'
                        if tasks[key]['name'] == '0-0':
                            tasks[key]['state'] = '0fs'
                    # Обновление бд, возвращение задачи на "игровой стол"
                    update_results('domino_tasks', get_point(tasks[key]['state']), team, grade)
                    update('domino_tasks', key, tasks[key]['state'], team, grade)
                    print('hah')
                    keys_of_picked_tasks.remove(key)
                    picked_tasks = []
                    for key in keys_of_picked_tasks:
                        picked_tasks.append(
                            {'name': domino_tasks_names_by_keys[key],
                             'content': str(get_task('domino', int(grade), domino_tasks_names_by_keys[key])),
                             'manual_check': get_manual_check('domino', grade, domino_tasks_names_by_keys[key]),
                             'ans_picture': get_ans_picture('domino', grade, domino_tasks_names_by_keys[key])})
                    domino_info[grade][key]['number'] += 1
            update('domino_tasks', 'picked_tasks', " ".join(keys_of_picked_tasks), team, grade)
            # Обновление страницы
            return render_template("domino.html", title="Домино ТЮМ72", block="", tasks=tasks,
                                   keys=domino_keys, picked_tasks=picked_tasks, message=message,
                                   info=domino_info[grade], state=state, end_time=end_time,
                                   number_of_picked_tasks=len(picked_tasks), now_time=now_time)


# Всё что нужно для пенальти

penalty_keys = list(map(lambda x: 't' + str(x), range(1, 17)))
penalty_info = {}
for grade in ['5', '6', '7']:
    penalty_info[grade] = {}
    for key in penalty_keys:
        penalty_info[grade][key] = {'name': key[1:], 'cost': 15}
stupid_crutch = 0
NUMBER_OF_PENALTY_TASKS_SETS = 2
penalty_start_time = datetime.datetime(2020, 6, 3, 10, 0, 30)
penalty_end_time = datetime.datetime(2020, 6, 3, 13, 0, 30)
penalty_messages = {'accepted': 'Вы уже решили эту задачу',
                    'failed': 'У вас закончились попытки на сдачу этой задачи'}


# Страница пенальти

@app.route('/penalty', methods=["GET", "POST"])
def penalty():
    global penalty_info, stupid_crutch, NUMBER_OF_PENALTY_TASKS_SETS
    if stupid_crutch == 0:
        for grade in ['5', '6', '7']:
            penalty_info[grade] = {}
            for key in penalty_keys:
                content = str(get_task('penalty', grade, key[1:]))
                number = NUMBER_OF_PENALTY_TASKS_SETS
                penalty_info[grade][key] = {'name': key[1:], 'cost': 15, 'content': content, 'number': number}
    stupid_crutch += 1
    # Если пользователь не вошёл в аккаунт команды/игрока, то мы сообщаем ему об этом
    if not is_auth():
        return render_template("not_authenticated.html")

    # Если пользователь нарушил правила, то мы сообщаем ему об этом

    if get_cheater_status(current_user.team_name, 'penalty'):
        return render_template("cheater.html")

    # Если мы забанили команду

    if get_cur_user().is_banned:
        return render_template("you_are_banned.html", title="Вас дисквалифицировали")

    team = current_user.team_name
    grade = str(current_user.grade)
    time = datetime.datetime.now() + datetime.timedelta(hours=5)

    # Если игра ещё не началась, то мы показывает отсчёт до начала
    if game_status('penalty', time) == 'not_started':
        print('what')
        start_time = f"{penalty_start_time.month} {penalty_start_time.day} {penalty_start_time.year} "
        start_time += f"{penalty_start_time.hour}:{penalty_start_time.minute}:{penalty_start_time.second}"
        now_time = f"{time.month} {time.day} {time.year} "
        now_time += f"{time.hour}:{time.minute}:{time.second}"
        return render_template("penalty.html", title="Пенальти ТЮМ72", state='not started',
                               start_time=start_time, now_time=now_time)
    # Если игра уже закончилась то мы сообщаем об этом
    elif game_status('penalty', time) == 'ended':
        return render_template("penalty.html", title="Пенальти ТЮМ72", state='ended')
    # Иначе отображаем игру
    else:
        update_visited_status(team, 'penalty')
        end_time = f"{penalty_end_time.month} {penalty_end_time.day} {penalty_end_time.year} "
        end_time += f"{penalty_end_time.hour}:{penalty_end_time.minute}:{penalty_end_time.second}"
        now_time = f"{time.month} {time.day} {time.year} "
        now_time += f"{time.hour}:{time.minute}:{time.second}"
        state = 'in progress'
        tasks = {}
        # Формируем информацию о состоянии задач пользователя
        for key in penalty_keys:
            tasks[key] = {'name': key[1:],
                          'state': get_task_state('penalty_tasks', key, team, grade),
                          'manual_check': get_manual_check('penalty', grade, key[1:]),
                          'ans_picture': get_ans_picture('penalty', grade, key[1:])
                          }
        # Если пользователь сдал задачу
        if request.method == "POST":
            key = 't' + request.form.get('name')
            verdicts = ['ok', 'ff', 'fs']
            # Если пользователь не попытался багануть сайт
            if get_state(tasks[key]['state']) in ['ok', 'ff']:
                result = check_task('penalty', grade, key[1:], request.form.get('answer'))
                # Если пользователь сдал задачу правильно
                if result:
                    # Если пользователь сдал задачу правильно с первой попытки
                    if get_state(tasks[key]['state']) == 'ok':
                        tasks[key]['state'] = str(penalty_info[grade][key]['cost']) + 'af'
                        penalty_info[grade][key]['number'] -= 1
                        if penalty_info[grade][key]['cost'] > 5:
                            if penalty_info[grade][key]['number'] == 0:
                                penalty_info[grade][key]['cost'] -= 1
                                penalty_info[grade][key]['number'] = NUMBER_OF_PENALTY_TASKS_SETS
                    # Если пользователь сдал задачу правильно со второй попытки
                    else:
                        tasks[key]['state'] = '3' + 'as'
                # Если пользователь сдал задачу неправильно
                else:
                    tasks[key]['state'] = verdicts[
                        verdicts.index(get_state(tasks[key]['state'])) + 1]
                    if tasks[key]['state'] == 'ff':
                        tasks[key]['state'] = '0' + 'ff'
                    else:
                        tasks[key]['state'] = '-2' + 'fs'
                # обновление бд
                update_results('penalty_tasks', get_point(tasks[key]['state']), team, grade)
                update('penalty_tasks', key, tasks[key]['state'], team, grade)
        # отображение страницы
        return render_template("penalty.html", title="Пенальти ТЮМ72", tasks=tasks,
                               keys=penalty_keys,
                               info=penalty_info[grade], state=state, end_time=end_time, now_time=now_time)


# Результаты

@app.route('/results/<game>/<grade>')
def results(game, grade):
    debug_var_test = RESULTS_SHOW_TEST  # 0 - показываем тестовых юзеров, 1 - не показываем
    debug_var_zero = RESULTS_SHOW_ZERO  # 0 - показываем юзеров с 0 баллами, 1 - не показываем
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
        number = 16
        keys = penalty_keys
    table = game + '_tasks' + str(grade)
    con = sqlite3.connect(os.path.join("db", "tasks.db"))
    cur = con.cursor()
    results = cur.execute(f"SELECT * from {table} ORDER BY sum DESC").fetchall()
    numbers_of_solved = []
    if game == 'domino':
        step = 3
    else:
        step = 2
    for i in results:
        x = 0
        for j in i[step:-1]:
            if int(get_point(j)) > 0:
                x += 1
        numbers_of_solved.append(x)
    con.close()
    team_num = len(results)
    return render_template("results.html", team=team, results=results, title=titles[game],
                           grade=grade,
                           info=info, number=number, team_num=team_num, keys=keys, numbers_of_solved=numbers_of_solved)


# Страница для авторизации

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    params = dict()
    params["title"] = "Вход"
    params["form"] = form
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect("/")
        return render_template('login.html',
                               invalid_parameters=True,
                               form=form)
    return render_template("login.html", **params)


# Показывать/Не показывать нулёвых

@app.route('/toggle_show_zero')
def toggle_zero():
    global RESULTS_SHOW_ZERO

    if RESULTS_SHOW_ZERO == 0:
        RESULTS_SHOW_ZERO = 1
    else:
        RESULTS_SHOW_ZERO = 0

    return "ok. now is " + str(RESULTS_SHOW_ZERO)


# Показывать/Не показывать тестовых

@app.route('/toggle_show_test')
def toggle_test():
    global RESULTS_SHOW_TEST

    if RESULTS_SHOW_TEST == 0:
        RESULTS_SHOW_TEST = 1
    else:
        RESULTS_SHOW_TEST = 0

    return "ok. now is " + str(RESULTS_SHOW_TEST)


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
    return session.query(User).get(user_id)


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
        login_data = session.query(User).filter(User.id == cur_user.id).first()
        return login_data.is_banned
    return None


# Возвращает True если в команде один участник

def is_player(team_name):
    user = get_user_from_team_name(team_name)
    if None in user.member2:
        return True
    return False


if __name__ == '__main__':
    app.run(port=80, host='0.0.0.0')
