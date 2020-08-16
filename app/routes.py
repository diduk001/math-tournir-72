# -*- coding: utf-8 -*-
import os
import os.path

from flask import render_template, request, flash, redirect, jsonify
from flask_login import logout_user, current_user, login_user
from datetime import datetime

from app import app
from app import login_manager
from app.forms import *
from app.game_creator import *
from config import Config, Constants


# Главная страница
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    params = dict()
    params['title'] = 'ТЮМ 72'
    params['is_teacher'] = False
    if is_auth() and current_user.is_teacher:
        params['form'] = CreateTeamForm()
        params['is_teacher'] = True
        if params['form'].validate_on_submit():
            title = request.form.get('title')
            grade = request.form.get('grade')
            login = request.form.get('login')
            password = request.form.get('password')
            password_again = request.form.get('password_again')
            if password != password_again:
                return render_template('error.html', message='Пароли не соовпадают', last='/')
            if db.session.query(Team).filter(Team.title == title).first() is not None:
                return render_template('team_already_exists.html', attribute='названием', value=title, last='/')
            if db.session.query(Team).filter(Team.login == login).first() is not None:
                return render_template('team_already_exists.html', attribute='логином', value=login, last='/')
            team = Team(title, grade, login)
            team.set_password(password)
            db.session.add(team)
            current_user.managed_teams.append(team)
            team.teacher.append(current_user)
            db.session.commit()
            register_to_game(f"ТЮМ72 Домино {grade} класс", team.id)
            register_to_game(f"ТЮМ72 Пенальти {grade} класс", team.id)
            return render_template('success.html', last='../')
    elif is_auth():
        params['grade'] = current_user.grade
    return render_template('index.html', **params)

# П₽@Вi/\@
@app.route('/rules/')
def rules():
    return render_template("rules.html")

# Регистрация
@app.route('/sign_up/<role>', methods=['GET', 'POST'])
def sign_up(role):
    if role == 'Student':
        sign_up_form = SignUpStudentForm()
    elif role == 'Teacher':
        sign_up_form = SignUpTeacherForm()
    else:
        return render_template('what_are_you_doing_here.html')
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
        if role == 'Student':
            user = User(
                'Student',
                {'login': request.form.get("login"),
                 'name':  request.form.get("name"),
                 'surname': request.form.get("surname"),
                 'last_name': request.form.get('last_name'),
                 'grade': int(request.form.get("grade")),
                 'school': request.form.get("school"),
                 'teachers': request.form.get("teachers"),
                 'info': request.form.get("info")}
            )
        elif role == 'Teacher':
            user = User(
                'Teacher',
                {'login': request.form.get('login'),
                 'name': request.form.get('name'),
                 'surname': request.form.get('surname'),
                 'last_name': request.form.get('last_name'),
                 'work_place': request.form.get('work_place'),
                 'phone_number': request.form.get('phone_number')}
            )
        if request.form.get('password') != request.form.get('password_again'):
            return render_template('error.html', message='Пароли не совпадают', last=f'../../sign_up/{role}')
        user.set_password(request.form.get("password"))
        user.set_email(request.form.get("email"))
        # Добавление пользователя в базы данных

        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)
        return redirect("/")

    return render_template("sign_up_user.html", **params)


