# -*- coding: utf-8 -*-
import os.path

from flask import render_template, request, flash, redirect
from flask_login import logout_user, current_user, login_user

from app import app
from app import login_manager
from app.forms import *
from app.game_creator import *
from config import Config


# Главная страница
@app.route('/')
@app.route('/index/')
def index():
    params = dict()
    params['title'] = 'ТЮМ 72'
    return render_template('index.html', **params)


# Регистрация
@app.route('/sign_up/', methods=['GET', 'POST'])
def sign_up():
    sign_up_form = SignUpUserForm()
    params = dict()
    params["title"] = "Регистрация"
    params["form"] = sign_up_form

    if sign_up_form.validate_on_submit():
        if is_auth():
            logout_user()

        user_login = request.form.get('login')
        login_used_query = db.session.query(User).filter(User.login == user_login)
        login_used = login_used_query.scalar() is not None

        if login_used:
            if login_used:
                params["login_used"] = True
            return render_template("sign_up_user.html", **params)

        # Создания объекта User

        user = User(
            request.form.get("login"),
            request.form.get("name"),
            request.form.get("surname"),
            int(request.form.get("grade")),
            request.form.get("school"),
            request.form.get("teachers"),
            request.form.get("info"))

        user.set_password(request.form.get("password"))
        user.set_email(request.form.get("email"))
        # Добавление пользователя в базы данных

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("sign_up_user.html", **params)


# Страница для авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    params = dict()
    params["title"] = "Вход"
    params["form"] = form
    if form.validate_on_submit():
        session = db.session
        user = session.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect("/")
        return render_template('login.html',
                               invalid_parameters=True,
                               form=form)
    return render_template("login.html", **params)


