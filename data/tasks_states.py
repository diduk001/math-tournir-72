import sqlalchemy
from sqlalchemy.orm import mapper, sessionmaker


# Создать таблицу состояния задач для игры
# game_title - название игры, str
# tasks_number - количество задач, int
def create_tasks_table(game_title, tasks_number):
    engine = sqlalchemy.create_engine('sqlite:///db/tasks_states.db')
    metadata = sqlalchemy.MetaData(engine)
    table = sqlalchemy.Table(game_title, metadata,
                          sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                          sqlalchemy.Column('name', sqlalchemy.String),
                          *[sqlalchemy.Column('t' + str(i), sqlalchemy.Integer) for i in range(1, tasks_number + 1)]
                          )
    metadata.create_all(engine)


# Добавить пользователя в таблицу состояний задач игры
# name - имя пользователя, str
# surname - фамилия пользователя, str
# tasks_number - количество задач, int
# game_title - название игры, str
def add_user_to_game_table(name, surname, tasks_number, game_title):
    class UserTasks(object):
        def __init__(self, dict_of_attr):
            for key, val in dict_of_attr.items():
                setattr(self, key, val)
    engine = sqlalchemy.create_engine('sqlite:///tasks_states.db')
    metadata = sqlalchemy.MetaData(engine)
    table = sqlalchemy.Table(game_title, metadata, autoload=True)
    mapper(UserTasks, table)
    Session = sessionmaker(bind=engine)
    session = Session()
    dict_of_attr = {'name': name + surname}
    for i in range(1, tasks_number + 1):
        dict_of_attr[f't{i}'] = '0ok'
    user = UserTasks(dict_of_attr)
    session.add(user)
    session.commit()