# Страница для авторизации
@app.route('/login/', methods=['GET', 'POST'])
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


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/login')


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
            last_name = current_user.last_name
            school = current_user.school
            grade = current_user.grade
            login = current_user.login
            is_teacher = current_user.is_teacher
            dict_of_rights = {'god': 'Выдать набор прав',
                              'moderator': 'Заблокировать/Разблокировать пользователя',
                              'author': 'Игры',
                              'user': 'Команды',
                              'checker': 'Проверка'}
            rights = (current_user.rights + (' checker' if len(current_user.checkering) > 0 else ' ')).split()
            if section == 'common':
                return render_template("profile.html", name=name, surname=surname, last_name=last_name, school=school,
                                       grade=grade, login=login, rights=rights, dict_of_rights=dict_of_rights,
                                       is_teacher=is_teacher)
            # Если пользователь перешёл в раздел в который ему можно перейти
            elif section in rights:
                # Если раздел "Пользователь" то возвращаем команды, в кототрых пользователь состоит/ которыми руководит
                if section == 'user':
                    formatted_teams = []

                    if is_teacher:
                        form = MakeCaptainForm()
                        not_formatted_teams = current_user.managed_teams
                    else:
                        form = EnterTeamForm()
                        not_formatted_teams = current_user.teams
                    if form.validate_on_submit():
                        if is_teacher:
                            player_login = request.form.get('login')
                            team_title = request.form.get('team_title')
                            team = db.session.query(Team).filter(Team.title == team_title).first()
                            if team is None:
                                return render_template('error.html',
                                                       message="Команды с таким названием не существует",
                                                       last='../profile/user')
                            if team not in current_user.managed_teams:
                                return render_template('error.html',
                                                       message='Вы не являетесь руководителем указанной команды',
                                                       last='../profile/user')
                            player = db.session.query(User).filter(User.login == player_login).first()
                            if player is None:
                                return render_template('error.html',
                                                       message='Пользователя с таким логином не существует',
                                                       last='../profile/user')
                            if player.is_teacher:
                                return render_template('error.html',
                                                       message='Указанный пользователь не является учеником',
                                                       last='../profile/user')
                            if player not in team.members:
                                return render_template('error.html',
                                                       message='Указанный игрок не состоит в указанной команде',
                                                       last='../profile/user')
                            if len(team.captain) != 0:
                                captain = team.captain
                                captain.captaining.delete(team)
                                team.captain.delete(captain)
                            player.captaining.append(team)
                            db.session.commit()
                            return render_template('success.html', last='../profile/user')
                        else:
                            login = request.form.get('login')
                            password = request.form.get('password')
                            team = db.session.query(Team).filter(Team.login == login).first()
                            if team is None:
                                return render_template('team_not_found.html', login=login, last='../profile/user')
                            if not team.check_password(password):
                                return render_template('wrong_password.html', last='../profile/user')
                            if str(team.grade) != str(current_user.grade):
                                return render_template('error.html', message='Ваш класс не соответсвует классу команды',
                                                       last='../profile/user')
                            team.members.append(current_user)
                            db.session.commit()
                            return render_template('success.html', last='../profile/user')
                    for team in not_formatted_teams:
                        formatted_team = dict()
                        formatted_team['title'] = team.title
                        formatted_team['grade'] = team.grade
                        formatted_team['captain'] = '-'
                        formatted_team['members'] = []
                        for player in team.members:
                            formatted_team['members'].append({'login': player.login,
                                                              'name': player.name,
                                                              'surname': player.surname,
                                                              'last_name': player.last_name})
                        if len(team.captain) > 0:
                            formatted_team['captain'] = f"{team.captain[0].name} {team.captain[0].surname}" \
                                                        f" {team.captain[0].last_name}"
                        formatted_team['size'] = len(formatted_team['members'])
                        formatted_teams.append(formatted_team)
                    return render_template("profile_teams.html", name=name, surname=surname, last_name=last_name,
                                           school=school, grade=grade, login=login, rights=rights,
                                           dict_of_rights=dict_of_rights, teams=formatted_teams, is_teacher=is_teacher,
                                           form=form)
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
                    return render_template('profile_god.html', name=name, surname=surname, last_name=last_name,
                                           school=school, grade=grade, rights=rights, login=login,
                                           dict_of_rights=dict_of_rights, form=form, is_teacher=is_teacher)
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
                    return render_template('profile_moderator.html', name=name, surname=surname, last_name=last_name,
                                           school=school, grade=grade, rights=rights, login=login,
                                           dict_of_rights=dict_of_rights, ban_form=ban_form, pardon_form=pardon_form,
                                           is_teacher=is_teacher)
                # Если раздел "Автор", то возвращаем профиль с ссылкой на создание игр, отображаем все игры и их
                elif section == 'author':
                    # Список с играми
                    games = []
                    # Добавление игр в список с играми
                    for game in current_user.authoring:
                        new_game = {'common': get_game_common_info_human_format(game.title),
                                    'tasks': get_game_tasks_info_human_format(game.title),
                                    'tasks_positions': get_game_tasks_positions(game.title),
                                    'authors_and_checkers': get_game_authors_and_checkers_info_human_format(
                                        game.title)}
                        if new_game['common'][5][1] == 'командная':
                            new_game['team'] = get_game_team_info_human_format(game.title)
                        else:
                            new_game['team'] = [('Минимальный размер команды', '-'),
                                                ('Максимальный размер команды', '-')]
                        games.append(new_game)
                    return render_template('profile_author.html', name=name, surname=surname, last_name=last_name,
                                           school=school, grade=grade, rights=rights, login=login,
                                           dict_of_rights=dict_of_rights, games=games, is_teacher=is_teacher)
                elif section == 'checker':
                    checkering_games = list(map(lambda x: x.title, current_user.checkering))
                    return render_template('profile_checker.html', name=name, surname=surname, last_name=last_name,
                                           school=school, grade=grade, rights=rights, login=login,
                                           dict_of_rights=dict_of_rights, games=checkering_games, is_teacher=is_teacher)
                else:
                    return render_template('what_are_you_doing_here.html')
            else:
                return render_template('what_are_you_doing_here.html')
        else:
            # Иначе переправляем на вход
            return redirect("/login")
    elif debug_var == 1:
        return redirect("/login")


