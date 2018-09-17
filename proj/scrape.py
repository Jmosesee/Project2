# This module is used to scrape Indeed

import requests
from bs4 import BeautifulSoup
import itertools
from urllib.parse import parse_qs
import re

# Todo: consider adding a read_timeout to each requests.get() call, to avoid hanging in case of a slow response
# Todo: consider serving Indeed's cookie
# Fake browser visit
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}

# Todo: consider using keyword parameters
# Todo: experiment with multi-word queries
# Todo: test many combinations of constraints

# Scrape one page of search results from Indeed.  Generally the retured result will be a list of ten job URL's
def get_job_links_page(query, constraints, page):
    base_url = "https://www.indeed.com/jobs?"

    # Build a url to query Indeed
    url = base_url + 'q=' + query + '&' + constraints + '&start=' + str(10 * (page-1))
    print(url)

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    links = soup.find_all("a")
    # For the Indeed search just executed, Indeed will report the number of jobs found.
    # The code below scrapes this number from the html and assigns it to the found_jobs variabl
    search_count = soup.find(id="searchCount").get_text()
    found_jobs = list(map(int, re.findall('\d+', search_count.replace(',', ''))))[1]
    print("Found " + str(found_jobs) + " jobs")
    # build a list of job links
    some_links = []
    ids = []
    regex = r"-[a-zA-Z0-9]{16}\?"

    for l in links:
        link = None
        hyperlink = l.attrs.get('href')
        if (hyperlink):
            if ("/rc/clk?jk" in hyperlink):
                link = l.attrs.get('href')
                i = parse_qs(link).get('/rc/clk?jk')[0]
            else:
                match = re.search(regex, hyperlink)
                if (match):
                    link = match.string
                    i = match.group()[1: -1]
        if (link):
            some_links.append(link)
            ids.append(i) 

        # try:
        #     hyperlink = l.attrs.get('href')
            
            
        #     if ("/rc/clk?jk" in hyperlink):
        #         link = l.attrs.get('href')
        #         i = parse_qs(link).get('/rc/clk?jk')[0]
        #     else:
        #         match = re.search(regex, hyperlink)
        #         link = match.string()
        #         i = match.group()[1: -1]
        #     some_links.append(link)
        #     ids.append(i) 
        # except:
        #     pass
    
    job_links = ["https://www.indeed.com{}".format(x)
             for x in some_links
             ]
    print (len(job_links))
    print (job_links[0])
    return (job_links, found_jobs, ids)

# def get_job_links():
#     links = [get_job_links_page(x) for x in range(1, 5)]
#     merged = list(itertools.chain(*links))
#     parsed = [parse_qs(m) for m in merged]
#     # I think the fccid identifies the company posting the job?
#     fccid =  [p.get('fccid')[0] for p in parsed]
#     # I think this id uniquely identifies each job?
#     id = [p.get('https://www.indeed.com/rc/clk?jk')[0] for p in parsed]
#     return id

# get_job_links_page(1)

# Scrape the details of one job from Indeed
def get_job(link):
    attempts = 0
    
    # I don't know why this sometimes fails on the first try, but retrying seems to succeed.
    while attempts < 3:
        try:
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            jobtitle = soup.find(class_="jobsearch-JobInfoHeader-title").get_text()
            subtitle_divs = soup.find(class_="jobsearch-JobInfoHeader-subtitle").find("div").find_all("div")
            company = subtitle_divs[0].get_text()
            location = subtitle_divs[-1].get_text()
            job_summary = soup.find(class_="jobsearch-JobComponent-description").get_text()
            break
        except :
            attempts += 1
            jobtitle = "Not Available"
            company = "Not Available"
            location = "Not Available"
            job_summary = "Not Available"

    return {'job_summary': job_summary,
            'company': company,
            'location': location,
            'jobtitle': jobtitle}