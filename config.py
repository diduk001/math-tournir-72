import os.path

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'b50f19617f114c3fb0db6ae3a8937332'
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URL') or
                               'sqlite:///' + os.path.join(basedir, 'databases', 'main.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_BINDS = {
    #     'tasks_archive': 'sqlite:///' + os.path.join(basedir, 'databases', 'tasks_archive.db'),
    #     'games': 'sqlite:///' + os.path.join(basedir, 'databases', 'games.db'),
    #     'users': 'sqlite:///' + os.path.join(basedir, 'databases', 'users.db')
    # }
    TASKS_UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'tasks_files')
    TASKS_UPLOAD_FROM_TEMPLATES = os.path.join('..', 'static', 'tasks_files')


class Constants(object):
    VALID_REQUEST_TYPES = ('check_task', 'get_task', 'add_task')
    VALID_GAME_TYPES = ('domino', 'penalty')
    VALID_GRADES = (5, 6, 7, 8, 9, 10, 11)
    VALID_PENALTY_TASKS_NUMBERS = tuple([str(i) for i in range(1, 17)])
    VALID_DOMINO_TASKS_NUMBERS = tuple([f'{i}-{j}' for i in range(7) for j in range(i, 7)])
    ALLOWED_TEXT_EXTENSIONS = {'txt'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    # Словарь с информацией о том, может ли в игре быть разное количество задач
    GAMES_TASK_NUMBERS_VARIABILITY = {'domino': False,
                                      'peanlty': True}
    # Словарь количества задач в играх по умолчанию
    GAMES_DEFAULT_TASK_NUMBERS = {'domino': 28,
                                  'penalty': 16}

    # Словарь с информацией о том, может ли в игре быть больше одного набора задач
    GAMES_SETS_NUMBERS_VARIABILITY = {'domino': True,
                                      'penalty': False}
    # Словарь количества наборов задач в играх по умолчанию
    GAMES_DEFAULT_SETS_NUMBERS = {'domino': 2,
                                  'penalty': 1}
    TIME_FORMAT_FOR_HUMAN = '%d.%m.%Y %H:%M:%S'
    TIME_FORMAT_FOR_JS = '%m %d %Y %H:%M:%S'
    # Словарь позиций задач в играх по умолчанию
    GAMES_DEFAULT_TASKS_POSITIONS = {'domino': '0-0:-:0|0-1:-:0|0-2:-:0|0-3:-:0|0-4:-:0|0-5:-:0|0-6:-:0|1-1:-:0|'
                                               '1-2:-:0|1-3:-:0|1-4:-:0|1-5:-:0|1-6:-:0|2-2:-:0|2-3:-:0|2-4:-:0|'
                                               '2-5:-:0|2-6:-:0|3-3:-:0|3-4:-:0|3-5:-:0|3-6:-:0|4-4:-:0|4-5:-:0|'
                                               '4-6:-:0|5-5:-:0|5-6:-:0|6-6:-:0'
,
                                     'penalty': '1:-:0|2:-:0|3:-:0|4:-:0|5:-:0|6:-:0|7:-:0|8:-:0|9:-:0|10:-:0|11:-:0|'
                                                '12:-:0|13:-:0|14:-:0|15:-:0|16:-:0'}
    TASKS_KEYS = {'domino': list(map(lambda x: 't' + str(x), range(1, 29))),
                  'penalty': list(map(lambda x: 't' + str(x), range(1, 17)))}
    TASKS_POSITIONS = {'domino': ['0-0', '0-1', '0-2', '0-3', '0-4', '0-5', '0-6', '1-1', '1-2', '1-3', '1-4', '1-5',
                                  '1-6', '2-2', '2-3', '2-4', '2-5', '2-6', '3-3', '3-4', '3-5', '3-6', '4-4', '4-5',
                                  '4-6', '5-5', '5-6', '6-6'],
                       'penalty': list(map(lambda x: str(x), range(1, 17)))}
    TASKS_KEYS_BY_POSITIONS = {'domino': {'0-0': 't1', '0-1': 't2', '0-2': 't3', '0-3': 't4', '0-4': 't5', '0-5': 't6',
                                          '0-6': 't7', '1-1': 't8', '1-2': 't9', '1-3': 't10', '1-4': 't11',
                                          '1-5': 't12', '1-6': 't13', '2-2': 't14', '2-3': 't15', '2-4': 't16',
                                          '2-5': 't17', '2-6': 't18', '3-3': 't19', '3-4': 't20', '3-5': 't21',
                                          '3-6': 't22', '4-4': 't23', '4-5': 't24', '4-6': 't25', '5-5': 't26',
                                          '5-6': 't27', '6-6': 't28'},
                               'penalty': {'1': 't1', '2': 't2', '3': 't3', '4': 't4', '5': 't5', '6': 't6', '7': 't7',
                                           '8': 't8', '9': 't9', '10': 't10', '11': 't11', '12': 't12', '13': 't13',
                                           '14': 't14', '15': 't15', '16': 't16'}

}
    TASKS_POSITIONS_BY_KEYS = {'domino': {'t1': '0-0', 't2': '0-1', 't3': '0-2', 't4': '0-3', 't5': '0-4', 't6': '0-5',
                                           't7': '0-6', 't8': '1-1', 't9': '1-2', 't10': '1-3', 't11': '1-4',
                                           't12': '1-5', 't13': '1-6', 't14': '2-2', 't15': '2-3', 't16': '2-4',
                                           't17': '2-5', 't18': '2-6', 't19': '3-3', 't20': '3-4', 't21': '3-5',
                                           't22': '3-6', 't23': '4-4', 't24': '4-5', 't25': '4-6', 't26': '5-5',
                                           't27': '5-6', 't28': '6-6'},
                               'penalty': {'t1': '1', 't2': '2', 't3': '3', 't4': '4', 't5': '5', 't6': '6', 't7': '7',
                                           't8': '8', 't9': '9', 't10': '10', 't11': '11', 't12': '12', 't13': '13',
                                           't14': '14', 't15': '15', 't16': '16'}
                               }
    MESSAGES = {'domino': {'full': "Вы уже взяли 2 задачи", 'af': 'Вы уже решили эту задачу',
                          'as': 'Вы уже решили эту задачу',
                          'fs': 'У Вас закончились попытки на сдачу этой задачи',
                          'absent': 'На данный момент задачи с этим номером отсутсвуют',
                          'hand': 'Вы уже взяли эту задачу',
                          'cf': "Задача проверяется",
                          'cs': 'Задача проверяется'},
                'penalty': {'accepted': 'Вы уже решили эту задачу',
                            'failed': 'У вас закончились попытки на сдачу этой задачи'}
              }
    # Список игр и их названий
    GAMES_DICT = [('domino', 'Домино'),
                  ('penalty', 'Пенальти')]

    # Словарь для перевода из бд формата в формат удобный пользователю
    DICT_OF_HUMAN_FORMAT = {'open': 'открытая',
                            'private': 'закрытая',
                            'domino': 'Домино',
                            'penalty': 'Пенальти',
                            'team': 'командная',
                            'personal': 'личная'
                            }