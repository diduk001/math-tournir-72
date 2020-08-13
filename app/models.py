from flask_login import UserMixin
from flask_sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy
from sqlalchemy.pool import StaticPool
from app import db
import os
from config import basedir
db.metadata.clear()

authors_to_games_assoc_table = db.Table(
    'authors_to_games', db.metadata,
    db.Column('authoring_game', db.ForeignKey('games.id'), primary_key=True),
    db.Column('author', db.ForeignKey('users.id'), primary_key=True)
)

checkers_to_games_assoc_table = db.Table(
    'checkers_to_games', db.metadata,
    db.Column('checking_game', db.ForeignKey('games.id'), primary_key=True),
    db.Column('checker', db.ForeignKey('users.id'), primary_key=True)
)

members_to_teams_assoc_table = db.Table(
    'members_to_teams', db.metadata,
    db.Column('team', db.ForeignKey('teams.id'), primary_key=True),
    db.Column('member', db.ForeignKey('users.id'), primary_key=True)
)

teachers_to_teams_assoc_table = db.Table(
    'teachers_to_teams', db.metadata,
    db.Column('team', db.ForeignKey('teams.id'), primary_key=True),
    db.Column('teacher', db.ForeignKey('users.id'), primary_key=True)
)


captains_to_teams_assoc_table = db.Table(
    'captains_to_teams', db.metadata,
    db.Column('team', db.ForeignKey('teams.id'), primary_key=True),
    db.Column('captain', db.ForeignKey('users.id'), primary_key=True)
)


teams_to_games_assoc_table = db.Table(
    'teams_to_games', db.metadata,
    db.Column('team', db.ForeignKey('teams.id'), primary_key=True),
    db.Column('game', db.ForeignKey('games.id'), primary_key=True)
)

players_to_games_assoc_table = db.Table(
    'players_to_games', db.metadata,
    db.Column('player', db.ForeignKey('users.id'), primary_key=True),
    db.Column('game', db.ForeignKey('games.id'), primary_key=True)
)


class Task(db.Model):
    __tablename__ = 'tasks_archive'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    min_grade = db.Column(db.Integer)
    max_grade = db.Column(db.Integer)
    manual_check = db.Column(db.Boolean)
    ans_picture = db.Column(db.Boolean)
    have_solution = db.Column(db.Boolean, default=False)
    hidden = db.Column(db.Boolean, default=False)
    hashed_answer = db.Column(db.String())

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Установить ответ

    def set_ans(self, ans):
        print('new_ans', ans, generate_password_hash(ans))
        if self.hashed_answer is None:
            self.hashed_answer = generate_password_hash(ans)
        else:
            self.hashed_answer += '|' + generate_password_hash(ans)
        print('result', self.hashed_answer)
    # Проверить ответ

    def check_ans(self, ans):
        hashed_answers = self.hashed_answer.split('|')
        result = False
        for hashed_answer in hashed_answers:
            if check_password_hash(hashed_answer, ans):
                result = True
        return result

    def __repr__(self):
        return f"<Task {self.id}>"