# Вход и профиль (профиль открывается только тогда, когда пользователь авторизован)
@app.route("/profile/<section>", methods=["GET", "POST"])
def profile(section):
    # Переменная для отладки, значения:
    # 0 - сценарий для релиза
    # 1 - открывает "Вход"
    # 2 - открывает "Профиль"

    debug_var = 0
    if debug_var == 0:
        if is_auth():
            # Если мы забанили игрока

            if current_user.is_banned:
                return render_template("you_are_banned.html", title="Ваш аккаунт заблокирован")

            # Имя, Фамилия, школа, класс, наборы прав, логин пользователя и словарь с разделами для наборов прав
            name = current_user.name
            surname = current_user.surname
            school = current_user.school
            grade = current_user.grade
            rights = current_user.rights.split()
            login = current_user.login
            dict_of_rights = {'god': 'Выдать набор прав',
                              'moderator': 'Заблокировать/Разблокировать пользователя',
                              'author': 'Игры'}
            # Если пользователь перешёл в раздел в который ему можно перейти
            if section in current_user.rights.split():
                # Если раздел "Пользователь" то просто возвращаем профиль без дополнительной информации
                if section == 'user':
                    return render_template("profile.html", name=name, surname=surname, school=school,
                                           grade=grade,
                                           login=login, rights=rights, dict_of_rights=dict_of_rights)
                # Если раздел "Бог" то возвращаем профиль с формой для выдачи прав
                elif section == 'god':
                    # Сама форма
                    form = GiveRightForm()
                    # Если форма правильно заполнена
                    if form.validate_on_submit():
                        # Логин пользователя, которому выдают права, набор прав который выдаётся
                        login = request.form.get('login')
                        right = request.form.get('right')
                        # Сам пользователь, которому выдают права
                        user = db.session.query(User).filter(User.login == login).first()
                        # Сообщение о отсутствии пользователя с таким логином
                        if user is None:
                            return render_template('users_not_found.html', users=[login],
                                                   last='/profile/god')
                        # Выдача набора прав
                        user.rights = user.rights + f' {right}'
                        db.session.commit()
                        # Сообщение о успехе выдачи прав
                        return render_template('success.html', last='/profile/god')
                    return render_template('profile_god.html', name=name, surname=surname,
                                           school=school, grade=grade,
                                           rights=rights, login=login, dict_of_rights=dict_of_rights,
                                           form=form)
                # Если раздел "Модератор", то воозвращаем формы для блокирования и разблокирования пользователей
                elif section == 'moderator':
                    # Формы для блокирования и разблокирования
                    ban_form = BanForm()
                    pardon_form = PardonForm()
                    # Если форма для блокирования заполнена корректно
                    if ban_form.validate_on_submit():
                        # Логин пользователя, которого хотят заблокировать
                        login = request.form.get('login')
                        # Сам пользователь, которого хотят заблокировать
                        user = db.session.query(User).filter(User.login == login).first()
                        # Сообщение о отсутствии пользователя с таким логином
                        if user is None:
                            return render_template('users_not_found.html', users=[login],
                                                   last='/profile/moderator')
                        # Блокировка пользователя
                        user.is_banned = True
                        db.session.commit()
                        return render_template('success.html', last='/profile/moderator')
                    # Если форма для разблокировки заполнена  корректно
                    if pardon_form.validate_on_submit():
                        # Логин пользователя, которого хотят разблокировать
                        login = request.form.get('login')
                        # Сам пользователь, которого хотят разблокировать
                        user = db.session.query(User).filter(User.login == login).first()
                        # Сообщение о отсутствии пользователя с таким логином
                        if user is None:
                            return render_template('users_not_found.html', users=[login],
                                                   last='/profile/moderator')
                        # Разблокировка пользователя
                        user.is_banned = False
                        db.session.commit()
                        return render_template('success.html', last='/profile/moderator')
                    return render_template('profile_moderator.html', name=name, surname=surname,
                                           school=school,
                                           grade=grade, rights=rights, login=login,
                                           dict_of_rights=dict_of_rights,
                                           ban_form=ban_form, pardon_form=pardon_form)
                # Если раздел "Автор", то возвращаем профиль с ссылкой на создание игр, отображаем все игры и их
                elif section == 'author':
                    games = []
                    for game in current_user.authoring:
                        new_game = {'common': get_game_common_info_human_format(game.title),
                                    'tasks': get_game_tasks_info_human_format(game.title),
                                    'authors_and_checkers': get_game_authors_and_checkers_info_human_format(
                                        game.title)}
                        if new_game['common'][5][1] == 'командная':
                            new_game['team'] = get_game_team_info_human_format(game.title)
                        else:
                            new_game['team'] = [('Минимальный размер команды', '-'),
                                                ('Максимальный размер команды', '-')]
                        games.append(new_game)
                    return render_template('profile_author.html', name=name, surname=surname,
                                           school=school,
                                           grade=grade, rights=rights, login=login,
                                           dict_of_rights=dict_of_rights,
                                           games=games)
                else:
                    return render_template('what_are_you_doing_here.html')
            else:
                return render_template('what_are_you_doing_here.html')
        else:
            # Иначе переправляем на вход
            return redirect("/login")
    elif debug_var == 1:
        return redirect("/login")


# Создание игры
@app.route('/create_game_form', methods=['POST', 'GET'])
def create_game_form():
    if is_auth():
        if 'author' in current_user.rights.split():
            form = GameCommonInfoForm()
            if form.validate_on_submit():
                title = request.form.get('title')
                grade = request.form.get('grade')
                info = request.form.get('info')
                game_type = request.form.get('game_type')
                start_time = request.form.get('start_time')
                end_time = request.form.get('end_time')
                game_format = request.form.get('game_format')
                privacy = request.form.get('privacy')
                author = current_user.id
                session = db.session
                author = session.query(User).filter(User.id == author).first()
                create_game(title, grade, game_type, start_time, end_time, game_format, privacy,
                            info, author)
                return render_template('success.html', last='../../profile/author')
            return render_template('game_creator.html', form=form, title='Создание игры')
    return render_template('what_are_you_doing_here.html')


