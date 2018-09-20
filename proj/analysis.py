import pandas as pd
from nltk.tokenize import word_tokenize
from collections import defaultdict
from dynamodb_json import json_util as json
from nltk.tokenize import RegexpTokenizer
import re

# job_summary is a string
def tally_skill_mentions_in_job(job_summary, job_title, skills):

    skill_dict = {}
    # print ("Skills: ")
    # print (skills)
    for index, row in skills.iterrows():
        s = row['skill_name']
        # print (s)
        pattern = re.compile(s + r'[^\w]', flags=re.I)
        # print (pattern)
        skill_dict[s] = len(re.findall(pattern, job_title)) + len(re.findall(pattern, job_summary))
    
    # print (skill_dict)
    return skill_dict

def analyze(job, skills, analysis_table):
    # print ('Beginning job analysis')
    tallied_skill_mentions = []
    job_summary = job['job_summary']
    job_title = job['jobtitle']
    if type(job_summary) == str:
        tallied_skill_mentions = tally_skill_mentions_in_job(job_summary, job_title, skills)
        table_item = tallied_skill_mentions.copy()  # Shallow copy!  (Deep copy would be fine too)
        table_item['JobId'] = job['JobId']
        analysis_table.put_item(Item=table_item)
    else:
        tallied_skill_mentions = defaultdict(int)
    print (tallied_skill_mentions)
    return tallied_skill_mentions

def reanalyze(skill, jobs_table, analysis_table):
    #Todo: also need to reanalyze jobs in jobs_table_queue
    analysis_response = analysis_table.scan()['Items']
    with analysis_table.batch_writer() as batch:
        # Go through the whole analysis table in the database and find each of its jobs in the job table and reanalyze it
        for table_item in analysis_response:
            try: 
                response = jobs_table.get_item(Key={'JobId': table_item['JobId']})
                job_summary = response['Item']['job_summary']
                job_title = response['Item']['job_summary']
                if type(job_summary) == str:
                    tallied_skill_mentions = tally_skill_mentions_in_job(job_summary, job_title, pd.DataFrame({"skill_name": [skill], "have": [True]}))[skill]
                else:
                    tallied_skill_mentions = 0
                table_item[skill] = tallied_skill_mentions
                batch.put_item(Item = table_item)
            except ClientError:
                pass
        # Then go through the queue of jobs waiting to be written to the jobs table and reanalyze them too
        # for j in jobs_table_queue:
        #     id = j['JobId']
        #     job_summary = j['job_summary']
        #     job_title = j['job_title']
        #     if type(job_summary) == str:
        #         tallied_skill_mentions = tally_skill_mentions_in_job(job_summary, job_title, pd.DataFrame({"skill_name": [skill], "have": [True]}))[skill]
        #     else:
        #         tallied_skill_mentions = 0
        #     # Find the existing analyzsis for that job
        #     response = analysis_table.get_item(Key={'JobId': id})
        #     response['Item'][skill] = tallied_skill_mentions
        #     batch.put_item(Item = response['Item'])
          