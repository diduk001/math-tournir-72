# Файл, содержащий формы для входа и регистрации

from flask_wtf import FlaskForm
from flask_wtf.file import *
from wtforms import *
from wtforms.validators import *

from config import Constants as Consts


# Функция-Валидатор для проверки строки на номер задачи

def is_task_validator(form, field):
    game_type = form.game_type.data
    task = field.data
    if game_type == "domino":
        if task not in Consts.VALID_DOMINO_TASKS_NUMBERS:
            raise ValidationError("Номер задачи не прошёл проверку")
    elif game_type == "penalty":
        if task not in Consts.VALID_PENALTY_TASKS_NUMBERS:
            raise ValidationError("Номер задачи не прошёл проверку")


# Функция-Валидатор для проверки, добавлен ли хотя бы один файл

def at_least_one_file_validator(form, field):
    files = field.data
    raise ValidationError(repr(files))


# Константные валидаторы проверки имени и наличия ввода

IS_NAME_VALIDATOR = [Regexp(regex="^[А-Я+Ё][а-я+ё]+", message="Неверный формат записи")]
DATA_REQUIRED_VALIDATOR = [InputRequired(message="Это поле обязательно для заполения")]
FILE_REQUIRED_VALIDATOR = [FileRequired(message="Нужно отправить этот файл")]
AT_LEAST_ONE_FILE_REQUIRED_VALIDATOR = []
IS_TASK_VALIDATOR = [is_task_validator]
ALL_IMAGES_FILES = [FileAllowed(Consts.ALLOWED_IMAGE_EXTENSIONS, message="Неправильный формат "
                                                                         "файла")]
ALL_TEXT_FILES = [FileAllowed(Consts.ALLOWED_TEXT_EXTENSIONS, message="Неправильный формат файла")]

EMAIL_VALIDATOR = [Email(message="Формат ввода Email неправильный")]

GRADE_CHOICES = [(str(i), str(i)) for i in range(5, 12)]
GAME_TYPE_CHOICES = [("domino", "Домино"), ("penalty", "Пенальти")]


# Форма для входа

class LoginForm(FlaskForm):
    login = StringField("Логин", validators=DATA_REQUIRED_VALIDATOR)
    password = PasswordField("Пароль", validators=DATA_REQUIRED_VALIDATOR)
    submit = SubmitField("Вход")


# Форма для регистрации члена команды с полями имени, фамилии, школы

class SignUpMemberForm(Form):
    surname = StringField("Фамилия", validators=IS_NAME_VALIDATOR + DATA_REQUIRED_VALIDATOR)
    name_field = StringField("Имя", validators=IS_NAME_VALIDATOR + DATA_REQUIRED_VALIDATOR)
    school = StringField("Школа", validators=DATA_REQUIRED_VALIDATOR)


# Форма для регистрации команды с полями логина, пароля, названия команды, выбора класса

class SignUpTeamForm(Form):
    login = StringField("Логин", validators=DATA_REQUIRED_VALIDATOR)
    password = PasswordField("Пароль", validators=DATA_REQUIRED_VALIDATOR)
    email = StringField("Email", validators=DATA_REQUIRED_VALIDATOR + EMAIL_VALIDATOR)
    team_name = StringField("Название команды", validators=DATA_REQUIRED_VALIDATOR)
    grade = SelectField("Класс", choices=GRADE_CHOICES)


# Всеобобщающая форма с формой регистрацией команды

class SignUpForm(FlaskForm):
    team = FormField(SignUpTeamForm)

    member1 = FormField(SignUpMemberForm)
    member2 = FormField(SignUpMemberForm)
    member3 = FormField(SignUpMemberForm)
    member4 = FormField(SignUpMemberForm)
    submit = SubmitField("Регистрация")


# Всеобобщающая форма для регистрации команды из одного человека

class SignUpPlayerForm(FlaskForm):
    team = FormField(SignUpTeamForm)
    member = FormField(SignUpMemberForm)
    submit = SubmitField("Регистрация")


# Форма для бана команды

class BanTeamForm(FlaskForm):
    team_name = StringField("Название команды", validators=DATA_REQUIRED_VALIDATOR)
    submit = SubmitField("Удалить команду из соревнования")


# Форма для пардона команды

class PardonTeamForm(FlaskForm):
    team_name = StringField("Название команды", validators=DATA_REQUIRED_VALIDATOR)
    submit = SubmitField("Удалить команду из соревнования")


# Форма для добавления задачи в архив

class AddTaskForm(FlaskForm):
    min_grade = SelectField("Самый младший рекомендуемый класс", default='5',
                            choices=GRADE_CHOICES)
    max_grade = SelectField("Самый старший рекомендуемый класс", default='5',
                            choices=GRADE_CHOICES)
    condition_file = FileField("*.txt файл с условием", validators=FILE_REQUIRED_VALIDATOR)
    condition_images = MultipleFileField("Файлы иллюстраций к условию (допустимы файлы "
                                         "*.png/*.jpg/*.jpeg/*.gif)",
                                         validators=ALL_IMAGES_FILES)
    solution_file = FileField("*.txt файл с решением", validators=ALL_TEXT_FILES)
    solution_images = MultipleFileField("Файлы иллюстраций к решению (допустимы файлы "
                                         "*.png/*.jpg/*.jpeg/*.gif)",
                                         validators=ALL_IMAGES_FILES)
    answer = StringField("Ответ", validators=DATA_REQUIRED_VALIDATOR)
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
    grade = RadioField("Выберите класс", choices=GRADE_CHOICES,
                       validators=DATA_REQUIRED_VALIDATOR)
    game = RadioField("Выберите игру", choices=GAME_TYPE_CHOICES)
    submit = SubmitField("Перейти")


''' ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ '''


def get_extension(filename):
    if '.' not in filename:
        return ""

    return filename.rsplit('.', 1)[1].lower()