# Изменение данных о игре
@app.route('/update_game/<game_title>/<block>', methods=["POST", "GET"])
def update_game(game_title, block):
    if is_auth():
        if 'author' in current_user.rights:
            game = get_game(game_title)
            if game != "Not found":
                if game.title in map(lambda x: x.title, current_user.authoring):
                    form = DICT_OF_FORMS[block].__call__()
                    if block == 'common':
                        default = get_game_common_info(game_title)
                    elif block == 'tasks':
                        default = get_game_tasks_info(game_title)
                    elif block == 'team':
                        default = get_game_team_info(game_title)
                    elif block == 'authors_and_checkers':
                        default = {'authors': ', '.join(get_game_authors_info(game_title)),
                                   'checkers': ', '.join(get_game_checkers_info(game_title))}
                    else:
                        return render_template('what_are_you_doing_here.html')
                    if form.validate_on_submit():
                        if block == 'common':
                            update_game_common_info(game_title, *(list(request.form.values())[1:-1]))
                            return render_template('success.html', last='../../profile/author')
                        elif block == 'tasks':
                            update_game_tasks_info(game_title, *(list(request.form.values())[1:-1]))
                            return render_template('success.html', last='../../profile/author')
                        elif block == 'team':
                            update_game_team_info(game_title, *(list(request.form.values())[1:-1]))
                            return render_template('success.html', last='../../profile/author')
                        elif block == 'authors_and_checkers':
                            game, not_found_users = update_game_authors_and_checkers_info(
                                game_title,
                                *(list(request.form.values())[
                                  1:-1]))
                            if len(not_found_users) == 0:
                                return render_template('success.html', last='../../profile/author')
                            else:
                                return render_template('users_not_found.html', users=not_found_users,
                                                       last='../../profile/author')
                        else:
                            return render_template('what_are_you_doing_here.html')
                    form.set_defaults(default)
                    return render_template('game_creator.html', form=form, default=default)
    return render_template('what_are_you_doing_here.html')


# Добавить задачу
@app.route('/add_task/', methods=['GET', 'POST'])
def add_task():
    add_task_form = AddTaskForm()
    params = dict()
    params['title'] = 'Добавить Задачу'
    params['add_task_form'] = add_task_form
    params['success'] = False

    if request.method == 'POST' and add_task_form.validate_on_submit():
        min_grade = request.form.get("min_grade")
        max_grade = request.form.get("max_grade")
        manual_check = request.form.get("manual_check")
        condition = request.form.get("condition")
        condition_images = request.files.getlist("condition_images")
        solution = request.form.get("solution")
        solution_images = request.files.getlist("solution_images")
        ans_picture = request.form.get("ans_picture")
        answer = request.form.get("answer")

        if min_grade > max_grade:
            flash("Младший класс старше Старшего класса")
            return render_template('add_task.html', **params)

        if ans_picture:
            manual_check = True

        task = Task()
        task.min_grade = min_grade
        task.max_grade = max_grade
        task.manual_check = bool(manual_check)
        task.ans_picture = bool(ans_picture)

        for ans in answer.split('|'):
            task.set_ans(ans)

        if solution:
            task.have_solution = True

        db.session.add(task)
        db.session.commit()

        task_directory = os.path.join(Config.TASKS_UPLOAD_FOLDER, f'task_{task.id}')
        condition_directory = os.path.join(task_directory, "condition")
        os.mkdir(task_directory)
        os.mkdir(condition_directory)
        with open(os.path.join(condition_directory, "condition.txt"), mode="w") as wfile:
            wfile.write(condition)

        if condition_images:
            for image in condition_images:
                if image.filename:
                    image.save(os.path.join(condition_directory, image.filename))

        if solution:
            solution_directory = os.path.join(task_directory, "solution")
            os.mkdir(solution_directory)
            with open(os.path.join(solution_directory, "solution.txt"), mode="w") as wfile:
                wfile.write(solution)

            if solution_images:
                for image in solution_images:
                    if image.filename:
                        image.save(os.path.join(solution_directory, image.filename))

        params["success"] = True
        return render_template("add_task.html", **params)

    return render_template('add_task.html', **params)


