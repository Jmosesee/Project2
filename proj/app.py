# This module serves a Flask app asynchronously using Celery.
# This video is very helpful in understanding this: https://www.youtube.com/watch?v=iwxzilyxTbQ
# To get this running follow these steps:
# 1: Open a terminal window
# 2: Enter the following command to activate the PythonData environment:
#    $ source activate PythonData
# 3. Navigate into the ~/environment/proj folder
# 4. Enter the following command to start the Celery worker and beat:
#    $ celery -A app.celery worker --loglevel=info -B
# 5: Open a second terminal window
# 6. Navigate into the ~/environment/proj folder
# 7: Enter the following command to activate the PythonData environment in the second terminal:
#    $ source activate PythonData
# 8: Enter the following command to start the Flask app:
#    $ python3 app.py

# Todo: Create a readme file for this project
# Todo: Use Github to manage this code
# Todo: Consider separating the DynamoDB interface into a new module

from flask import Flask, jsonify, request
from flask_cors import CORS
import boto3
from flask_celery import make_celery
from scrape import get_job_links_page, get_job
from urllib.parse import parse_qs, urlencode
import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
skill_table = dynamodb.Table('Skills')
constraints_table = dynamodb.Table('Constraints')
jobs_table = dynamodb.Table('Jobs')
scraped_jobs = []  # This list temporarily holds scraped job data in RAM until put_job() gets around to putting it into DynamoDB

flask_app = Flask(__name__)
CORS(flask_app)
flask_app.config.update(
    CELERY_BROKER_URL='redis://project2-unclustered.7xt2wp.0001.use2.cache.amazonaws.com:6379',
    CELERY_RESULT_BACKEND='redis://project2-unclustered.7xt2wp.0001.use2.cache.amazonaws.com:6379'
)
celery = make_celery(flask_app)

@flask_app.route('/')
def hello_world():
    return 'Hello, World!'

# The return value for these routes is not being used for anything.  Feel free to change it to something useful
@flask_app.route("/do-have/<skill>")
def do_have(skill):
    sk = {"SkillId": skill, "have": True}
    skill_table.put_item(Item=sk)
    scrape.delay(skill)
    return 'Inserted: ' + skill

@flask_app.route("/dont-have/<skill>")
def dont_have(skill):
    sk = {"SkillId": skill, "have": False}
    skill_table.put_item(Item=sk)
    return 'Inserted' + skill

# This route is used to capture the search constraints
@flask_app.route("/jobs/")
def jobs():
    # return request.query_string
    constraints = {k: v for k,v in request.args.items()}
    skill = constraints.pop('q')
    sk = {"SkillId": skill, "have": True}
    skill_table.put_item(Item=sk)
    # # after popping q from a, the remaining parameters are the constraints
    encoded = urlencode(constraints)
    c={'ConstraintId': 1, 'Constraint': encoded}
    constraints_table.put_item(Item=c)
    # return 'Inserted: ' + ", ".join(skill)
    return jsonify(sk)

# The reason for this celery beat is to avoid overloading the very limited throughput capacity of our Amazon DynamoDB.
# We can always raise the capacity if we want to.  Still, it's nice to have control of it, thus.
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(2.0, put_job.s(), name='beat for put_job')

# Scrape data about one job from Indeed
@celery.task(name='app.scrape_job')
def scrape_job(id, link):
    j = get_job(link)
    j['JobId'] = id
    j['link'] = link
    # print(j['company'])
    # jobs_table.put_item(Item=j)
    scraped_jobs.append(j)
    # print(len(scraped_jobs))

#Put this one job's data into the jobs table of the database
@celery.task
def put_job():
    print (len(scraped_jobs))
    if len(scraped_jobs) > 0:
        jobs_table.put_item(Item=scraped_jobs.pop())

# Scrape a list of job links by searching Indeed
@celery.task(name='app.scrape')
def scrape(query):
    response = constraints_table.get_item(Key={'ConstraintId': 1})
    # query = "data scientist"
    constraints = response['Item']['Constraint']
    for page in range(1,100):
        (links, found_jobs, ids) = get_job_links_page(query, constraints, page)
        zipped = list(zip(ids, links))
        jobs = [{"JobId": i, "link": l} for i,l in zipped]
        with jobs_table.batch_writer() as batch:
            for j in jobs:
                batch.put_item(Item=j)
        for i,l in zipped:
            response = scrape_job.delay(i,l)
        if found_jobs < (page*10):
            break

    now = datetime.datetime.now().isoformat()
    sk = {"SkillId": query,
            "have": True,
            "last_searched": now}
    skill_table.put_item(Item=sk)


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8080)
    