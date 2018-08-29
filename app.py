from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.json_util import dumps

client = MongoClient('localhost', 27017)
db = client.job_search
skills_coll = db.skills
constraints_coll = db.constraints

app = Flask(__name__)

@app.route("/do-have/<skill>")
def do_have(skill):
    sk = {"name": skill, "have": True}
    skills_coll.insert_one(sk)
    return 'inserted' + skill

@app.route("/dont-have/<skill>")
def dont_have(skill):
    sk = {"name": skill, "have": False}
    skills_coll.insert_one(sk)
    return 'inserted' + skill

@app.route("/get/")
def get():
    return dumps([d for d in skills_coll.find()])

@app.route("/jobs/")
def jobs():
    # return request.query_string
    a = dict(request.args)

    skill = a.pop('q')
    sk = {"name": skill, "have": True}
    skills_coll.insert_one(sk)
    # after popping q from a, the remaining parameters are the constraints
    constraints_coll.insert_one(a)

    return 'inserted' + ", ".join(skill)

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()