class Game(db.Model):
    __tablename__ = 'games'
    __table_args__ = {'extend_existing': True}
    # id игры
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Название, класс, тип игры(домино, пенальти и т.п., время начала, время конца,
    # формат(командная/личная), приватность(закрытая/открытая), информация об игре, количество
    # задач, максимальный размер команды, минимальный размер команды, путь к файлу с решениями,
    # id авторов и проверяющих соответсвенно
    title = db.Column(db.String)
    grade = db.Column(db.String)
    game_type = db.Column(db.String)
    start_time = db.Column(db.String)
    end_time = db.Column(db.String)
    game_format = db.Column(db.String)
    privacy = db.Column(db.String)
    info = db.Column(db.Text)
    tasks_positions = db.Column(db.Text)
    tasks_number = db.Column(db.Integer)
    sets_number = db.Column(db.Integer)
    min_team_size = db.Column(db.Integer)
    max_team_size = db.Column(db.Integer)
    solutions = db.Column(db.String)
    authors = orm.relation("User",
                           secondary=authors_to_games_assoc_table,
                           back_populates='authoring')
    checkers = orm.relation("User",
                            secondary=checkers_to_games_assoc_table,
                            back_populates='checkering')
    teams = orm.relationship('Team',
                             secondary=teams_to_games_assoc_table,
                             back_populates='games')
    players = orm.relation('User',
                           secondary=players_to_games_assoc_table,
                           back_populates='playing')

    def __init__(self, title, grade, game_type, start_time, end_time, game_format, privacy, info,
                 author, task_number, min_team_size, max_team_size, sets_number, tasks_positions):
        self.title = title
        self.grade = grade
        self.game_type = game_type
        self.start_time = start_time
        self.end_time = end_time
        self.game_format = game_format
        self.privacy = privacy
        self.info = info
        self.authors.append(author)
        self.tasks_number = task_number
        self.min_team_size = min_team_size
        self.max_team_size = max_team_size
        self.sets_number = sets_number
        self.tasks_positions = tasks_positions


# Создать таблицу состояния задач для игры
# game_title - название игры, str
# tasks_number - количество задач, int
def create_tasks_tables(game_id, tasks_number):
    engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(basedir, 'databases', 'tasks_states.db'))
    metadata = sqlalchemy.MetaData(engine)
    game = db.session.query(Game).filter(Game.id == game_id).first()
    working_manual_check_table = sqlalchemy.Table(f"{game_id}_working_manual_check", metadata,
                                       sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                                       sqlalchemy.Column('login', sqlalchemy.String),
                                       sqlalchemy.Column('task_id', sqlalchemy.String),
                                       sqlalchemy.Column('position', sqlalchemy.String),
                                       sqlalchemy.Column('answer', sqlalchemy.String),
                                       sqlalchemy.Column('ans_picture', sqlalchemy.Boolean),
                                       sqlalchemy.Column('time', sqlalchemy.String))
    result_manual_check_table = sqlalchemy.Table(f'{game_id}_result_manual_check', metadata,
                                               sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                                               sqlalchemy.Column('login', sqlalchemy.String),
                                               sqlalchemy.Column('task_id', sqlalchemy.String),
                                               sqlalchemy.Column('position', sqlalchemy.String),
                                               sqlalchemy.Column('answer', sqlalchemy.String),
                                               sqlalchemy.Column('time', sqlalchemy.String),
                                               sqlalchemy.Column('result', sqlalchemy.Boolean))
    if game.game_type == 'domino':
        state_table = sqlalchemy.Table(f"{game_id}_states", metadata,
                                       sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                                       sqlalchemy.Column('login', sqlalchemy.String),
                                       sqlalchemy.Column('picked_tasks', sqlalchemy.String),
                                       *[sqlalchemy.Column('t' + str(i), sqlalchemy.Integer) for i in
                                         range(1, tasks_number + 1)]
                                       )
        numbers_of_sets_table = sqlalchemy.Table(f"{game_id}_numbers_of_sets", metadata,
                                                 sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                                                 sqlalchemy.Column('current_checking_id', sqlalchemy.Integer),
                                                 sqlalchemy.Column('key', sqlalchemy.String),
                                                 sqlalchemy.Column('number_of_sets', sqlalchemy.Integer)
                                                 )
        dict_of_attrs = {'number_of_sets': game.sets_number}
    else:
        state_table = sqlalchemy.Table(f"{game_id}_states", metadata,
                                       sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                                       sqlalchemy.Column('login', sqlalchemy.String),
                                       *[sqlalchemy.Column('t' + str(i), sqlalchemy.Integer) for i in
                                       range(1, tasks_number + 1)]
                                       )
        numbers_of_sets_table = sqlalchemy.Table(f"{game_id}_numbers_of_sets", metadata,
                                                 sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                                                 sqlalchemy.Column('current_checking_id', sqlalchemy.Integer),
                                                 sqlalchemy.Column('key', sqlalchemy.String),
                                                 sqlalchemy.Column('cost', sqlalchemy.Integer),
                                                 sqlalchemy.Column('number_of_sets', sqlalchemy.Integer)
                                                 )
        dict_of_attrs = dict([('number_of_sets', game.sets_number), ('cost', 16)])

    class Tasks(object):
        def __init__(self, dict_of_attrs):
            for item in dict_of_attrs.items():
                print(item[0], item[1])
                setattr(self, item[0], item[1])

    metadata.create_all(engine)
    print('what?')
    orm.mapper(Tasks, numbers_of_sets_table)
    _session = orm.sessionmaker(bind=engine)
    session = _session()
    dict_of_attrs['current_checking_id'] = 1
    for i in range(1, game.tasks_number + 1):
        new_dict_of_attrs = dict_of_attrs.copy()
        new_dict_of_attrs['key'] = f't{i}'
        task = Tasks(new_dict_of_attrs)
        session.add(task)
    session.commit()


