# Файл, содержащий класс пользователя

from werkzeug.security import generate_password_hash, check_password_hash


# Класс с данными о команде

class User:
    # Инициализация
    # team_name - название команды
    # member1, member2, member3, member4 - кортежи или список из Имени, Фамилия, Школы
    # grade - класс участников
    # ВАЖНО!! hashed_password здесь не указан, так как задаётся отдельным методом
    def __init__(self, login, team_name, grade, member1, member2, member3, member4):
        self.login = login
        check_type("login", login, str)

        self.id = int
        self.hashed_password = str

        self.team_name = team_name
        check_type("team name", team_name, str)

        self.grade = grade
        check_type("grade", grade, int)

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

    def set_password(self, password):
        check_type("password", password, str)
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        check_type("password", password, str)
        return check_password_hash(self.hashed_password, password)

    def __str__(self):
        fields = [f"login {self.login}",
                  f"team_name {self.team_name}",
                  f"grade {str(self.grade)}",
                  f"Member 1 {self.member1}",
                  f"Member 2 {self.member2}",
                  f"Member 3 {self.member3}",
                  f"Member 4 {self.member4}"]

        try:
            fields.insert(1, f"hashed password " + self.hashed_password)
        except AttributeError:
            pass

        try:
            fields.insert(0, "id " + str(self.id))
        except AttributeError:
            pass

        return " | ".join(fields)

    def __bool__(self):
        return True

    def __dict__(self):
        return {"login": self.login,
                "team_name": self.team_name,
                "grade": self.grade,

                "member1_name": self.member1[0],
                "member1_surname": self.member1[1],
                "member1_school": self.member1[2],

                "member2_name": self.member2[0],
                "member2_surname": self.member2[1],
                "member2_school": self.member2[2],

                "member3_name": self.member3[0],
                "member3_surname": self.member3[1],
                "member3_school": self.member3[2],

                "member4_name": self.member4[0],
                "member4_surname": self.member4[1],
                "member4_school": self.member4[2]
                }


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

IS_NAME_VALIDATOR = [Regexp(regex="^[А-Я+Ё][а-я+ё]+", message="Неверный формат записи")]
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
