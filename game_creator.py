from data.games import Game
from data.db_session import create_session
from config import GAMES_DEFAULT_TASK_NUMBERS, GAMES_DEFAULT_SETS_NUMBERS
from data.users import User
from data.tasks_states import create_tasks_table
from data.db_session import global_init, create_session
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
def create_game(title, grade, game_type, start_time, end_time, format, privacy, info, author,
                min_team_size=4, max_team_size=4):
    task_number = GAMES_DEFAULT_TASK_NUMBERS[game_type]
    sets_number = GAMES_DEFAULT_SETS_NUMBERS[game_type]
    game = Game(title, grade, game_type, start_time, end_time, format, privacy, info, author,
                              task_number, min_team_size, max_team_size, sets_number)
    create_tasks_table(title, task_number)
    author.authoring.append(game)
    session = create_session()
    current_session = session.object_session(game)
    current_session.add(game)
    current_session.commit()



# Изменить общую информацию о игре
def update_game_common_info(last_title, current_title, info, grade, game_type, start_time, end_time, format, privacy):
    game, session = get_game(last_title)
    if game != 'Not found':
        game.title = current_title
        game.info = info
        game.grade = grade
        game.game_type = game_type
        game.start_time = start_time
        game.end_time = end_time
        game.format = format
        game.privacy = privacy
        game.tasks_number = GAMES_DEFAULT_TASK_NUMBERS[game_type]
        game.sets_number = GAMES_DEFAULT_SETS_NUMBERS[game_type]
        session.commit()
    return game


# Изменить информацию о задачах
def update_game_tasks_info(title, tasks_number, sets_number):
    game, session = get_game(title)
    if game != 'Not found':
        game.tasks_number = tasks_number
        game.sets_number = sets_number
        session.commit()
    return game


# Изменить информацию о размере команд
def update_game_team_info(title, min_team_size, max_team_size):
    game, session = get_game(title)
    if game != 'Not found':
        game.min_team_size = min_team_size
        game.max_team_size = max_team_size
        session.commit()
    return game


# Изменение информации о авторах и проверяющих
# add_authors - имена и фамилии добавленных авторов, list<tuple<str, str>>
# delete_authors - имена и фамилии удалённых авторов, list<tuple<str, str>>
# add_checkers - имена и фамилии добавленных проверяющих, list<list<str, str>>
# delete_checkers - имена и фамилии удалённых проверяющих, list<list<str, str>>
def update_game_authors_and_checkers_info(title, add_authors=None, delete_authors=None,
                                        add_checkers=None, delete_checkers=None):
    game, session = get_game(title)
    if game != 'Not found':
        for author in add_authors:
            right_author = get_user(author[0], author[1])
            game.authors.append(right_author)
            right_author.authoring.append(game)
        for author in delete_authors:
            right_author = get_user(author[0], author[1])
            game.authors.remove(right_author)
            right_author.authoring.delete(game)
        for checker in add_checkers:
            right_checker = get_user(checker[0], checker[1])
            game.chechers.append(right_checker)
            right_checker.append(game)
        for checker in delete_checkers:
            right_checker = get_user(checker[0], checker[1])
            game.chechers.remove(right_checker)
            right_checker.remove(game)
        session.commit()
    return game


# Получить общую информацию о игре по её названию
def get_game_common_info(title):
    game, session = get_game(title)
    if game != 'Not found':
        result = {'title': title,
                  'grade': game.grade,
                  'game_type': game.type,
                  'start_time': game.start_time,
                  'end_time': game.end_time,
                  'format': game.format,
                  'privacy': game.privacy,
                  'info': game.info}
        return result
    return game


# Получить информацию о задачах игры по её названию
def get_game_tasks_info(title):
    game, session = get_game(title)
    if game != 'Not found':
        result = {'tasks_number': game.tasks_number,
                  'sets_number': game.sets_number}
        return result
    return game


# Получить информацию о размере команд игры по её нахванию
def get_game_team_info(title):
    game, session = get_game(title)
    if game != 'Not found':
        result = {'max_team_size': game.max_team_size,
                  'min_team_size': game.min_team_size}
        return result
    return game


# Получить имена и фамилии авторов игры по её названию
def get_game_authors_info(title):
    game, session = get_game(title)
    if game != 'Not found':
        result = list(map(lambda author: (author.name, author.surname), game.authors))
        return result
    return game


# Получить имена и фамилии проверяющих игру по её названию
def get_game_checkers_info(title):
    game, session = get_game(title)
    if game != 'Not found':
        result = list(map(lambda checker: (checker.name, checker.surname), game.checkers))
        return result
    return game


# Получить игру по названию
def get_game(title):
    session = create_session()
    game = session.query(Game).filter(Game.title == title)
    if game:
        return game.first(), session
    return 'Not found', None


# Получить пользователя по имени и фамилии
def get_user(name, surname):
    session = create_session()
    user = session.query(User).filter(User.name == name, User.surname == surname)
    if user:
        return user.first()
    return "Not found"
