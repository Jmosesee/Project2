# This module serves a Flask app asynchronously using Celery.
# This video is very helpful in understanding this: https://www.youtube.com/watch?v=iwxzilyxTbQ
# To get this running follow these steps:
# 1: Open a terminal window
# 2: Enter the following command to activate the PythonData environment:
#    $ source activate PythonData
# 3. Navigate into the project folder
# 4. Enter the following command to start the Celery worker and beat:
#    $ celery -A app.celery worker --loglevel=info -B
# 5: Open a second terminal window
# 6. Navigate into the project folder
# 7: Enter the following command to activate the PythonData environment in the second terminal:
#    $ source activate PythonData
# 8: Enter the following command to start the Flask app:
#    $ python3 app.py

# Here we have a Flask app and a Celery worker in the same file.
# The two processes have access to the variable names defined globally here
# However, they do not share memory, so they are using two different copies of those variables!

# Todo: Find a way to simplify the above architecture.
# Todo: Can we create a boot script that will do the above whenever our virtual machine boots?
# Todo: Create a readme file for this project
# Todo: Use Github to manage this code
# Todo: Consider separating the DynamoDB interface into a new module
# Todo: Consider applying OOP principles

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import boto3
from flask_celery import make_celery
from urllib.parse import parse_qs, urlencode
import datetime
import pandas as pd
from collections import defaultdict
from dynamodb_json import json_util as json

from scrape import get_job_links_page, get_job
from analysis import analyze, reanalyze

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
skill_table = dynamodb.Table('Skills')
constraints_table = dynamodb.Table('Constraints')
jobs_table = dynamodb.Table('Jobs')
jobids_table = dynamodb.Table('JobIds')
analysis_table = dynamodb.Table('Analysis')

# jobs_table_queue is for use by Celery and only Celery.
# scrape_job() appends to it and put_job() pops from it.
jobs_table_queue = []  # This list temporarily holds scraped job data in RAM until put_job() gets around to putting it into DynamoDB

# Todo: Could skills change after being passed into a celery function?
# analysis_df = pd.DataFrame()

flask_app = Flask(__name__)
CORS(flask_app)
flask_app.config.update(
    CELERY_BROKER_URL='redis://project2-2.7xt2wp.ng.0001.use2.cache.amazonaws.com:6379',
    CELERY_RESULT_BACKEND='redis://project2-2.7xt2wp.ng.0001.use2.cache.amazonaws.com:6379'
)
celery = make_celery(flask_app)

@flask_app.route('/')
def hello():
    # return 'Hello, World!'
    return render_template('index.html', name=None)

def put_skill(skill, have):
    global skills   # As a reminder, don't do this in a celery function, but only in flask functions.
    
    sk = {"skill_name": skill, "have": True}
    print ("Before append:")
    print (skills)
    skills = skills.append(sk, ignore_index=True)
    print ("After append:")
    print (skills)
    skill_table.put_item(Item=sk)
    return 'Inserted: ' + skill
    
# The return value for these routes is not being used for anything.  Feel free to change it to something useful
@flask_app.route("/do-have/<skill>")
def do_have(skill):
    # global analysis_df
    
    # Todo: consider functionizing the next 3 lines of code
    r = put_skill(skill, True)
    # Todo: How long does reanalyzing take?  Should it be handled by celery?
    #analysis_df[skill] = reanalyze(analysis_df, skill, jobs_table, analysis_table)
    reanalyze(skill, jobs_table, analysis_table)
    scrape.delay(skill, skills)
    return r

@flask_app.route("/dont-have/<skill>")
def dont_have(skill):
    return put_skill(skill, False)

# This route is used to capture the search constraints
@flask_app.route("/jobs/")
def jobs():
    # global analysis_df
    
    constraints = {k: v for k,v in request.args.items()}
    skill = constraints.pop('q')
    # Todo: consider functionizing the next 3 lines of code
    r = put_skill(skill, True)
    # Todo: How long does reanalyzing take?  Should it be handled by celery?
    # analysis_df[skill] = reanalyze(analysis_df, skill, jobs_table, analysis_table)
    # analysis_df.append(scrape.delay(skill, skills.to_json()))
    reanalyze(skill, jobs_table, analysis_table)
    scrape.delay(skill, skills.to_json())
    # after popping q from a, the remaining parameters are the constraints
    # Todo: Also need to strip the start page
    encoded = urlencode(constraints)
    c={'ConstraintId': 1, 'Constraint': encoded}
    constraints_table.put_item(Item=c)
    return ("OK")

def sort_jobs(df):
    if 'Score' in df.columns:
        df.drop('Score', axis=1)
    df['Score'] = df.sum(axis = 1)
    return df.sort_values('Score', ascending=False)