# Лента новостей
# @app.route("/article/<section>", methods=["GET"])
# def article(section):
#     if section == 'common':
#         games = db.session.query(Game).filter(True).all()
#         formated_games = []
#         for game in games:
#             new_formated_game = {'title': game.title,
#                                  'grade': game.grade,
#                                  'game_type': Constants.DICT_OF_HUMAN_FORMAT[game.game_type],
#                                  'start_time': game.start_time,
#                                  'end_time': game.end_time,
#                                  'game_format': Constants.DICT_OF_HUMAN_FORMAT[game.game_format],
#                                  'info': game.info,
#                                  'max_team_size': game.max_team_size,
#                                  'min_team_size': game.min_team_size
#                                  }
#             formated_games.append(new_formated_game)
#         return render_template('news.html', games=formated_games)
#     else:
#         game = db.session.querry(Game).filter(Game.title == section).first()
#         if game is None:
#             return render_template('what_are_you_doing_here.html')
#         else:
#             new_formated_game = {'title': game.title,
#                                  'grade': game.grade,
#                                  'game_type': Constants.DICT_OF_HUMAN_FORMAT[game.game_type],
#                                  'start_time': game.start_time,
#                                  'end_time': game.end_time,
#                                  'game_format': Constants.DICT_OF_HUMAN_FORMAT[game.game_format],
#                                  'info': game.info,
#                                  'max_team_size': game.max_team_size,
#                                  'min_team_size': game.min_team_size
#                                  }
#             return render_template('game_news.html', game=new_formated_game)

# Создание игры
@app.route('/create_game_form/', methods=['POST', 'GET'])
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
                if db.session.query(Game).filter(Game.title == title).first() is not None:
                    return render_template('error.html', message='Игра с таким названием уже существует',
                                           last='/profile/author')
                create_game(title, grade, game_type, start_time, end_time, game_format, privacy,
                            info, current_user)
                return render_template('success.html', last='/profile/author')
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
@app.route('/add_task/<game_title>/<task_position>/<current_value>', methods=['GET', 'POST'])
def add_task(game_title, task_position, current_value):
    if is_auth() and 'author' in current_user.rights.split():
        add_task_form = AddTaskForm()
        params = dict()
        params['title'] = 'Добавить Задачу'
        params['add_task_form'] = add_task_form
        params['success'] = False
        if request.method == 'POST' and add_task_form.validate_on_submit():
            game = db.session.query(Game).filter(Game.title == game_title).first()
            if game is None:
                return render_template('what_are_you_doing_here.html')
            min_grade = request.form.get("min_grade")
            max_grade = request.form.get("max_grade")
            manual_check = request.form.get("manual_check")
            hidden = request.form.get("hidden")
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
            task.hidden = bool(hidden)
            task.ans_picture = bool(ans_picture)

            for ans in answer.split('|'):
                task.set_ans(ans)

            if solution:
                task.have_solution = True

            db.session.add(task)
            db.session.commit()

            task_directory = os.path.join(Config.TASKS_UPLOAD_FOLDER, f'task_{task.id}')
            condition_directory = os.path.join(task_directory, "condition")
            os.makedirs(task_directory)
            os.makedirs(condition_directory)
            with open(os.path.join(condition_directory, "condition.txt"), mode="w") as wfile:
                wfile.write(condition)

            if condition_images:
                for image in condition_images:
                    if image.filename:
                        image.save(os.path.join(condition_directory, image.filename))

            if solution:
                solution_directory = os.path.join(task_directory, "solution")
                os.makedirs(solution_directory)
                with open(os.path.join(solution_directory, "solution.txt"), mode="w") as wfile:
                    wfile.write(solution)

                if solution_images:
                    for image in solution_images:
                        if image.filename:
                            image.save(os.path.join(condition_directory, image.filename))
            tasks_positions = list(map(lambda x: x.split(':'), game.tasks_positions.split('|')))
            tasks_positions[tasks_positions.index([task_position, current_value])] = (task_position, str(task.id))
            game.tasks_positions = '|'.join(list(map(lambda x: ':'.join(x), tasks_positions)))
            db.session.commit()
            params["success"] = True
            return render_template("add_task.html", **params)
        return render_template('add_task.html', **params)
    return render_template('what_are_you_doing_here.html')


