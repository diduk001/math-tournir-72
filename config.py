# URL для совершения запросов

SERVER_URL = "http://0.0.0.0:80"

from data.users_login_data import User
# Файл, содержащий класс пользователя

from werkzeug.security import generate_password_hash, check_password_hash


# Создание данных о пользователе
def create_user(login, name, surname, email, grade, school, teacher, info):
    user = User()
    user.login = login
    user.name = name
    user.surname = surname
    user.email = email
    user.grade = grade
    user.school = school
    user.teacher = teacher
    user.info = info
    return user


# Словарь с информацией о том, может ли в игре быть разное количество задач
GAMES_TASK_NUMBERS_VARIABILITY = {'domino':False,
                                  'peanlty':True}
# Словарь количества задач в играх по умолчанию
GAMES_DEFAULT_TASK_NUMBERS = {'domino':28,
                              'penalty': 16}
# Словарь с информацией о том, может ли в игре быть больше одного набора задач
GAMES_SETS_NUMBERS_VARIABILITY = {'domino': True,
                                  'penalty': False}
# Словарь количества наборов задач в играх по умолчанию
GAMES_DEFAULT_SETS_NUMBERS = {'domino': 1,
                              'penalty': 1}
# Кортежи, в которых указаны валидные данные

VALID_REQUEST_TYPES = ("check_task", "get_task", "add_task")
VALID_GAME_TYPES = ("domino", "penalty")
VALID_GRADES = (5, 6, 7)
VALID_PENALTY_TASKS_NUMBERS = tuple([str(i) for i in range(1, 17)])
VALID_DOMINO_TASKS_NUMBERS = tuple([f"{i}-{j}" for i in range(7) for j in range(i, 7)])

# Файл, содержащий формы для входа и регистрации

from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *


# Функция проверки класса параметра
# parameter_name - имя параметра, используется в вызове ошибки
# var - значение переменной
# class_ - класс переменной
def check_type(parameter_name, var, class_):
    assert isinstance(var, class_), f"{parameter_name} is not {class_}"


def is_task_validator(form, field):
    game_type = form.game_type.data
    task = field.data
    if game_type == "domino":
        if task not in VALID_DOMINO_TASKS_NUMBERS:
            raise ValidationError("Not valid task")
    elif game_type == "penalty":
        if task not in VALID_PENALTY_TASKS_NUMBERS:
            raise ValidationError("Not valid task")


# Константные валидаторы проверки имени и наличия ввода

IS_NAME_VALIDATOR = [Regexp(regex="^[А-Я+Ё][а-я+ё]+", message="Неверный формат записи")]
DATA_REQUIRED_VALIDATOR = [InputRequired(message="Это поле обязательно для заполения")]
IS_TASK_VALIDATOR = [is_task_validator]
FILENAME_VALIDATOR = [Regexp(regex="^[\w\(\)\+\.\=\-]+\.(jpg|png|jpeg|gif|)$")]
EMAIL_VALIDATOR = [Email(message="Формат ввода Email неправильный")]


# Форма для входа

class LoginForm(FlaskForm):
    login = StringField("Логин", validators=DATA_REQUIRED_VALIDATOR)
    password = PasswordField("Пароль", validators=DATA_REQUIRED_VALIDATOR)
    submit = SubmitField("Вход")


# Форма для регистрации члена команды с полями имени, фамилии, школы


# Форма для регистрации команды с полями логина, пароля, названия команды, выбора класса

class SignUpUserForm(Form):
    login = StringField("Логин*", validators=DATA_REQUIRED_VALIDATOR)
    password = PasswordField("Пароль*", validators=DATA_REQUIRED_VALIDATOR)
    email = StringField("Email*", validators=DATA_REQUIRED_VALIDATOR + EMAIL_VALIDATOR)
    name = StringField("Имя*", validators=DATA_REQUIRED_VALIDATOR + IS_NAME_VALIDATOR)
    surname = StringField("Фамилия*", validators=DATA_REQUIRED_VALIDATOR + IS_NAME_VALIDATOR)
    grade = SelectField("Класс*", choices=[(5, 5), (6, 6), (7, 7)], coerce=int)
    school = StringField("Школа*", validators=DATA_REQUIRED_VALIDATOR)
    teachers = StringField("Учителя математики и руководители кружков, которые внесли вклад в Ваши успехи",
                           validators=DATA_REQUIRED_VALIDATOR + IS_NAME_VALIDATOR)
    info = StringField("Дополнительная информация о Вас (как с Вами можно связаться, что Вы хотите рассказать о себе)",
                       validators=DATA_REQUIRED_VALIDATOR)

# Форма для бана команды

class BanTeamForm(FlaskForm):
    team_name = StringField("Название команды", validators=DATA_REQUIRED_VALIDATOR)
    submit = SubmitField("Удалить команду из соревнования")


# Форма для пардона команды

class PardonTeamForm(FlaskForm):
    team_name = StringField("Название команды", validators=DATA_REQUIRED_VALIDATOR)
    submit = SubmitField("Удалить команду из соревнования")

# Форма для добавления задачи

class AddTaskForm(FlaskForm):
    grade = SelectField("Класс", choices=[("5", "5"), ("6", "6"), ("7", "7")])
    game_type = SelectField("Тип игры", choices=[("domino", "Домино"), ("penalty", "Пенальти")])
    task = StringField("Номер задачи", validators=DATA_REQUIRED_VALIDATOR + IS_TASK_VALIDATOR)
    answer = StringField("Ответ", validators=DATA_REQUIRED_VALIDATOR)
    info = FileField("Загрузить условие - изображение с расширением *.jpg/*.jpeg/*.png/*.gif",
                     validators=FILENAME_VALIDATOR)
    manual_check = BooleanField("Задача проверяется вручную")
    ans_picture = BooleanField("Ответом является рисунок (тогда задача проверяется вручную)")
    submit = SubmitField("Добавить задачу")


# Форма для выбора начала и конца соревнования

class StartEndTimeForm(FlaskForm):
    game_type = SelectField("Тип игры", choices=[("domino", "Домино"), ("penalty", "Пенальти")],
                            validators=DATA_REQUIRED_VALIDATOR)
    time_start = DateTimeField("Начало игры", format="%d.%m.%Y %H:%M:%S",
                               validators=DATA_REQUIRED_VALIDATOR)
    time_end = DateTimeField("Конец игры", validators=DATA_REQUIRED_VALIDATOR)
    submit = SubmitField("Установить время начала и конца")


# Форма для забывчивых

class ForgotPassword(FlaskForm):
    email = StringField("Email", validators=DATA_REQUIRED_VALIDATOR + EMAIL_VALIDATOR)
    submit = SubmitField("Восстановить пароль")


# Чтобы выбрать класс и тип игры

class GradeGameForm(FlaskForm):
    grade = RadioField("Выберите класс", choices=[("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"),
                                                  ("10", "10"), ("11", "11")],
                       validators=DATA_REQUIRED_VALIDATOR)
    game = RadioField("Выберите игру", choices=[("domino", "Домино"), ("penalty",
                                                                       "Пенальти")])
    submit = SubmitField("Перейти")