@flask_app.route("/get-top-jobs/")
def get_top_jobs():
    # global analysis_df
    # analysis_df.drop('Score')
    # analysis_df['Score'] = analysis_df.sum(axis = 1)
    # analysis_df = analysis_df.sort_values('Score', ascending=False)
    # now analysis_df is local
    analysis_df = pd.DataFrame(json.loads(analysis_table.scan()['Items'])).fillna(False)
    analysis_df = sort_jobs(analysis_df)
    top_jobs_df = pd.DataFrame()
    # print("Length of analysis_df: "+ str(len(analysis_df)))
    for row in range(0,10):
        if row >= len(analysis_df):
            break
        print ("Score: " + str(analysis_df.iloc[row]['Score']))
        JobId = analysis_df.iloc[row]['JobId']
        response = jobs_table.get_item(Key={'JobId': JobId})
        job = response['Item']
        top_jobs_df = top_jobs_df.append(pd.DataFrame(job, index=[JobId]))
    return top_jobs_df.to_json()

@flask_app.route("/get-top-skills/")
def get_top_skills():
    # global analysis_df
    # now analysis_df is local
    analysis_df = pd.DataFrame(json.loads(analysis_table.scan()['Items'])).fillna(False)
    analysis_df = sort_jobs(analysis_df)
    trimmed_df = analysis_df.copy()
    if 'JobId' in trimmed_df.columns:
        trimmed_df = trimmed_df.drop('JobId', axis=1)
    skill_scores = 3 * trimmed_df.iloc[0:10].sum(axis=0)
    skill_scores += 2 * trimmed_df.iloc[10:20].sum(axis=0)
    skill_scores += 1 * trimmed_df.iloc[20:30].sum(axis=0)
    return skill_scores.to_json()
    
@flask_app.route("/get-skills/")
def get_skills():
    # response = skill_table.scan()
    # skills = response['Items']
    print(skills)
    return skills.to_json()

# Celery functions cannot use global variables.  If they try, they will get their own separate copy of them!    

# The reason for this celery beat is to avoid overloading the very limited throughput capacity of our Amazon DynamoDB.
# We can always raise the capacity if we want to.  Still, it's nice to have control of it, thus.
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(3.0, put_job.s(), name='beat for put_job')

# Scrape data about one job from Indeed
@celery.task(name='app.scrape_job')
def scrape_job(id, link, json_skills):
    skills = pd.read_json(json_skills)  # Pandas dataframes can't be passed directly into celery tasks
    j = get_job(link)
    j['JobId'] = id
    j['link'] = link
    # jobs_table.put_item(Item=j)
    jobs_table_queue.append(j)
    print("Passing job to analyze")
    d = analyze(j, skills, analysis_table)
    # if len(d.keys()) == len(d.values()):
    # analysis_df.loc[id] = d
    return d
    # return pd.DataFrame(d, index=[id])

#Put one job's data into the jobs table of the database
@celery.task
def put_job():
    print (len(jobs_table_queue))

    if len(jobs_table_queue) > 0:
        batch_count = 0;
        with jobs_table.batch_writer() as batch:
            while len(jobs_table_queue) > 0 and batch_count < 10:
                j = jobs_table_queue.pop()
                if (j):
                    batch.put_item(Item = j)
                    batch_count += 1
                    
# Scrape a list of job links by searching Indeed
@celery.task(name='app.scrape')
def scrape(query, json_skills):
    # scraped_analysis = pd.DataFrame()
    print("Commencing scrape")
    # if query not in analysis_df.columns:
    #     analysis_df[query] = pd.Series([0] * len(analysis_df), index=analysis_df.index)

    response = constraints_table.get_item(Key={'ConstraintId': 1})
    # query = "data scientist"
    constraints = response['Item']['Constraint']
    for page in range(1,3):
        (links, found_jobs, ids) = get_job_links_page(query, constraints, page)
        zipped = list(zip(ids, links))
        jobs = [{"JobId": i, "link": l} for i,l in zipped]
        with jobids_table.batch_writer() as batch:
            for j in jobs:
                batch.put_item(Item={'JobId': j['JobId']})
        with jobs_table.batch_writer() as batch:
            for j in jobs:
                batch.put_item(Item=j)
        for i,l in zipped:
            d = scrape_job.delay(i, l, json_skills)
            # Todo: Improve efficiency by gathering these dictionaries into a list and then appending to the dataframe as a batch
            # scraped_analysis = scraped_analysis.append(pd.DataFrame(d, index=[i]))
        if found_jobs < (page*10):
            break

    print ("Found: " + str(found_jobs) + "jobs")
    now = datetime.datetime.now().isoformat()
    sk = {"skill_name": query,
            "have": True,
            "last_searched": now}
    # Todo: Consider doing this earlier
    skill_table.put_item(Item=sk)
    # return scraped_analysis

# skills is a Flask variable
skills = pd.DataFrame(json.loads(skill_table.scan()['Items'])).fillna(False)
# Todo: Make skill_name the index
# print(skills)
# if not skills.empty:
#     for skill in skills.get('skill_name'):
#         if skill not in analysis_df.columns:
#             analysis_df[skill] = pd.Series([0] * len(analysis_df), index=analysis_df.index)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8080, ssl_context='adhoc')

    