from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Task(db.Model):
    __bind_key__ = 'tasks_archive'
    __tablename__ = 'tasks_archive'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    min_grade = db.Column(db.Integer)
    max_grade = db.Column(db.Integer)
    manual_check = db.Column(db.Boolean)
    ans_picture = db.Column(db.Boolean)
    have_solution = db.Column(db.Boolean, default=False)
    hidden = db.Column(db.Boolean, default=False)
    hashed_answer = db.Column(db.String(128))
    # author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Установить ответ

    def set_ans(self, ans):
        self.hashed_answer = generate_password_hash(ans)

    # Проверить ответ

    def check_ans(self, ans):
        return check_password_hash(self.hashed_answer, ans)

    def __repr__(self):
        return f"<Task {self.id}>"

if __name__ == '__main__':
    db.create_all()
    db.session.commit()