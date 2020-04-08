# Файл, соержащий формы для входа и регистрации

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired


# Функция проверки класса параметра
# parameter_name - имя параметра, используется в вызове ошибки
# var - значение переменной
# class_ - класс переменной
def check_type(parameter_name, var, class_):
    if not isinstance(var, type):
        raise TypeError(f"{parameter_name} is not {class_}")


# Класс с данными о команде
class Team:
    # Инициализация
    # team_name - название команды
    # member1, member2, member3, member4 - кортежи или список из Имени, Фамилия, Школы
    # grade - класс участников
    def __init__(self, team_name, member1, member2, member3, member4, grade):
        self.team_name = team_name
        check_type("team name", team_name, str)

        self.member1 = member1
        check_type("member1", member1, tuple)

        self.member2 = member2
        check_type("member2", member2, tuple)

        self.member3 = member3
        check_type("member3", member3, tuple)

        self.member4 = member4
        check_type("member4", member4, tuple)

        try:
            self.name1, self.surname1, self.school1 = member1
        except ValueError:
            raise ValueError(f"member1 tuple {member1} length is {len(member1)}, but must be len 3")

        try:
            self.name2, self.surname2, self.school2 = member2
        except ValueError:
            raise ValueError(f"member1 tuple {member2} length is {len(member2)}, but must be len 3")

        try:
            self.name3, self.surname3, self.school3 = member3
        except ValueError:
            raise ValueError(f"member1 tuple {member3} length is {len(member3)}, but must be len 3")

        try:
            self.name4, self.surname4, self.school4 = member4
        except ValueError:
            raise ValueError(f"member1 tuple {member4} length is {len(member4)}, but must be len 3")

        self.grade = grade

        check_type("grade", grade, int)

    # метод, возвращающий имена участников
    # surname - параметр, отвечающий за то, есть ли фамилия
    def get_names(self, surname=True):
        if surname:
            return (self.name1 + ' ' + self.surname1,
                    self.name2 + ' ' + self.surname2,
                    self.name3 + ' ' + self.surname3,
                    self.name4 + ' ' + self.surname4)
        else:
            return (self.name1,
                    self.name2,
                    self.name3,
                    self.name4)


# Константа для проверки на то, есть ли содержание и выводе ошибки в ином случа
DATA_REQUIRED_VALIDATOR = [DataRequired(message="Это обязательное поле")]


# Форма для входа

class LoginForm(FlaskForm):
    login = StringField("Логин", validators=DATA_REQUIRED_VALIDATOR)
    password = PasswordField("Пароль", validators=DATA_REQUIRED_VALIDATOR)
    submit = SubmitField('Вход')


# Форма для регистрции пользователя

class SignUpMemberForm(FlaskForm):
    name = StringField("Имя", validators=DATA_REQUIRED_VALIDATOR)
    surname = StringField("Фамилия", validators=DATA_REQUIRED_VALIDATOR)
    school = StringField("Школа", validators=DATA_REQUIRED_VALIDATOR)


# Форма для регистрации команды

class SignUpTeamForm(FlaskForm):
    login = StringField("Логин", validators=DATA_REQUIRED_VALIDATOR)
    password = PasswordField("Пароль", validators=DATA_REQUIRED_VALIDATOR)
    team_name = StringField("Название команды", validators=DATA_REQUIRED_VALIDATOR)
    grade = SelectField("Класс", choices=[(5, "5"), (6, "6"), (7, "7")],
                        validators=DATA_REQUIRED_VALIDATOR)
    # member1_form = SignUpMemberForm()
    # member2_form = SignUpMemberForm()
    # member3_form = SignUpMemberForm()
    # member4_form = SignUpMemberForm()

    submit = SubmitField("Регистрация")
