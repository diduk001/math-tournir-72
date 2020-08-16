from app.models import *
from config import Constants as Consts
from datetime import datetime
# Во всём коде:
# title - Название игры, string
# grade - Класс, int
# game_type - тип игры(домино, пенальти и т.п.), string
# start_time - начало игры, string
# end_time - конец игры, string
# format - формат игры(командная/личная), string
# privacy - приватность игры(открытая, закрытая), string
# info - дополнительная информация о игре(описание string
# author - id того кто инициировал создание игры, string
# task_number - количество задач, int
# sets_number - количество наборов задач, int
# min_team_size - минимальный размер команды, int
# max_team_size - максимальный размер команды, int


# Функция создающая игру
def create_game(title, grade, game_type, start_time, end_time, game_format, privacy, info, author,
                min_team_size=4, max_team_size=4):
    task_number = Consts.GAMES_DEFAULT_TASK_NUMBERS[game_type]
    sets_number = Consts.GAMES_DEFAULT_SETS_NUMBERS[game_type]
    tasks_positions = Consts.GAMES_DEFAULT_TASKS_POSITIONS[game_type]
    game = Game(title, grade, game_type, start_time, end_time, game_format, privacy, info, author,
                task_number, min_team_size, max_team_size, sets_number, tasks_positions)
    author.authoring.append(game)
    db.session.add(game)
    db.session.commit()
    create_tasks_tables(game.id, task_number)



def get_game_status(game_title, time):
    game = get_game(game_title)
    if game == 'Not found':
        return game
    start_time = datetime.strptime(game.start_time, Consts.TIME_FORMAT_FOR_HUMAN)
    end_time = datetime.strptime(game.end_time, Consts.TIME_FORMAT_FOR_HUMAN)
    print(time, start_time, end_time)
    if time < start_time:
        return 'not started'
    elif time > end_time:
        return 'ended'
    else:
        return 'in progress'


# Зарегистрировать команду/игрока на игру
def register_to_game(game_title, player_id):
    game = get_game(game_title)
    if game == "Not found":
        return 'Game not found'
    if game.game_format == 'team':
        team = db.session.query(Team).filter(Team.id == player_id).first()
        if team is None:
            return "Team not found"
        game.teams.append(team)
        db.session.commit()
        add_user_to_game_table(team.login, game.id)
    elif game.game_format == 'personal':
        player = db.session.query(User).filter(User.id == player_id).first()
        if player is None:
            return "Player not found"
        game.players.append(player)
        db.session.commit()
        add_user_to_game_table(player.login, game.id)


# Изменить общую информацию о игре
def update_game_common_info(last_title, current_title, info, grade, game_type, start_time, end_time,
                            game_format, privacy):
    game = get_game(last_title)
    if game != 'Not found':
        game.title = current_title
        game.info = info
        game.grade = grade
        game.game_type = game_type
        game.start_time = start_time
        game.end_time = end_time
        game.game_format = game_format
        game.privacy = privacy
        game.tasks_number = Consts.GAMES_DEFAULT_TASK_NUMBERS[game_type]
        game.sets_number = Consts.GAMES_DEFAULT_SETS_NUMBERS[game_type]
        db.session.commit()
    return game


# Изменить информацию о задачах
def update_game_tasks_info(title, tasks_number, sets_number):
    game = get_game(title)
    if game != 'Not found':
        game.tasks_number = tasks_number
        game.sets_number = sets_number
        db.session.commit()
        changes = {}
        for i in range(1, game.tasks_number):
            changes[f't{i}'] = dict()
            changes[f't{i}']['number_of_sets'] = sets_number
        update_tasks_info('numbers_of_sets', title, changes)
    return game


# Изменить информацию о размере команд
def update_game_team_info(title, min_team_size, max_team_size):
    game = get_game(title)
    if game != 'Not found':
        game.min_team_size = min_team_size
        game.max_team_size = max_team_size
        db.session.commit()
    return game


