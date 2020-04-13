from flask import Flask, render_template, current_app, redirect, request
import json

from config import config
from db_interface import *
from forms import SignUpForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "0d645377e31ab6b5847ec817bac4aaf8"
    
with app.app_context():
    config(current_app)

number_of_task = 5
with open("tasks_info.json", "rt", encoding="utf8") as f:
    tasks = json.loads(f.read())
for key in tasks.keys():
    print(tasks[key])
    tasks[key]['number'] = number_of_task

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
  
keys = list(map(str, range(1, 29)))
tasks_names = {'0-0':'1', '0-1':'2', '0-2':'3', '0-3':'4', '0-4':'5', '0-5':'6', '0-6':'7', '1-1':'8', '1-2':'9',
               '1-3':'10', '1-4':'11', '1-5':'12', '1-6':'13', '2-2':'14', '2-3':'15', '2-4':'16', '2-5':'17',
               '2-6':'18', '3-3':'19', '3-4':'20', '3-5':'21', '3-6':'22', '4-4':'23', '4-5':'24', '4-6':'25',
               '5-5':'26', '5-6':'27', '6-6':'28'}
number_of_picked_task = 0
picked_tasks = []

@app.route("/domino", methods=["GET", "POST", "PATCH"])
def domino():
    global number_of_picked_task, picked_tasks, keys, tasks
    messages = {'full': "Вы уже взяли 2 задачи", 'accepted':'Вы уже решили эту задачу',
                'failed': 'У Вас закончились попытки на сдачу этой задачи', 'absent': 'На данный момент задачи с этим номером отсутсвуют',
                'hand': 'Вы уже взяли эту задачу'}
    if request.method == "GET":
        return render_template("domino.html", title="Домино ТЮМ72", block="", tasks=tasks, keys=keys, picked_tasks=picked_tasks, message=False)
    elif request.method == "POST":
        message = False
        if request.form.get("picked"):
            key = tasks_names[request.form.get("picked")]
            if number_of_picked_task == 2:
                message = messages['full']
            elif tasks[key]['state'] in ['first_try_failed', 'ok']:
                picked_tasks.append(key)
                number_of_picked_task += 1
            else:
                print(tasks[key]['state'])
                message = messages[tasks[key]['state']]
        elif request.form.get('name'):
            key = tasks_names[request.form.get('name')]
            verdicts = ['ok', 'first_try_failed', 'failed']
            if tasks[key]['answer'] == request.form.get('answer'):
                tasks[key]['state'] = 'accepted'
            else:
                tasks[key]['state'] = verdicts[verdicts.index(tasks[key]['state']) + 1]
            picked_tasks.remove(key)
            number_of_picked_task -= 1
        return render_template("domino.html", title="Домино ТЮМ72", block="", tasks=tasks, keys=keys, picked_tasks=picked_tasks, message=message)


@app.route('/penalty')
def penalty():
    return "Я захотел поспать и поэтому не сделал эту страницу"


if __name__ == '__main__':
    app.debug = True
    app.run(port=8080, host='127.0.0.1')
