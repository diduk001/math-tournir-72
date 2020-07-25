import os.path
import app.forms

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'b50f19617f114c3fb0db6ae3a8937332'
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URL') or
                               'sqlite:///' + os.path.join(basedir, 'databases', 'main.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {
        'tasks_archive': 'sqlite:///' + os.path.join(basedir, 'databases', 'tasks_archive.db')
    }
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
    GAMES_DEFAULT_SETS_NUMBERS = {'domino': 1,
                                  'penalty': 1}

    # Словарь игр и их названий
    GAMES_DICT = [('domino', 'Домино'),
                  ('penalty', 'Пенальти')]

    DICT_OF_FORMS = {'tasks': app.forms.GameTasksInfoForm,
                     'common': app.forms.GameCommonInfoForm,
                     'team': app.forms.GameTeamInfoForm,
                     'author_and_checkers': app.forms.GameAuthorsAndCheckersInfoForm}