def get_current_manual_checking(game_id):
    engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(basedir, 'databases', 'tasks_states.db'))
    metadata = sqlalchemy.MetaData(engine)
    task_id = get_tasks_info('numbers_of_sets', game_id)['t1']['current_checking_id']

    class WorkingTask(object):
        def __init__(self, attr_dict):
            for key, val in attr_dict.items():
                setattr(self, key, val)
    working_table = sqlalchemy.Table(f"{game_id}_working_manual_check", metadata, autoload=True)
    orm.mapper(WorkingTask, working_table)
    _session = orm.sessionmaker(bind=engine)
    session = _session()
    checking_answer = session.query(WorkingTask).filter(WorkingTask.id == task_id).first()
    if checking_answer is None:
        return 'Not found'
    else:
        return checking_answer, task_id


def add_task_for_manual_checking_db(game_id, attrs, is_result=False):

    class ResultTask(object):
        def __init__(self, attr_dict):
            for key, val in attr_dict.items():
                setattr(self, key, val)

    class WorkingTask(object):
        def __init__(self, attr_dict):
            for key, val in attr_dict.items():
                setattr(self, key, val)
    engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(basedir, 'databases', 'tasks_states.db'))
    metadata = sqlalchemy.MetaData(engine)
    if is_result:

        result_table = sqlalchemy.Table(f'{game_id}_result_manual_check', metadata, autoload=True)
        orm.mapper(ResultTask, result_table)
    else:

        working_table = sqlalchemy.Table(f"{game_id}_working_manual_check", metadata, autoload=True)
        orm.mapper(WorkingTask, working_table)
    _session = orm.sessionmaker(bind=engine)
    session = _session()
    if is_result:

        print('attrs', attrs)
        result = ResultTask(attrs)
        session.add(result)
    else:
        working_task = WorkingTask(attrs)
        session.add(working_task)
    session.commit()


# Добавить пользователя в таблицу состояний задач игры
# name - имя пользователя, str
# surname - фамилия пользователя, str
# tasks_number - количество задач, int
# game_title - название игры, str
def add_user_to_game_table(login, game_id):
    class UserTasks(object):
        def __init__(self, attr_dict):
            for key, val in attr_dict.items():
                setattr(self, key, val)
    engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(basedir, 'databases', 'tasks_states.db'))
    metadata = sqlalchemy.MetaData(engine)
    table = sqlalchemy.Table(f"{game_id}_states", metadata, autoload=True)
    orm.mapper(UserTasks, table)
    _session = orm.sessionmaker(bind=engine)
    session = _session()
    game = db.session.query(Game).filter(Game.id == game_id).first()
    dict_of_attr = {'login': login}
    if game.game_type == 'domino':
        dict_of_attr['picked_tasks'] = ''
    for i in range(1, game.tasks_number + 1):
        dict_of_attr[f't{i}'] = '0ok'
    user = UserTasks(dict_of_attr)
    session.add(user)
    session.commit()


def get_results(game_id):
    class UserTasks(object):
        pass

    engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(basedir, 'databases', 'tasks_states.db'))
    metadata = sqlalchemy.MetaData(engine)
    table = sqlalchemy.Table(f"{game_id}_states", metadata, autoload=True)
    orm.mapper(UserTasks, table)
    _session = orm.sessionmaker(bind=engine)
    session = _session()
    game = db.session.query(Game).filter(Game.id == game_id).first()
    result = []
    users_states = session.query(UserTasks).filter(True).all()
    for user_states in users_states:
        new_result = []
        s = 0
        login = user_states.login
        if game.game_format == 'personal':
            title = login
        else:
            team = db.session.query(Team).filter(Team.login == login).first()
            title = team.title
        new_result.append(title)
        for i in range(1, game.tasks_number + 1):
            new_result.append(getattr(user_states, f't{i}'))
            print(user_states)
            s += int(new_result[-1][:-2])
        new_result.append(s)
        result.append(new_result)
    result.sort(key=lambda x: -x[-1])
    return result


def get_tasks_info(table_title, game_id, login=None):
    class UserTasks(object):
        pass

    engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(basedir, 'databases', 'tasks_states.db'))
    metadata = sqlalchemy.MetaData(engine)
    table = sqlalchemy.Table(f"{game_id}_{table_title}", metadata, autoload=True)
    orm.mapper(UserTasks, table)
    _session = orm.sessionmaker(bind=engine)
    session = _session()
    game = db.session.query(Game).filter(Game.id == game_id).first()
    result = dict()
    if login is not None:
        user_states = session.query(UserTasks).filter(UserTasks.login == login).first()
        if game.game_type == 'domino':
            result['picked_tasks'] = getattr(user_states, 'picked_tasks').split()
        for i in range(1, game.tasks_number + 1):
            result[f't{i}'] = getattr(user_states, f't{i}')
    else:
        tasks = session.query(UserTasks).filter(True).all()
        for task in tasks:
            result[task.key] = {'number_of_sets': task.number_of_sets}
            result[task.key]['current_checking_id'] = task.current_checking_id
            if (game.game_type == 'penalty'):
                result[task.key]['cost'] = task.cost
    return result