# Архив
@app.route('/archive/')
@app.route('/tasks/')
def archive():
    params = dict()
    params['title'] = 'Архив'

    tasks_table = db.session.query(Task).filter(Task.hidden == False)

    params["tasks_table"] = tasks_table

    return render_template("archive.html", **params)


# Отображение задачи
@app.route('/tasks/<int:task_id>')
def task(task_id):
    params = dict()
    params['title'] = 'Задача ' + str(task_id)

    task = db.session.query(Task).filter(Task.id == task_id).first()

    if not task:
        return render_template("no_task.html")

    if task.hidden:
        if is_auth():
            rights = current_user.rights.split()
            if not (current_user.id == task.author_id or 'god' in rights):
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


# Страница домино
@app.route("/domino/<game_title>", methods=["GET", "POST"])
def domino(game_title):
    # Если пользователь не вошёл в аккаунт команды/игрока, то мы сообщаем ему об этом
    game = db.session.query(Game).filter(Game.title == game_title).first()
    if game is None:
        return render_template('what_are_you_doing_here.html')
    if not is_auth():
        return render_template("not_authenticated.html")
    current_team = None
    is_member = False
    if game.game_type == 'personal':
        current_team = current_user
    else:
        for team in current_user.captaining:
            if game in team.games:
                current_team = team
        if current_team is None:
            for team in current_user.teams:
                if game in team.games:
                    is_member = True
                    current_team = team
        if current_team is None:
            return render_template('error.html', message='Ваша команда не зарегистрирована на игру', last='../../')
        if len(current_team.members) > game.max_team_size:
            return render_template('error.html', message='Размер вашей команды больше допустимого игрой', last='../../')
    # Если игра ещё не началась, то мы показывает отсчёт до начала
    time = datetime.now()
    status = get_game_status(game_title, time)
    if status == 'not started':
        start_time = datetime.strftime(datetime.strptime(game.start_time, Consts.TIME_FORMAT_FOR_HUMAN),
                                       Consts.TIME_FORMAT_FOR_JS)
        now_time = datetime.strftime(time, Consts.TIME_FORMAT_FOR_JS)
        return render_template("domino.html", title=f'{game_title}', status=status,
                               start_time=start_time, now_time=now_time)
    # Если игра уже закончилась то мы сообщаем об этом
    elif status == 'ended':
        return render_template("domino.html", title=f"{game_title}", status=status)
    # Иначе отображаем игру
    else:
        # Время окончание игры
        end_time = datetime.strftime(datetime.strptime(game.end_time, Consts.TIME_FORMAT_FOR_HUMAN),
                                     Consts.TIME_FORMAT_FOR_JS)
        now_time = datetime.strftime(time, Consts.TIME_FORMAT_FOR_JS)
        message = None
        # Формируем информацию о состоянии задач у пользователя
        tasks_positions = []
        for task_position in game.tasks_positions.split('|'):
            position, task_id = task_position.split(':')
            task = db.session.query(Task).filter(Task.id == int(task_id)).first()
            tasks_positions.append([position, task])
        tasks_positions = dict(tasks_positions)
        tasks = {}
        tasks_states = get_tasks_info('states', game.id, login=current_team.login)
        numbers_of_sets = get_tasks_info('numbers_of_sets', game.id)
        changes_numbers_of_sets = dict()
        changes_tasks_states = dict()
        for key in Consts.TASKS_KEYS['domino']:
            tasks[key] = {'name': Consts.TASKS_POSITIONS_BY_KEYS['domino'][key],
                          'state': tasks_states[key],
                          'manual_check': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].manual_check,
                          'ans_picture': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].ans_picture}
        # Обновляем состояние задач, которые закончились/появились на "игровом столе"
        for key in Consts.TASKS_KEYS['domino']:
            if get_state(tasks[key]['state']) == 'ok' and numbers_of_sets[key]['number_of_sets'] == 0:
                tasks[key]['state'] = '0bo'
            elif get_state(tasks[key]['state']) == 'ff' and numbers_of_sets[key]['number_of_sets'] == 0:
                tasks[key]['state'] = '0bf'
            elif get_state(tasks[key]['state']) == 'bo' and numbers_of_sets[key]['number_of_sets'] > 0:
                tasks[key]['state'] = '0ok'
            elif get_state(tasks[key]['state']) == 'bf' and numbers_of_sets[key]['number_of_sets'] > 0:
                tasks[key]['state'] = '0ff'
        # Формируем информацию о задачах, которые сейчас "на руках" у пользователя
        keys_of_picked_tasks = tasks_states['picked_tasks']
        picked_tasks = []
        for key in keys_of_picked_tasks:
            picked_tasks.append(
                {'id': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].id,
                 'name': Consts.TASKS_POSITIONS_BY_KEYS['domino'][key],
                 'condition': get_condition(tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].id),
                 'manual_check': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].manual_check,
                 'ans_picture': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].ans_picture})

        # Если пользователь просто загрузил страницу игры то показывает её ему
        if request.method == "GET":
            return render_template("domino.html", title=f'{game_title}', block="", tasks=tasks,
                                   keys=Consts.TASKS_KEYS['domino'], picked_tasks=picked_tasks, message=False,
                                   state=status, end_time=end_time, now_time=now_time,
                                   number_of_picked_tasks=len(picked_tasks), is_member=is_member)
        # Иначе пользователь сдал или взял "на руки" задачу
        elif request.method == "POST":
            # Сообщение об ошибке
            # Если пользователь попытался взять задачу
            if request.form.get("picked") and not is_member:
                key = Consts.TASKS_KEYS_BY_POSITIONS['domino'][request.form.get("picked")]
                number_of_picked_task = len(picked_tasks)
                # У пользователя уже 2 задачи "на руках", сообщаем, что больше взять нельзя
                if number_of_picked_task == 2:
                    message = Consts.MESSAGES['domino']['full']
                # Выбранная задача уже "на руках" у пользователя, сообщаем об этом
                elif key in keys_of_picked_tasks:
                    message = Consts.MESSAGES['domino']['full']
                # Пользователь может взять задачу, выдаём её
                elif get_state(tasks[key]['state']) in ['ff', 'ok']:
                    keys_of_picked_tasks.append(key)
                    changes_tasks_states['picked_tasks'] = ' '.join(keys_of_picked_tasks)
                    picked_tasks.append(
                        {'id': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].id,
                         'name':Consts.TASKS_POSITIONS_BY_KEYS['domino'][key],
                         'condition': get_condition(tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].id),
                         'manual_check': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].manual_check,
                         'ans_picture': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].ans_picture})
                    if key not in changes_numbers_of_sets.keys():
                        changes_numbers_of_sets[key] = dict()
                    changes_numbers_of_sets[key]['number_of_sets'] = numbers_of_sets[key]['number_of_sets'] - 1
                # Пользователь не может взять задачу по другой причине, сообщаем причину
                else:
                    message = Consts.MESSAGES['domino'][get_state(tasks[key]['state'])]
            # Пользователь сдаёт задачу
            elif request.form.get('answer') and not is_member:
                key = Consts.TASKS_KEYS_BY_POSITIONS['domino'][request.form.get('name')]
                verdicts = ['ok', 'ff', 'fs']
                # Если всё нормально и пользователь не попытался багануть сайт
                if get_state(tasks[key]['state']) in ['ok', 'ff'] and key in keys_of_picked_tasks:
                    result = tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].check_ans(request.form.get('answer'))
                    # Если пользователь решил задачу с первой попытки
                    if result and get_state(tasks[key]['state']) == 'ok':
                        tasks[key]['state'] = str(
                            sum(map(int, tasks[key]['name'].split('-')))) + 'af'
                        if tasks[key]['name'] == '0-0':
                            tasks[key]['state'] = '10af'
                    # Если пользователь решил задачу со второй попытки
                    elif result:
                        tasks[key]['state'] = str(
                            max(map(int, tasks[key]['name'].split('-')))) + 'as'
                    # Если пользователь решил задачу неправильно
                    else:
                        tasks[key]['state'] = verdicts[
                            verdicts.index(get_state(tasks[key]['state'])) + 1]
                        if tasks[key]['state'] == 'ff':
                            tasks[key]['state'] = '0ff'
                        else:
                            tasks[key]['state'] = str(
                                -min(map(int, tasks[key]['name'].split('-')))) + 'fs'
                        if tasks[key]['name'] == '0-0':
                            tasks[key]['state'] = '0fs'
                    # Обновление бд, возвращение задачи на "игровой стол"
                    keys_of_picked_tasks.remove(key)
                    picked_tasks = []
                    changes_tasks_states['picked_tasks'] = ' '.join(keys_of_picked_tasks)
                    changes_tasks_states[key] = tasks[key]['state']
                    for key in keys_of_picked_tasks:
                        picked_tasks.append(
                            {'id': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].id,
                             'name': Consts.TASKS_POSITIONS_BY_KEYS['domino'][key],
                             'condition': get_condition(
                                 tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].id),
                             'manual_check': tasks_positions[
                                 Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].manual_check,
                             'ans_picture': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['domino'][key]].ans_picture})

                    if key not in changes_numbers_of_sets.keys():
                        changes_numbers_of_sets[key] = dict()
                    changes_numbers_of_sets[key]['number_of_sets'] = numbers_of_sets[key]['number_of_sets'] + 1
            update_tasks_info('states', game.id, changes_tasks_states, login=current_team.login)
            update_tasks_info('numbers_of_sets', game.id, changes_numbers_of_sets)
            return jsonify({'hah':'hah'})
        else:
            return render_template('error.html', message='У вас нет прав на сдачу задач', last=f'../domino/{game_title}')
            # Обновление страницы


