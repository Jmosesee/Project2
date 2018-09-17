# Todo: There should be a boot script that will read data from the DB into memory

import pandas as pd
from nltk.tokenize import word_tokenize
from collections import defaultdict
from dynamodb_json import json_util as json
from nltk.tokenize import RegexpTokenizer

# def load_skills_list(dynamodb):
#     skills_df = pd.DataFrame(json.loads(dynamodb.Table('Skills').scan()['Items'])).fillna(False)
#     # skills.columns = ['skill_name']
#     skills['skill_name'] = skills.skill_name.map(lambda x: x.lower().strip())
#     return skills.skill_name.tolist()

def load_skills_df(dynamodb):# the macro enabled excel file. 
    skills = pd.DataFrame(json.loads(dynamodb.Table('Skills').scan()['Items'])).fillna(False)
    # tokenizer = RegexpTokenizer(r'[a-zA-Z0-9#+-]+')
    # if not skills.empty:
    #     skills['WL'] = [tokenizer.tokenize(skill_phrase) for skill_phrase in skills.get('skill_name')]

    return skills
    
# job_summary is a string
def tally_skill_mentions_in_job_summary(job_summary, skills):

    tokenizer = RegexpTokenizer(r'[a-zA-Z0-9#+-]+')
    if skills.empty:
        return {}
    skills_wl = [tokenizer.tokenize(skill_phrase) for skill_phrase in skills.get('skill_name')]
    skill_dict = {skill_phrase: 0 for skill_phrase in skills.get('skill_name')}
    # skill_mentions_in_job = defaultdict(int)
    # tokenize the text of the description, without spans
    tokenizer = RegexpTokenizer(r'[a-zA-Z0-9#+-]+')
    tokens = tokenizer.tokenize(job_summary)
    # create a dictionary of the words in the job description
    word_index = defaultdict(list)
    for i, k in enumerate(tokens):
        word_index[k].append(i)
    
    # search the word_index dictionary to find the first word of each skill_phrase
    for skill_phrase, skill_phrase_wl in zip(skills.get('skill_name'), skills_wl):
        if word_index.get(skill_phrase_wl[0]):
            for occurence in word_index.get(skill_phrase_wl[0]):
                # Check to see if the whole phrase matches
                if len(tokens) > (occurence + len(skill_phrase_wl)):
                    if all((skill_phrase_wl[j] == tokens[j+occurence]) for j in range(len(skill_phrase_wl))):
                        skill_dict[skill_phrase] += 1
    return skill_dict

def analyze(job, skills, analysis_table):
    tallied_skill_mentions = []
    job_summary = job['job_summary']
    if type(job_summary) == str:
        tallied_skill_mentions = tally_skill_mentions_in_job_summary(job_summary, skills)
        table_item = tallied_skill_mentions.copy()  # Shallow copy!  (Deep copy would be fine too)
        table_item['JobId'] = job['JobId']
        analysis_table.put_item(Item=table_item)
    else:
        tallied_skill_mentions = defaultdict(int)
    return tallied_skill_mentions

def reanalyze(analysis_df, skill, jobs_table):
    reanalysis = []
    for index, row in analysis_df.iterrows():
        response = jobs_table.get_item(Key={'JobId': index})
        job_summary = response['Item']['job_summary']
        #Todo: also need to reanalyze jobs in jobs_table_queue
        if type(job_summary) == str:
            tallied_skill_mentions = tally_skill_mentions_in_job_summary(job_summary, [skill])[skill]
        else:
            tallied_skill_mentions = 0
        reanalysis.append(tallied_skill_mentions)
    return reanalysis