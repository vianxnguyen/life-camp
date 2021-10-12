from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    qtype = db.Column(db.String, nullable=False)
    stype = db.Column(db.String, nullable=False)
    surveys = db.relationship('Survey', backref='question')

    def __init__(self, **kwargs):
        self.text = kwargs.get("text")
        self.qtype = kwargs.get("qtype")
        self.stype = kwargs.get("stype")

    def serialize(self):
        return {
            "id": self.id,
            "text": self.text,
            "qtype": self.qtype,
            "stype": self.stype
        }


class Survey(db.Model):
    __tablename__ = "survey"
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, nullable=False) #change this to be int
    description = db.Column(db.String, nullable=False)
    answer_text = db.Column(db.String, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    time_of_submit = db.Column(db.DateTime)
    addressed = db.Column(db.Boolean, default=False)
    
    def __init__(self, **kwargs):
        self.response_id = kwargs.get("response_id")
        self.description = kwargs.get("description")
        self.answer_text = kwargs.get("answer_text")
        self.question_id = kwargs.get("question_id")
        dateTimeObj = datetime.utcnow()
        self.time_of_submit = dateTimeObj

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "response_id": self.response_id,
            "answer_text": self.answer_text,
            "question_id": self.question_id,
            "time_of_submit": self.time_of_submit.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
            "addressed": self.addressed
        }

# class Users(UserMixin, db.Model):
#     """An admin user capable of viewing reports.

#     :param str email: email address of user
#     :param str password: encrypted password for the user

#     """
#     __tablename__ = 'users'

#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(), unique=True)
#     password_hash = db.Column(db.String())

#     def set_password(self,password):
#         self.password_hash = generate_password_hash(password)
     
#     def check_password(self,password):
#         return check_password_hash(self.password_hash,password)
 