# Страница пенальти
@app.route('/penalty/<game_title>', methods=["GET", "POST"])
def penalty(game_title):
    # Если пользователь не вошёл в аккаунт команды/игрока, то мы сообщаем ему об этом
    game = db.session.query(Game).filter(Game.title == game_title).first()
    if game is None:
        return render_template('what_are_you_doing_here.html')
    if not is_auth():
        return render_template("not_authenticated.html")
    current_team = None
    is_member = False
    for team in current_user.captaining:
        if game in team.games:
            current_team = team
    if current_team is None:
        for team in current_user.teams:
            if game in team.games:
                is_member = True
                current_team = team
    if current_team is None:
        return render_template('error.html', message='Ваша команда не зарегистрирована на игру или Вы не являетесь её'
                                                     'капитаном', last='../../')
    if len(current_team.members) > game.max_team_size:
        return render_template('error.html', message='Размер вашей команды больше допустимого игрой', last='../../')
    # Если игра ещё не началась, то мы показывает отсчёт до начала
    time = datetime.now()
    status = get_game_status(game_title, time)
    print(status)
    if status == 'not started':
        start_time = datetime.strftime(datetime.strptime(game.start_time, Consts.TIME_FORMAT_FOR_HUMAN),
                                       Consts.TIME_FORMAT_FOR_JS)
        now_time = datetime.strftime(time, Consts.TIME_FORMAT_FOR_JS)
        return render_template("penalty.html", title=f"{game_title}", status=status,
                               start_time=start_time, now_time=now_time)
    # Если игра уже закончилась то мы сообщаем об этом
    elif status == 'ended':
        return render_template("penalty.html", title=f'{game_title}', status=status)
    # Иначе отображаем игру
    else:
        # Время окончание игры
        end_time = datetime.strftime(datetime.strptime(game.end_time, Consts.TIME_FORMAT_FOR_HUMAN),
                                     Consts.TIME_FORMAT_FOR_JS)
        now_time = datetime.strftime(time, Consts.TIME_FORMAT_FOR_JS)
        message = None
        tasks = {}
        # Формируем информацию о состоянии задач пользователя
        tasks_positions = []
        for task_position in game.tasks_positions.split('|'):
            position, task_id = task_position.split(':')
            task = db.session.query(Task).filter(Task.id == int(task_id)).first()
            tasks_positions.append([position, task])
        tasks_positions = dict(tasks_positions)
        tasks = {}
        tasks_states = get_tasks_info('states', game.id, login=current_team.login)
        numbers_of_sets = get_tasks_info('numbers_of_sets', game.id)
        changes_numbers_of_sets = dict()
        changes_tasks_states = dict()
        for key in Consts.TASKS_KEYS['penalty']:
            tasks[key] = {'id': tasks_positions[Consts.TASKS_POSITIONS_BY_KEYS['penalty'][key]].id,
                          'name': key[1:],
                          'state': tasks_states[key],
                          'condition': get_condition(tasks_positions[key[1:]].id),
                          'manual_check': tasks_positions[key[1:]].manual_check,
                          'ans_picture': tasks_positions[key[1:]].ans_picture
                          }
        # Если пользователь сдал задачу
        if request.method == "POST":
            key = 't' + request.form.get('name')
            verdicts = ['ok', 'ff', 'fs']
            # Если пользователь не попытался багануть сайт
            if get_state(tasks[key]['state']) in ['ok', 'ff'] and not is_member:
                result = tasks_positions[key[1:]].check_ans(request.form.get('answer'))
                # Если пользователь сдал задачу правильно
                if result:
                    # Если пользователь сдал задачу правильно с первой попытки
                    if get_state(tasks[key]['state']) == 'ok':
                        tasks[key]['state'] = str(numbers_of_sets[key]['cost']) + 'af'
                        if key not in changes_numbers_of_sets.keys():
                            changes_numbers_of_sets[key] = dict()
                        changes_numbers_of_sets[key]['number_of_sets'] = numbers_of_sets[key]['number_of_sets'] - 1
                        if numbers_of_sets[key]['cost'] > 5:
                            if changes_numbers_of_sets[key]['number_of_sets'] == 0:
                                changes_numbers_of_sets[key]['cost'] = numbers_of_sets[key]['cost'] - 1
                                changes_numbers_of_sets[key]['number_of_sets'] = game.sets_number
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
                changes_tasks_states[key] = tasks[key]['state']
                update_tasks_info('states', game.id, changes_tasks_states, login=current_team.login)
                update_tasks_info('numbers_of_sets', game.id, changes_numbers_of_sets)
                return jsonify({'hah':'hah'})
            else:
                return render_template('error.html', message='У вас нет прав на сдачу задач', last=f'../penalty/{game_title}')
        else:
            return render_template('penalty.html', title=f'{game_title}', block="", tasks=tasks,
                                   keys=Consts.TASKS_KEYS['domino'], message=False, info=numbers_of_sets,
                                   state=status, end_time=end_time, now_time=now_time, is_member=is_member)


