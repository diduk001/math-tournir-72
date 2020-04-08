from flask import Flask, render_template, current_app, redirect, request

from config import config
from forms import LoginForm, SignUpMemberForm, SignUpTeamForm

app = Flask(__name__)
with app.app_context():
    config(current_app)


# Вызов обработчика базового шаблона base.html
@app.route("/base")
@app.route("/base.html")
def base():
    params = dict()
    params["title"] = "base html"
    params["block"] = ""
    return render_template("base.html", **params)


# Главная страница
@app.route("/")
def index():
    params = dict()
    params["title"] = "ТЮМ 72"
    return render_template("index.html", **params)


# Вход и профиль (профиль открывается только тогда, когда пользователь авторизован)
@app.route("/profile", methods=["GET", "POST"])
def profile():
    # Переменная для отладки, значения:
    # 0 - сценарий для релиза
    # 1 - открывает "Вход"
    # 2 - открывает "Профиль"

    debug_var = 1
    if debug_var == 0:
        return "Это версия для релиза, но я её пока что не сделал"
    elif debug_var == 1:
        form = LoginForm()
        params = dict()
        params["title"] = "Вход"
        params["form"] = form

        if form.validate_on_submit():
            return redirect("/base.html")
        return render_template("login.html", **params)
    elif debug_var == 2:
        return "Это профиль, но я его пока не сделал"


# Регистрация
@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "GET":
        params = dict()
        params["title"] = "Регистрация"
        params["form_team"] = SignUpTeamForm()
        params["form_member"] = SignUpMemberForm()
        return render_template("signup.html", **params)


@app.route('/rules')
def rules():
    params = dict()
    params["title"] = "Правила"
    return render_template("rules.html", **params)


@app.route('/domino')
def domino():
    return "Тут должна быть страница с домино но я её не сделал"


@app.route('/penalty')
def penalty():
    return "Я захотел поспать и поэтому не сделал эту страницу"


def main():
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
