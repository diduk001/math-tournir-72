# -*- coding: utf-8 -*-
import os
import os.path

from flask import render_template, request, flash

from app import app
from app.forms import *
from app.models import *
from config import Config
from config import Constants as Consts


# Главная страница

@app.route('/')
@app.route('/index/')
def index():
    params = dict()
    params['title'] = 'ТЮМ 72'
    return render_template('index.html', **params)


# Регистрация

@app.route('/sign_up/', methods=['GET', 'POST'])
def sign_up():
    pass


# Вход

@app.route('/login/', methods=['GET', 'POST'])
def login():
    pass


# Добавить задачу

@app.route('/add_task/', methods=['GET', 'POST'])
def add_task():
    add_task_form = AddTaskForm()
    params = dict()
    params['title'] = 'Добавить Задачу'
    params['add_task_form'] = add_task_form
    params['success'] = False

    if request.method == 'POST' and add_task_form.validate_on_submit():
        min_grade = request.form.get("min_grade")
        max_grade = request.form.get("max_grade")
        manual_check = request.form.get("manual_check")
        condition_file = request.files.get("condition_file")
        condition_images = request.files.getlist("condition_images")
        solution_file = request.files.get("solution_file")
        solution_images = request.files.getlist("solution_images")
        ans_picture = request.form.get("ans_picture")
        answer = request.form.get("answer")

        if min_grade > max_grade:
            flash("Младший класс старше Старшего класса")
            return render_template('add_task.html', **params)

        if ans_picture:
            manual_check = True

        task = Task()
        task.min_grade = min_grade
        task.max_grade = max_grade
        task.manual_check = bool(manual_check)
        task.ans_picture = bool(ans_picture)
        task.set_ans(answer)

        db.session.add(task)
        db.session.commit()

        task_directory = os.path.join(Config.TASKS_UPLOAD_FOLDER, f'task_{task.id}')
        condition_directory = os.path.join(task_directory, "condition")
        os.mkdir(task_directory)
        os.mkdir(condition_directory)
        condition_file.save(os.path.join(condition_directory, rename_file(condition_file.filename,
                                                                          "condition")))
        if condition_images:
            for image in condition_images:
                if image.filename:
                    image.save(os.path.join(condition_directory, image.filename))

        if solution_file:
            task.have_solution = True
            solution_directory = os.path.join(task_directory, "solution")
            os.mkdir(solution_directory)
            solution_file.save(os.path.join(solution_directory, rename_file(solution_file.filename,
                                                                            "solution")))

            if solution_images:
                for image in solution_images:
                    if image.filename:
                        image.save(os.path.join(solution_directory, image.filename))

        params["success"] = True
        return render_template("add_task.html", **params)

    return render_template('add_task.html', **params)


# Архив

@app.route('/archive/')
@app.route('/tasks/')
def archive():
    params = dict()
    params['title'] = 'Архив'

    tasks_table = Task.quer

    params["tasks_table"] = tasks_table

    return render_template("archive.html", **params)


# Отображение задачи

@app.route('/tasks/<int:task_id>')
def task(task_id):
    params = dict()
    params['title'] = 'Задача ' + str(task_id)

    task = db.session.query(Task).filter_by(id=task_id).first()
    params['task'] = task

    task_dir_from_templates = os.path.join(Config.TASKS_UPLOAD_FROM_TEMPLATES,
                                           f'task_{task.id}')
    condition_dir_from_templates = os.path.join(task_dir_from_templates, 'condition')
    condition_from_templates = os.path.join(condition_dir_from_templates, 'condition.txt')

    params["condition_file_path"] = condition_from_templates

    if task.have_solution:
        params["have_solution"] = True
        solution_dir_from_templates = os.path.join(task_dir_from_templates, 'solution')
        solution_from_templates = os.path.join(solution_dir_from_templates, 'solution.txt')

        params["solution_file_path"] = solution_from_templates

    return render_template("task.html", **params)


''' ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ '''


def allowed_text_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Consts.ALLOWED_TEXT_EXTENSIONS


def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Consts.ALLOWED_IMAGE_EXTENSIONS


def rename_file(filename_old, filename_new):
    ext = filename_old.rsplit('.', 1)[1].lower()
    return '.'.join((filename_new, ext))


def get_extension(filename):
    if '.' not in filename:
        return ""

    return filename.rsplit('.', 1)[1].lower()
