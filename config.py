import os.path

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
    VALID_PENALTY_TASKS_NUMBERS = tuple([str(i) for i in range(1, 17)])
    VALID_DOMINO_TASKS_NUMBERS = tuple([f'{i}-{j}' for i in range(7) for j in range(i, 7)])
    ALLOWED_TEXT_EXTENSIONS = {'txt'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