# Сдача задачи на ручную проверку
@app.route("/add_task_for_manual_checking", methods=["POST"])
def add_task_for_manual_checking():
    print('hah')
    game_title = request.form['game_title']
    task_id = request.form['task_id']
    task_position = request.form['task_position']
    game = db.session.query(Game).filter(Game.title == game_title).first()
    if game is None:
        return jsonify({'hah': 'hah'})
    task = db.session.query(Task).filter(Task.id == task_id).first()
    if task is None:
        return jsonify({'hah': 'hah'})
    login = None
    if game.game_format == 'personal':
        login = current_user.login
    else:
        for team in current_user.captaining:
            if game in team.games:
                login = team.login
    if login is None:
        return jsonify({'hah': 'hah'})
    time = datetime.now()
    time = datetime.strftime(time, Consts.TIME_FORMAT_FOR_HUMAN)
    if task.ans_picture:
        answer = request.form['result'][1:]
    else:
        answer = request.form['result']
    params = {'login': login,
              'task_id': task_id,
              'position': task_position,
              'answer': answer,
              'ans_picture': task.ans_picture,
              'time': time}
    # Если Домино то возвращаем задачу на "игровой стол"
    changes_numbers_of_sets = dict()
    changes_tasks_states = dict()
    tasks_info = get_tasks_info('states', game.id, login=login)
    if game.game_type == "domino":
        key = Consts.TASKS_KEYS_BY_POSITIONS['domino'][task_position]
        numbers_of_sets = get_tasks_info('numbers_of_sets', game.id)
        picked_tasks = tasks_info['picked_tasks']
        picked_tasks.remove(key)
        changes_tasks_states['picked_tasks'] = ' '.join(picked_tasks)
        changes_numbers_of_sets[key] = dict()
        changes_numbers_of_sets[key]['number_of_sets'] = numbers_of_sets[key]['number_of_sets'] + 1
    else:
        key = Consts.TASKS_KEYS_BY_POSITIONS['penalty'][task_position]
    # Отмечаем что задача проверяется
    state = tasks_info[key]
    if get_state(state) == 'ok':
        state = '0cf'
    # Вторая попытка сдачи задачи
    else:
        state = '0cs'
    changes_tasks_states[key] = state
    update_tasks_info('numbers_of_sets', game.id, changes_numbers_of_sets)
    update_tasks_info('states', game.id, changes_tasks_states, login=login)
    add_task_for_manual_checking_db(game.id, params)
    return jsonify({'hah': 'hah'})


