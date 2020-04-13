from data import db_session


# Файл с конфигурацией приложения
def config(app):
    db_session.global_init("db/login_data_members_data_session.sqlite")
    app.config['SECRET_KEY'] = "0d645377e31ab6b5847ec817bac4aaf8"
    return
