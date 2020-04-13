from flask import Flask, render_template, current_app, redirect, request

from config import config
from db_interface import *
from forms import SignUpForm, LoginForm

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
    sign_up_form = SignUpForm()
    params = dict()
    params["title"] = "Регистрация"
    params["form"] = sign_up_form

    if sign_up_form.validate_on_submit():
        if check_login(request.form.get("team-login")):
            return render_template("sign_up.html", **params, used_login=True)

        print(repr(request.form.get("team-grade")))
        user = User(
            login=request.form.get("team-login"),
            team_name=request.form.get("team-team_name"),
            grade=int(request.form.get("team-grade")),

            member1=(request.form.get("member1-name_field"),
                     request.form.get("member1-surname"),
                     request.form.get("member1-school")),

            member2=(request.form.get("member2-name_field"),
                     request.form.get("member2-surname"),
                     request.form.get("member2-school")),

            member3=(request.form.get("member3-name_field"),
                     request.form.get("member3-surname"),
                     request.form.get("member3-school")),

            member4=(request.form.get("member4-name_field"),
                     request.form.get("member4-surname"),
                     request.form.get("member4-school"))
        )

        user.set_password(request.form.get("team-password"))
        add_user(user)
        return redirect("/login")

    return render_template("sign_up.html", **params)


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


if __name__ == '__main__':
    app.debug = True
    app.run(port=8080, host='127.0.0.1')