# Архив
@app.route('/archive/')
@app.route('/tasks/')
def archive():
    params = dict()
    params['title'] = 'Архив'

    tasks_table = db.session.query(Task).all().filter_by(Task.hidden == False)

    params["tasks_table"] = tasks_table

    return render_template("archive.html", **params)


# Отображение задачи
@app.route('/tasks/<int:task_id>')
def task(task_id):
    params = dict()
    params['title'] = 'Задача ' + str(task_id)

    task = db.session.query(Task).filter_by(Task.id == task_id).first()

    if not task:
        return render_template("no_task.html")

    if task.hidden:
        if is_auth():
            rights = current_user.rights.split()
            if not ('author' in rights or 'god' in rights or current_user.id == task.author_id):
                return render_template("what_are_you_doing_here.html")
        else:
            return render_template("what_are_you_doing_here.html")

    params['task'] = task

    task_directory = os.path.join(Config.TASKS_UPLOAD_FOLDER, f'task_{task.id}')
    condition_directory = os.path.join(task_directory, "condition")

    with open(os.path.join(condition_directory, "condition.txt"), mode="r") as rfile:
        condition = rfile.read()

    params["condition"] = condition

    if task.have_solution:
        params["have_solution"] = True

        solution_directory = os.path.join(task_directory, "solution")

        with open(os.path.join(solution_directory, "solution.txt"), mode="r") as rfile:
            solution = rfile.read()

        params["solution"] = solution

    return render_template("task.html", **params)


