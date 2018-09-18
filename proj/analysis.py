# Todo: There should be a boot script that will read data from the DB into memory

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
    # analysis_df is local
    analysis_df = pd.DataFrame(json.loads(analysis_table.scan()['Items'])).fillna(False)
    reanalysis = []
    with analysis_table.batch_writer() as batch:
        for index, row in analysis_df.iterrows():
            response = jobs_table.get_item(Key={'JobId': index})
            job_summary = response['Item']['job_summary']
            job_title = response['Item']['job_summary']
            #Todo: also need to reanalyze jobs in jobs_table_queue
            if type(job_summary) == str:
                tallied_skill_mentions = tally_skill_mentions_in_job(job_summary, job_title, [skill])[skill]
            else:
                tallied_skill_mentions = 0
            reanalysis.append(tallied_skill_mentions)
            table_item = tallied_skill_mentions.copy()  # Shallow copy!  (Deep copy would be fine too)
            table_item['JobId'] = index
            batch.put_item(Item=table_item)
    return reanalysis