# Ручная проверка
@app.route('/checking/<game_title>', methods=["POST", "GET"])
def manual_checking(game_title):
    if is_auth():
        game = db.session.query(Game).filter(Game.title == game_title).first()
        if game is None:
            return render_template('what_are_you_doing_here.html')
        if game not in current_user.checkering:
            return render_template('what_are_you_doing_here.html')
        if request.method == "GET":
            current_answer = get_current_manual_checking(game.id)
            if current_answer == 'Not found':
                return render_template("manual_checking.html", not_task=True)
            current_answer = current_answer[0]
            login = current_answer.login
            task_id = current_answer.task_id
            position = current_answer.position
            answer = current_answer.answer
            ans_picture = current_answer.ans_picture
            time = current_answer.time
            condition = get_condition(task_id)
            return render_template("manual_checking.html", login=login, position=position, condition=condition,
                                   answer=answer, game_title=game_title, not_task=False, ans_picture=ans_picture,
                                   time=time, task_id=task_id)
        elif request.method == "POST":
            login = request.form.get('login')
            task_id = request.form.get('task_id')
            task_position = request.form.get('task_position')
            answer = request.form.get('answer')
            time = request.form.get('time')
            result = True if request.form.get('result') == "true" else False
            verdicts = ['cf', 'ff', 'cs', 'fs']
            tasks_info = get_tasks_info('states', game.id, login=login)
            changes_numbers_of_sets = dict()
            changes_states = dict()
            if game.game_type == 'domino':
                key = Consts.TASKS_KEYS_BY_POSITIONS['domino'][task_position]
                task = {"state": get_state(tasks_info[key]), "position": task_position}
                if get_state(task['state']) in ['cf', 'cs']:
                    if result and get_state(task['state']) == 'cf':
                        task['state'] = str(
                            sum(map(int, task_position.split('-')))) + 'af'
                        if task['name'] == '0-0':
                            task['state'] = '10af'
                    # Если пользователь решил задачу со второй попытки
                    elif result:
                        task['state'] = str(
                            max(map(int, task_position.split('-')))) + 'as'
                    # Если пользователь решил задачу неправильно
                    else:
                        task['state'] = verdicts[
                            verdicts.index(get_state(task['state'])) + 1]
                        if task['state'] == 'ff':
                            task['state'] = '0ff'
                        else:
                            task['state'] = str(
                                -min(map(int, task_position.split('-')))) + 'fs'
                        if task['name'] == '0-0':
                            task['state'] = '0fs'
            else:
                key = Consts.TASKS_KEYS_BY_POSITIONS['penalty'][task_position]
                task = {"state": get_state(tasks_info[key]), "position": task_position}
                tasks_numbers_of_sets_info = get_tasks_info('numbers_of_sets', game.id)
                if get_state(task['state']) in ['cf', 'cs']:
                    # Если пользователь сдал задачу правильно
                    if result:
                        # Если пользователь сдал задачу правильно с первой попытки
                        if get_state(task['state']) == 'cf':
                            task['state'] = str(tasks_numbers_of_sets_info[key]['cost']) + 'af'
                            changes_numbers_of_sets[key] = dict()
                            changes_numbers_of_sets[key]['number_of_sets'] = tasks_numbers_of_sets_info[key]['number_of_sets'] - 1
                            if changes_numbers_of_sets[key]['number_of_sets'] == 0:
                                changes_numbers_of_sets[key]['cost'] = tasks_numbers_of_sets_info[key]['cost'] - 1
                                changes_numbers_of_sets[key]['number_of_sets'] = game.sets_number
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
            # обновление бд
            changes_states[key] = task['state']
            index = get_current_manual_checking(game.id)[1]
            if 't1' not in changes_numbers_of_sets.keys():
                changes_numbers_of_sets['t1'] = dict()
            changes_numbers_of_sets['t1']['current_checking_id'] = index + 1
            update_tasks_info('states', game.id, changes_states, login=login)
            update_tasks_info('numbers_of_sets', game.id, changes_numbers_of_sets)
            params = {'login': login,
                      'task_id': task_id,
                      'position': task_position,
                      'answer': answer,
                      'time': time,
                      'result': result}
            add_task_for_manual_checking_db(game.id, params, is_result=True)
        return jsonify({'hah': 'hah'})


