from config import GAMES_DEFAULT_TASK_NUMBERS
from data.games import Game
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
# solutions - путь к файлу с решениями, string
# author - id того кто инициировал создание игры, string
# task_number int
# min_team_size int
# max_team_size int
# sets_number - количество наборов задач, int

# Функция создающая игру
def create_game(title, grade, game_type, start_time, end_time, format,  privacy, info, solutions, author,
                task_number, min_team_size, max_team_size, sets_number):
    game = create_Game_object(title, grade, game_type, start_time, end_time, format, privacy, info, solutions, author,
                              task_number, min_team_size, max_team_size, sets_number)
    session = create_session('main_bd')
    session.add(game)
    session.commit()


# Создание объекта класса Game
def create_Game_object(title, grade, game_type, start_time, end_time, format,  privacy, info, solutions, author,
                task_number, min_team_size, max_team_size, sets_number):
    game = Game()
    game.title = title
    game.grade = grade
    game.game_type = game_type
    game.start_time = start_time
    game.end_time = end_time
    game.format = format
    game.privacy = privacy
    game.info = info
    game.solutions = solutions
    game.authors = author
    game.task_number = task_number
    game.min_team_size = min_team_size
    game.max_team_size = max_team_size
    game.sets_number = sets_number
    return game

# Обновить информацию о игре в блоке общей информации (название, доп. информация, класс, тип игры, время начала,
# время конца, формат (личная/командная), приватность(открытая/закрытая))
def update_games_common_info(title, info, grade, game_type, start_time, end_time, format, privacy):
    session = create_session('main_bd')
    game = session.query(Game).filter(Game.title == title)
    game.info = info
    game.grade = grade
    game.game_type = game_type
    game.start_time = start_time
    game.end_time = end_time
    game.format = format
    game.privacy = privacy
    session.commit()

# Обновить информацию о игре в блоке задач (файл с решениями, количество задач, количество наборов задач)
def update_games_task_info(title, solutions, task_number, sets_number):
    session = create_session('main_bd')
    game = session.query(Game).filter(Game.title == title)
    game.solutions = solutions
    game.task_number = task_number
    game.sets_number = sets_number
    session.commit()

# Обновить информацию о игре в блоке команды (максимальное и минимальное количество игроков в команде)
def update_games_team_info(title, min_team_size, max_team_size):
    session = create_session('main_bd')
    game = session.query(Game).filter(Game.title == title)
    game.min_team_size = min_team_size
    game.max_team_size = max_team_size
    session.commit()

# Обновить информацию о игре в блоке организаторов (авторы и проверяющие)
def update_games_authors_and_checkers_info(title, authors, checkers):
    session = create_session('main_bd')
    game = session.query(Game).filter(Game.title == title)
    for author in authors:
        if author[0] == '+':
            game.authors.append(int(author[1:]))
        else:
            game.authors.remove(int(author[1:]))
    for checker in checkers:
        if checker[0] == '+':
            game.checkers.append(int(checker[1:]))
        else:
            game.checkers.remove(int(checker[1:]))

# Получить игру по названию
def get_game(title):
    session = create_session('main_bd')
    game = session.query(Game).filter(Game.title == title)
    return game
