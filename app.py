import csv
import datetime
from db import db 
from db import Question, Survey
from flask import Flask, request, jsonify
# from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)
#from werkzeug.security import check_password_hash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from form import LoginForm
import json
import os
from sqlalchemy import func
import sqlite3

#post reponse: responseID, question, and the separate answers
app = Flask(__name__)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']

# app.config['JWT_ACCESS_COOKIE_PATH'] = '/api'
# app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

app.config['JWT_COOKIE_CSRF_PROTECT'] = False

# Set the secret key to sign the JWTs with
app.config['JWT_SECRET_KEY'] = 'secret'  # Change this!

jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize app
db.init_app(app)
with app.app_context():
        db.create_all()

# generalized response formats
def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

@app.route('/token/auth', methods=['POST'])
def login():
    body = json.loads(request.data)
    username = body.get('username', None)
    password = body.get('password', None)
    if not username or not password:
        return jsonify({'login': False}), 401

    # Create the tokens we will be sending back to the user
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    # Set the JWT cookies in the response
    resp = jsonify({'login': True, 'acc_token': access_token, 'refresh tok': refresh_token})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200

@app.route('/token/refresh', methods=['POST'])
@jwt_required()
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


@app.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


@app.route('/questions/')
@jwt_required()
def all_questions():
   result = [q.serialize() for q in Question.query.all()]
   return success_response(result)


@app.route('/questions/', methods=["POST"])
@jwt_required()
def add_question():
   body = json.loads(request.data)
   new_q = Question(text=body.get("text"), qtype=body.get("qtype"), stype=body.get("stype"))
   db.session.add(new_q)
   db.session.commit()
   return success_response(new_q.serialize(), 201)


@app.route('/responses/')
@jwt_required()
def all_responses():
   result = [r.serialize() for r in Survey.query.all()]
   return success_response(result)


@app.route('/responses/', methods=["POST"])
@jwt_required()
def add_response():
    body = json.loads(request.data)
    new_r = Survey(response_id=body.get("response_id"), description=body.get("description"), answer_text=body.get("answer_text"), question_id=body.get("question_id"))
    db.session.add(new_r)
    db.session.commit()
    return success_response(new_r.serialize(), 201)


"""
{
    "response_id": 1,
    "responses": [
        {
            "description": "Supplies requested",
            "answer_text": "clothes",
            "question_id": 1
        },
        {
            "description": "Name",
            "answer_text": "Bob",
            "question_id": 2
        },
    ]
}
"""

@app.route('/survey/', methods=["POST"])
@jwt_required()
def add_survey():
    body = json.loads(request.data)
    response_id = body.get("response_id")
    responses = body.get("responses")
    print(type(responses))
    if not response_id or not responses:
        return failure_response("Missing required field")
    added = []
    for r in responses:
        print(r)
        new_r = Survey(response_id=response_id, description=r.get("description"), answer_text=r.get("answer_text"), question_id=r.get("question_id"))
        db.session.add(new_r)
        db.session.commit()
        added.append(new_r.serialize())
    return success_response(added, 201)


@app.route('/responses/ct/<int:id>/')
@jwt_required()
def get_cts(id):
    filtered = Survey.query.filter_by(question_id=id)
    all_cts = db.session.query(Survey.answer_text, func.count(Survey.answer_text)).group_by(Survey.answer_text).all()
    return success_response(dict(all_cts))


@app.route('/addressed/<int:response_id>/', methods=["POST"])
@jwt_required()
def mark_addressed(response_id):
    survey = Survey.query.filter_by(response_id=response_id)
    for s in survey: 
        s.addressed = True
    return success_response(survey)


@app.route('/filter/')
@jwt_required()
def filter_queries():
    body = json.loads(request.data)
    age = body.get("age", "")
    zipcode = body.get("zipcode", "")
    date1 = body.get("start_date", "") # take in string of format %Y-%m-%d
    date2 = body.get("end_date", "")
    joined = db.session.query(Survey).join(Question)
    age_filtered = joined.filter(Question.text=="age", Survey.answer_text==age) if len(age) != 0 else joined.all()
    age_ids = [age.response_id for age in age_filtered]
    zip_filtered = joined.filter(Question.text=="zipcode", Survey.answer_text==zipcode) if len(zipcode) != 0 else joined.all()
    zip_ids = [z.response_id for z in zip_filtered]
    date_filtered = db.session.query(Survey).filter(Survey.time_of_submit.between(date1, date2)) if len(date1) != 0 and len(date2) != 0 else joined.all()
    date_ids = [d.response_id for d in date_filtered]
    all_ids = age_ids + zip_ids + date_ids
    result = {i for i in all_ids if all_ids.count(i) == 3}
    return success_response(list(result))
    

def surveyJSON(response_id):
    json = {}
    with app.app_context():
        surveys = Survey.query.filter_by(response_id=response_id)
        questions = []
        answers = []
        for s in surveys:
            questions.append(s.question_id)
            answers.append(s.answer_text)
            time = s.time_of_submit.strftime("%d-%b-%Y (%H:%M:%S.%f)")
            addressed = s.addressed
        json = {
            "response_id": response_id,
            "questions": questions,
            "answers": answers,
            "time_stamp": time,
            "addressed" : addressed
        }
        #print(json)
    return json
    

def convertToCSV():
    with app.app_context():
        with sqlite3.connect("users.sqlite3") as connection:
            csvWriter = csv.writer(open("Survey.csv", "w"))
            records = Survey.query.all()
            for r in records:
                csvWriter.writerow([r.id, r.description, r.response_id
                , r.answer_text, r.question_id, r.time_of_submit, r.addressed])
            csvWriter = csv.writer(open("Question.csv", "w"))
            records = Question.query.all()
            for r in records:
                csvWriter.writerow([r.id, r.text, r.qtype, r.stype])


if __name__ == '__main__':
    convertToCSV()
    surveyJSON(2)
    app.run(host='0.0.0.0', port=105, debug=True)
    