# Результаты
@app.route('/results/<game_title>')
def results(game_title):
    game = db.session.query(Game).filter(Game.title == game_title).first()
    if game is None:
        return render_template('what_are_you_doing_here.html')
    current_team = None
    if is_auth():
        if game.game_format == 'personal':
            if game in current_user.playing:
                current_team = current_user
        else:
            for team in current_user.captaining:
                if game in team.games:
                    current_team = team
            if current_team is None:
                for team in current_user.teams:
                    if game in team.games:
                        current_team = team
    team = ''
    if is_auth() and current_team is not None:
        team = current_team
    titles = {'domino': 'Домино', 'penalty': 'Пенальти'}
    info = Consts.TASKS_POSITIONS_BY_KEYS[game.game_type]
    keys = Consts.TASKS_KEYS[game.game_type]
    if game.game_type == 'domino':
        number = 28
    else:
        number = 16

    results = get_results(game.id)
    numbers_of_solved = []
    step = 1
    for result in results:
        x = 0
        for state in result[step:-1]:
            if get_point(state) > 0:
                x += 1
        numbers_of_solved.append(x)
    team_num = len(results)
    return render_template("results.html", team=team, results=results, title=titles[game.game_type],
                           info=info, number=number, team_num=team_num, keys=keys, numbers_of_solved=numbers_of_solved)


''' ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ '''


def get_condition(task_id):
    task_directory = os.path.join(Config.TASKS_UPLOAD_FOLDER, f'task_{task_id}')
    condition_directory = os.path.join(task_directory, "condition")

    with open(os.path.join(condition_directory, "condition.txt"), mode="r") as rfile:
        condition = rfile.read()
    return condition


def get_state(state):
    return state[-2:]


def get_point(state):
    return int(state[:-2])


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