# Изменение информации о авторах и проверяющих
# authors - логины авторов, str
# checkers - логины проверяющих, str
def update_game_authors_and_checkers_info(title, authors, checkers):
    game = get_game(title)
    authors = authors.split(', ')
    checkers = checkers.split(', ')
    game.authors = []
    game.checkers = []
    not_found_users = []
    if game != 'Not found':
        for author in authors:
            right_author = get_user(author)
            if right_author == "Not found":
                not_found_users.append(author)
            else:
                game.authors.append(right_author)
                if game not in right_author.authoring:
                    right_author.authoring.append(game)
        for checker in checkers:
            right_checker = get_user(checker)
            if right_checker == 'Not found':
                not_found_users.append(checker)
            else:
                game.checkers.append(right_checker)
                if game not in right_checker.checkering:
                    right_checker.append(game)
        db.session.commit()
    return game, not_found_users


# Получить общую информацию о игре по её названию
def get_game_common_info(title):
    game = get_game(title)
    if game != 'Not found':
        result = {'title': title,
                  'grade': game.grade,
                  'game_type': game.game_type,
                  'start_time': game.start_time,
                  'end_time': game.end_time,
                  'game_format': game.game_format,
                  'privacy': game.privacy,
                  'info': game.info}
        return result
    return game


# Получить общую информацию о игре по её названию в читаемом для пользователя формате
def get_game_common_info_human_format(title):
    game = get_game(title)
    if game != 'Not found':
        result = [('Название', title),
                  ('Класс', game.grade),
                  ('Тип игры', Consts.DICT_OF_HUMAN_FORMAT[game.game_type]),
                  ('Время начала', game.start_time),
                  ('Время конца', game.end_time),
                  ('Формат игры', Consts.DICT_OF_HUMAN_FORMAT[game.game_format]),
                  ('Приватность игры', Consts.DICT_OF_HUMAN_FORMAT[game.privacy]),
                  ('Описание игры', game.info)]
        return result
    return game


# Получить информацию о задачах игры по её названию в читаемом для пользователя формате
def get_game_tasks_info_human_format(title):
    game = get_game(title)
    if game != 'Not found':
        result = [('Количество задач', game.tasks_number),
                  ('Количество наборов задач', game.sets_number)]
        return result
    return game


# Получить информацию о задачах игры по её названию
def get_game_tasks_info(title):
    game = get_game(title)
    if game != 'Not found':
        result = {'tasks_number': game.tasks_number,
                  'sets_number': game.sets_number}
        return result
    return game


# Получить информацию о размере команд игры по её названию в читаемом для пользователя формате
def get_game_team_info_human_format(title):
    game = get_game(title)
    if game != 'Not found':
        result = [('Минимальный размер команды', game.min_team_size),
                  ('Максимальный размер команды', game.max_team_size)]
        return result
    return game


# Получить информацию о размере команд игры по её названию
def get_game_team_info(title):
    game = get_game(title)
    if game != 'Not found':
        result = {'max_team_size': game.max_team_size,
                  'min_team_size': game.min_team_size}
        return result
    return game


# Получить информацию о авторах и проверяющих игры по её названию в читаемом для пользователя формате
def get_game_authors_and_checkers_info_human_format(title):
    game = get_game(title)
    if game != 'Not found':
        result = [('Авторы', ', '.join(get_game_authors_info(title))),
                  ('Проверяющие', ', '.join(get_game_checkers_info(title)))]
        return result
    return game


# Получить какие позиции задач игры по названию
def get_game_tasks_positions(title):
    game = get_game(title)
    if game != 'Not found':
        result = list(map(lambda x: x.split(':'), game.tasks_positions.split('|')))
        return result
    return game

# Получить логины авторов игры по её названию
def get_game_authors_info(title):
    game = get_game(title)
    if game != 'Not found':
        result = list(map(lambda author: author.login, game.authors))
        return result
    return game


# Получить логины проверяющих игру по её названию
def get_game_checkers_info(title):
    game = get_game(title)
    if game != 'Not found':
        result = list(map(lambda checker: checker.login, game.checkers))
        return result
    return game


# Получить игру по названию
def get_game(title):
    game = db.session.query(Game).filter(Game.title == title)
    if game.first() is not None:
        return game.first()
    return 'Not found'


# Получить пользователя по имени и фамилии
def get_user(login):
    user = db.session.query(User).filter(User.login == login)
    if user.first() is not None:
        return user.first()
    return "Not found"