# # Всё что нужно для домино
#
# domino_start_time = datetime.datetime(2020, 6, 2, 10, 0, 30)
# domino_end_time = datetime.datetime(2020, 6, 2, 13, 0, 30)
# domino_keys = list(map(lambda x: 't' + str(x), range(1, 29)))
# domino_tasks_keys_by_names = {'0-0': 't1', '0-1': 't2', '0-2': 't3', '0-3': 't4', '0-4': 't5',
#                               '0-5': 't6',
#                               '0-6': 't7', '1-1': 't8', '1-2': 't9', '1-3': 't10', '1-4': 't11',
#                               '1-5': 't12',
#                               '1-6': 't13', '2-2': 't14', '2-3': 't15', '2-4': 't16', '2-5': 't17',
#                               '2-6': 't18',
#                               '3-3': 't19', '3-4': 't20', '3-5': 't21', '3-6': 't22', '4-4': 't23',
#                               '4-5': 't24',
#                               '4-6': 't25', '5-5': 't26', '5-6': 't27', '6-6': 't28'}
# domino_tasks_names_by_keys = {'t1': '0-0', 't2': '0-1', 't3': '0-2', 't4': '0-3', 't5': '0-4',
#                               't6': '0-5',
#                               't7': '0-6', 't8': '1-1', 't9': '1-2', 't10': '1-3', 't11': '1-4',
#                               't12': '1-5',
#                               't13': '1-6', 't14': '2-2', 't15': '2-3', 't16': '2-4', 't17': '2-5',
#                               't18': '2-6',
#                               't19': '3-3', 't20': '3-4', 't21': '3-5', 't22': '3-6', 't23': '4-4',
#                               't24': '4-5',
#                               't25': '4-6', 't26': '5-5', 't27': '5-6', 't28': '6-6'}
# domino_messages = {'full': "Вы уже взяли 2 задачи", 'af': 'Вы уже решили эту задачу',
#                    'as': 'Вы уже решили эту задачу',
#                    'fs': 'У Вас закончились попытки на сдачу этой задачи',
#                    'absent': 'На данный момент задачи с этим номером отсутсвуют',
#                    'hand': 'Вы уже взяли эту задачу',
#                    'cf': "Задача проверяется",
#                    'cs': 'Задача проверяется'}
#
# number_of_domino_task = 3
# domino_info = {'5': {}, '6': {}, '7': {}}
# for grade in ['5', '6', '7']:
#     for i in range(1, 29):
#         domino_info[grade][f't{i}'] = {'name': domino_tasks_names_by_keys[f't{i}'],
#                                        'number': number_of_domino_task}
#
#
# # Страница домино
# @app.route("/domino", methods=["GET", "POST"])
# def domino():
#     # Если пользователь не вошёл в аккаунт команды/игрока, то мы сообщаем ему об этом
#
#     if not is_auth():
#         return render_template("not_authenticated.html")
#
#     team = current_user.team_name
#     grade = str(current_user.grade)
#     # Если игра ещё не началась, то мы показывает отсчёт до начала
#     if game_status('domino', time) == 'not_started':
#         start_time = f"{domino_start_time.month} {domino_start_time.day} {domino_start_time.year} "
#         start_time += f"{domino_start_time.hour}:{domino_start_time.minute}:{domino_start_time.second}"
#         now_time = f"{time.month} {time.day} {time.year} "
#         now_time += f"{time.hour}:{time.minute}:{time.second}"
#         return render_template("domino.html", title="Домино ТЮМ72", state='not started',
#                                start_time=start_time, now_time=now_time)
#     # Если игра уже закончилась то мы сообщаем об этом
#     elif game_status('domino', time) == 'ended':
#         return render_template("domino.html", title="Домино ТЮМ72", state='ended')
#     # Иначе отображаем игру
#     else:
#         update_visited_status(team, 'domino')
#         # Время окончание игры
#         end_time = f"{domino_end_time.month} {domino_end_time.day} {domino_end_time.year} "
#         end_time += f"{domino_end_time.hour}:{domino_end_time.minute}:{domino_end_time.second}"
#         now_time = f"{time.month} {time.day} {time.year} "
#         now_time += f"{time.hour}:{time.minute}:{time.second}"
#         print(end_time, 'end_time')
#         # Игра в процессе
#         state = 'in progress'
#         # Формируем информацию о состоянии задач у пользователя
#         tasks = {}
#         for key in domino_keys:
#             tasks[key] = {'name': domino_info[grade][key]['name'],
#                           'state': get_task_state('domino_tasks', key, team, grade),
#                           'manual_check': get_manual_check('domino', grade,
#                                                            domino_tasks_names_by_keys[key]),
#                           'ans_picture': get_ans_picture('domino', grade,
#                                                          domino_tasks_names_by_keys[key])}
#         # Обновляем состояние задач, которые закончились/появились на "игровом столе"
#         for key in domino_keys:
#             if get_state(tasks[key]['state']) == 'ok' and domino_info[grade][key]['number'] == 0:
#                 tasks[key]['state'] = '0bo'
#             elif get_state(tasks[key]['state']) == 'ff' and domino_info[grade][key]['number'] == 0:
#                 tasks[key]['state'] = '0bf'
#             elif get_state(tasks[key]['state']) == 'bo' and domino_info[grade][key]['number'] > 0:
#                 tasks[key]['state'] = '0ok'
#             elif get_state(tasks[key]['state']) == 'bf' and domino_info[grade][key]['number'] > 0:
#                 tasks[key]['state'] = '0ff'
#         # Формируем информацию о задачах, которые сейчас "на руках" у пользователя
#         keys_of_picked_tasks = get_task_state('domino_tasks', 'picked_tasks', team, grade).split()
#         picked_tasks = []
#         for key in keys_of_picked_tasks:
#             picked_tasks.append(
#                 {'name': domino_tasks_names_by_keys[key],
#                  'content': str(get_task('domino', int(grade), domino_tasks_names_by_keys[key])),
#                  'manual_check': get_manual_check('domino', grade, domino_tasks_names_by_keys[key]),
#                  'ans_picture': get_ans_picture('domino', grade, domino_tasks_names_by_keys[key])})
#         print(picked_tasks)
#         # Если пользователь просто загрузил страницу игры то показывает её ему
#         if request.method == "GET":
#             return render_template("domino.html", title="Домино ТЮМ72", block="", tasks=tasks,
#                                    keys=domino_keys,
#                                    picked_tasks=picked_tasks, message=False, info=domino_info[grade],
#                                    state=state, end_time=end_time, now_time=now_time,
#                                    number_of_picked_tasks=len(picked_tasks))
#         # Иначе пользователь сдал или взял "на руки" задачу
#         elif request.method == "POST":
#             # Сообщение об ошибке
#             # Если пользователь попытался взять задачу
#             print(request.form)
#             if request.form.get("picked"):
#                 print('whatwhat')
#                 key = domino_tasks_keys_by_names[request.form.get("picked")]
#                 number_of_picked_task = len(picked_tasks)
#                 # У пользователя уже 2 задачи "на руках", сообщаем, что больше взять нельзя
#                 if number_of_picked_task == 2:
#                     message = domino_messages['full']
#                 # Выбранная задача уже "на руках" у пользователя, сообщаем об этом
#                 elif key in keys_of_picked_tasks:
#                     message = domino_messages['hand']
#                 # Пользователь может взять задачу, выдаём её
#                 elif get_state(tasks[key]['state']) in ['ff', 'ok']:
#                     picked_tasks.append(key)
#                     keys_of_picked_tasks.append(key)
#                     picked_tasks.append(
#                         {'name': domino_tasks_names_by_keys[key],
#                          'content': str(
#                              get_task('domino', int(grade), domino_tasks_names_by_keys[key])),
#                          'manual_check': get_manual_check('domino', grade,
#                                                           domino_tasks_names_by_keys[key]),
#                          'ans_picture': get_ans_picture('domino', grade,
#                                                         domino_tasks_names_by_keys[key])})
#                     domino_info[grade][key]['number'] -= 1
#                 # Пользователь не может взять задачу по другой причине, сообщаем причину
#                 else:
#                     message = domino_messages[get_state(tasks[key]['state'])]
#             # Пользователь сдаёт задачу
#             elif request.form.get('answer'):
#                 key = domino_tasks_keys_by_names[request.form.get('name')]
#                 verdicts = ['ok', 'ff', 'fs']
#                 # Если всё нормально и пользователь не попытался багануть сайт
#                 if get_state(tasks[key]['state']) in ['ok', 'ff'] and key in keys_of_picked_tasks:
#                     result = check_task('domino', grade, domino_tasks_names_by_keys[key],
#                                         request.form.get('answer'))
#                     # Если пользователь решил задачу с первой попытки
#                     if result and get_state(tasks[key]['state']) == 'ok':
#                         tasks[key]['state'] = str(
#                             sum(map(int, domino_info[grade][key]['name'].split('-')))) + 'af'
#                         if tasks[key]['name'] == '0-0':
#                             tasks[key]['state'] = '10af'
#                     # Если пользователь решил задачу со второй попытки
#                     elif result:
#                         tasks[key]['state'] = str(
#                             max(map(int, domino_info[grade][key]['name'].split('-')))) + 'as'
#                     # Если пользователь решил задачу неправильно
#                     else:
#                         tasks[key]['state'] = verdicts[
#                             verdicts.index(get_state(tasks[key]['state'])) + 1]
#                         if tasks[key]['state'] == 'ff':
#                             tasks[key]['state'] = '0ff'
#                         else:
#                             tasks[key]['state'] = str(
#                                 -min(map(int, domino_info[grade][key]['name'].split('-')))) + 'fs'
#                         if tasks[key]['name'] == '0-0':
#                             tasks[key]['state'] = '0fs'
#                     # Обновление бд, возвращение задачи на "игровой стол"
#                     update_results('domino_tasks', get_point(tasks[key]['state']), team, grade)
#                     update('domino_tasks', key, tasks[key]['state'], team, grade)
#                     print('hah')
#                     keys_of_picked_tasks.remove(key)
#                     picked_tasks = []
#                     for key in keys_of_picked_tasks:
#                         picked_tasks.append(
#                             {'name': domino_tasks_names_by_keys[key],
#                              'content': str(
#                                  get_task('domino', int(grade), domino_tasks_names_by_keys[key])),
#                              'manual_check': get_manual_check('domino', grade,
#                                                               domino_tasks_names_by_keys[key]),
#                              'ans_picture': get_ans_picture('domino', grade,
#                                                             domino_tasks_names_by_keys[key])})
#                     domino_info[grade][key]['number'] += 1
#             update('domino_tasks', 'picked_tasks', " ".join(keys_of_picked_tasks), team, grade)
#             # Обновление страницы
#             return render_template("domino.html", title="Домино ТЮМ72", block="", tasks=tasks,
#                                    keys=domino_keys, picked_tasks=picked_tasks, message=message,
#                                    info=domino_info[grade], state=state, end_time=end_time,
#                                    number_of_picked_tasks=len(picked_tasks), now_time=now_time)
#
#
# penalty_keys = list(map(lambda x: 't' + str(x), range(1, 17)))
# penalty_info = {}
# for grade in ['5', '6', '7']:
#     penalty_info[grade] = {}
#     for key in penalty_keys:
#         penalty_info[grade][key] = {'name': key[1:], 'cost': 15}
# stupid_crutch = 0
# NUMBER_OF_PENALTY_TASKS_SETS = 2
# penalty_start_time = datetime.datetime(2020, 6, 3, 10, 0, 30)
# penalty_end_time = datetime.datetime(2020, 6, 3, 13, 0, 30)
# penalty_messages = {'accepted': 'Вы уже решили эту задачу',
#                     'failed': 'У вас закончились попытки на сдачу этой задачи'}
#
#
# # Страница пенальти
# @app.route('/penalty', methods=["GET", "POST"])
# def penalty():
#     global penalty_info, stupid_crutch, NUMBER_OF_PENALTY_TASKS_SETS
#     if stupid_crutch == 0:
#         for grade in ['5', '6', '7']:
#             penalty_info[grade] = {}
#             for key in penalty_keys:
#                 content = str(get_task('penalty', grade, key[1:]))
#                 number = NUMBER_OF_PENALTY_TASKS_SETS
#                 penalty_info[grade][key] = {'name': key[1:], 'cost': 15, 'content': content,
#                                             'number': number}
#     stupid_crutch += 1
#     # Если пользователь не вошёл в аккаунт команды/игрока, то мы сообщаем ему об этом
#     if not is_auth():
#         return render_template("not_authenticated.html")
#
#     # Если пользователь нарушил правила, то мы сообщаем ему об этом
#
#     if get_cheater_status(current_user.team_name, 'penalty'):
#         return render_template("cheater.html")
#
#     # Если мы забанили команду
#
#     if get_cur_user().is_banned:
#         return render_template("you_are_banned.html", title="Вас дисквалифицировали")
#
#     team = current_user.team_name
#     grade = str(current_user.grade)
#     time = datetime.datetime.now() + datetime.timedelta(hours=5)
#
#     # Если игра ещё не началась, то мы показывает отсчёт до начала
#     if game_status('penalty', time) == 'not_started':
#         print('what')
#         start_time = f"{penalty_start_time.month} {penalty_start_time.day} {penalty_start_time.year} "
#         start_time += f"{penalty_start_time.hour}:{penalty_start_time.minute}:{penalty_start_time.second}"
#         now_time = f"{time.month} {time.day} {time.year} "
#         now_time += f"{time.hour}:{time.minute}:{time.second}"
#         return render_template("penalty.html", title="Пенальти ТЮМ72", state='not started',
#                                start_time=start_time, now_time=now_time)
#     # Если игра уже закончилась то мы сообщаем об этом
#     elif game_status('penalty', time) == 'ended':
#         return render_template("penalty.html", title="Пенальти ТЮМ72", state='ended')
#     # Иначе отображаем игру
#     else:
#         update_visited_status(team, 'penalty')
#         end_time = f"{penalty_end_time.month} {penalty_end_time.day} {penalty_end_time.year} "
#         end_time += f"{penalty_end_time.hour}:{penalty_end_time.minute}:{penalty_end_time.second}"
#         now_time = f"{time.month} {time.day} {time.year} "
#         now_time += f"{time.hour}:{time.minute}:{time.second}"
#         state = 'in progress'
#         tasks = {}
#         # Формируем информацию о состоянии задач пользователя
#         for key in penalty_keys:
#             tasks[key] = {'name': key[1:],
#                           'state': get_task_state('penalty_tasks', key, team, grade),
#                           'manual_check': get_manual_check('penalty', grade, key[1:]),
#                           'ans_picture': get_ans_picture('penalty', grade, key[1:])
#                           }
#         # Если пользователь сдал задачу
#         if request.method == "POST":
#             key = 't' + request.form.get('name')
#             verdicts = ['ok', 'ff', 'fs']
#             # Если пользователь не попытался багануть сайт
#             if get_state(tasks[key]['state']) in ['ok', 'ff']:
#                 result = check_task('penalty', grade, key[1:], request.form.get('answer'))
#                 # Если пользователь сдал задачу правильно
#                 if result:
#                     # Если пользователь сдал задачу правильно с первой попытки
#                     if get_state(tasks[key]['state']) == 'ok':
#                         tasks[key]['state'] = str(penalty_info[grade][key]['cost']) + 'af'
#                         penalty_info[grade][key]['number'] -= 1
#                         if penalty_info[grade][key]['cost'] > 5:
#                             if penalty_info[grade][key]['number'] == 0:
#                                 penalty_info[grade][key]['cost'] -= 1
#                                 penalty_info[grade][key]['number'] = NUMBER_OF_PENALTY_TASKS_SETS
#                     # Если пользователь сдал задачу правильно со второй попытки
#                     else:
#                         tasks[key]['state'] = '3' + 'as'
#                 # Если пользователь сдал задачу неправильно
#                 else:
#                     tasks[key]['state'] = verdicts[
#                         verdicts.index(get_state(tasks[key]['state'])) + 1]
#                     if tasks[key]['state'] == 'ff':
#                         tasks[key]['state'] = '0' + 'ff'
#                     else:
#                         tasks[key]['state'] = '-2' + 'fs'
#                 # обновление бд
#                 update_results('penalty_tasks', get_point(tasks[key]['state']), team, grade)
#                 update('penalty_tasks', key, tasks[key]['state'], team, grade)
#         # отображение страницы
#         return render_template("penalty.html", title="Пенальти ТЮМ72", tasks=tasks,
#                                keys=penalty_keys,
#                                info=penalty_info[grade], state=state, end_time=end_time,
#                                now_time=now_time)


''' ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ '''


def allowed_text_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Consts.ALLOWED_TEXT_EXTENSIONS


def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Consts.ALLOWED_IMAGE_EXTENSIONS


def rename_file(filename_old, filename_new):
    ext = filename_old.rsplit('.', 1)[1].lower()
    return '.'.join((filename_new, ext))


def get_extension(filename):
    if '.' not in filename:
        return ""

    return filename.rsplit('.', 1)[1].lower()


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == user_id).first()


# Функция возвращает True если пользователь авторизован, иначе False

def is_auth():
    return current_user.is_authenticated


from app import forms

DICT_OF_FORMS = {'tasks': forms.GameTasksInfoForm,
                 'common': forms.GameCommonInfoForm,
                 'team': forms.GameTeamInfoForm,
                 'authors_and_checkers': forms.GameAuthorsAndCheckersInfoForm}
