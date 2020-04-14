# Файл, содержащий класс пользователя

from werkzeug.security import generate_password_hash, check_password_hash

from forms import check_type


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
