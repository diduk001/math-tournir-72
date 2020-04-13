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


# Константные валидаторы проверки имени и наличия ввода

IS_NAME_VALIDATOR = [Regexp(regex="^[А-Я][а-я]+", message="Неверный формат записи")]
DATA_REQUIRED_VALIDATOR = [InputRequired(message="Это поле обязательно для заполения")]


# Форма для входа

class LoginForm(FlaskForm):
    login = StringField("Логин", validators=DATA_REQUIRED_VALIDATOR)
    password = PasswordField("Пароль", validators=DATA_REQUIRED_VALIDATOR)
    submit = SubmitField("Вход")


# Форма для регистрации члена команды с полями имени, фамилии, школы

class SignUpMemberForm(Form):
    name_field = StringField("Имя", validators=IS_NAME_VALIDATOR + DATA_REQUIRED_VALIDATOR)
    surname = StringField("Фамилия", validators=IS_NAME_VALIDATOR + DATA_REQUIRED_VALIDATOR)
    school = StringField("Школа", validators=DATA_REQUIRED_VALIDATOR)


# Форма для регистрации команды с полями логина, пароля, названия команды, выбора класса

class SignUpTeamForm(Form):
    login = StringField("Логин", validators=DATA_REQUIRED_VALIDATOR)
    password = PasswordField("Пароль", validators=DATA_REQUIRED_VALIDATOR)
    team_name = StringField("Название команды", validators=DATA_REQUIRED_VALIDATOR)
    grade = SelectField("Класс", choices=[(5, 5), (6, 6), (7, 7)], coerce=int)


# Глобальная форма с формой регистрацией команды и

class SignUpForm(FlaskForm):
    team = FormField(SignUpTeamForm)

    member1 = FormField(SignUpMemberForm)
    member2 = FormField(SignUpMemberForm)
    member3 = FormField(SignUpMemberForm)
    member4 = FormField(SignUpMemberForm)
    submit = SubmitField("Регистрация")
