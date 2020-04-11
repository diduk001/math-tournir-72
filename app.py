from flask import Flask, render_template, request
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = "0d645377e31ab6b5847ec817bac4aaf8"
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
    return render_template("base.html", title="base", block="")

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
def main():
    app.run()


if __name__ == '__main__':
    main()