def update_tasks_info(table_title, game_id, changes, login=None):
    class UserTasks(object):
        pass
    engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(basedir, 'databases', 'tasks_states.db'))
    metadata = sqlalchemy.MetaData(engine)
    table = sqlalchemy.Table(f"{game_id}_{table_title}", metadata, autoload=True)
    orm.mapper(UserTasks, table)
    _session = orm.sessionmaker(bind=engine)
    session = _session()
    print(table, game_id, changes)
    if login is not None:
        user_states = session.query(UserTasks).filter(UserTasks.login == login).first()
        for state in changes.items():
            setattr(user_states, state[0], state[1])
        session.commit()
    else:
        for change in changes.items():
            task = session.query(UserTasks).filter(UserTasks.key == change[0]).first()
            print('change', change)
            print('change[1]', change[1])
            print(task.cost, task.key, task.id)
            for attr in change[1].items():
                print('attr', attr)
                setattr(task, attr[0], attr[1])
            session.commit()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    # id в бд
    id = db.Column(db.Integer,
                   primary_key=True, autoincrement=True, index=True)
    # Информация которую о себе вводит пользователь:
    # Имя, Фамилия, класс, школа, учителя математики, информация о себе, электонная почта, её хеш,
    # логин, хеш пароля соответсвенно
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    grade = db.Column(db.Integer, nullable=True)
    school = db.Column(db.String, nullable=True)
    work_place = db.Column(db.String, nullable=True)
    phone_number = db.Column(db.String, nullable=True)
    teachers = db.Column(db.Text, nullable=True)
    info = db.Column(db.Text, nullable=True)
    email = db.Column(db.String, nullable=False)
    hashed_email = db.Column(db.String, nullable=False)
    login = db.Column(db.String, nullable=False)
    hashed_password = db.Column(db.String, nullable=False)
    # Системная информация о пользователе:
    # задани, которые создал, права, команды, в которых состоит, команды, в которые приглашён,
    # потверждена ли почта, заблокирован ли соответсвенно
    created_tasks = orm.relationship("Task")
    rights = db.Column(db.String, nullable=False, default='user')
    authoring = orm.relationship('Game',
                                 secondary=authors_to_games_assoc_table,
                                 back_populates="authors")
    checkering = orm.relationship('Game',
                                  secondary=checkers_to_games_assoc_table,
                                  back_populates='checkers')
    playing = orm.relationship('Game',
                               secondary=players_to_games_assoc_table,
                               back_populates='players')
    captaining = orm.relationship('Team',
                                  secondary=captains_to_teams_assoc_table,
                                  back_populates='captain')
    teams = orm.relationship('Team',
                             secondary=members_to_teams_assoc_table,
                             back_populates='members')
    managed_teams = orm.relationship('Team',
                                     secondary=teachers_to_teams_assoc_table,
                                     back_populates='teacher')
    is_approved = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    is_authenticated = True
    is_teacher = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def set_email(self, email):
        self.email = email
        self.hashed_email = generate_password_hash(email)

    def __init__(self, role, params):
        self.login = params['login']
        self.name = params['name']
        self.surname = params['surname']
        self.last_name = params['last_name']
        if role == 'Student':
            self.grade = params['grade']
            self.school = params['school']
            self.teachers = params['teachers']
            self.info = params['info']
        elif role == 'Teacher':
            self.is_teacher = True
            self.work_place = params['work_place']
            self.phone_number = params['phone_number']


class Team(db.Model):
    __tablename__ = 'teams'
    __table_args__ = {'extend_existing': True}

    # id в бд
    id = db.Column(db.Integer,
                   primary_key=True, autoincrement=True, index=True)
    title = db.Column(db.String, nullable=False)
    login = db.Column(db.String, nullable=False)
    grade = db.Column(db.String, nullable=False)
    hashed_password = db.Column(db.String, nullable=False)
    members = orm.relation('User',
                           secondary=members_to_teams_assoc_table,
                           back_populates='teams')
    teacher = orm.relation('User',
                           secondary=teachers_to_teams_assoc_table,
                           back_populates='managed_teams')
    captain = orm.relation('User',
                           secondary=captains_to_teams_assoc_table,
                           back_populates='captaining')
    games = orm.relation('Game',
                         secondary=teams_to_games_assoc_table,
                         back_populates='teams'
    )

    def __init__(self, title, grade, login):
        self.title = title
        self.grade = grade
        self.login = login

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


if __name__ == '__main__':
    db.create_all()
    db.session.commit()
