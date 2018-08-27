# Enhanced Job Search
___
## The problem:
Nearly 10 jobs per second are added to the www.indeed.com website.  Which one is the best match for you?  Without automatic searching and sorting, finding your own perfect opportunity by reading each listing would be an impossible task.  The website does offer search tools, but even with the use of these tools, finding the most relevant job listings may be extremely time consuming.  For example, on August 26, 2018, a search for the job title, "data scientist," in, "Denver, CO," produced 760 listings.  A smorgasbord of possibilities!  However, most data science job seekers would not be qualified for most of these jobs.  For example, the first job listed requires a Masters degree or PhD; the second job listed requires an, "advanced degree in applied statistics or epidemiology;" the third job listed requires experience with Java, etc.  A job applicant may have hundreds of marketable skills, and there may be hundreds of job requirements that the same applicant cannot meet, but the search tools provided by the Indeed website are meant for entering only a small number of search terms at a time.
___
## The solution:
The goal of this project is to create tools for enhanced job searching on Indeed.com.  The project outcome will incorporate:

|  Technology  |  Use in this project  |
|--------------|-----------------------|
| Javascript-based Chrome browser extension | User interface |
| MongoDB | Store user input and scraped results |
| Python Flask RESTful API | Two-way pipeline between browser-based user interface and database storage |
| Python-based web scraping | Gather job listing data from www.indeed.com |
| nltk for Python | Process job descriptions |
| pandas for Python | Aggregate job skill data |
| Plotly | Draw graphs |
| HTML page with a local Web Server | Present results |

### Inputs
The Chrome browser extension will be active only when the user is visiting www.indeed.com or the localhost.  When the user first begins to use the extension, it won't do anything because it won't have any data.  It will begin to collect data as soon as the user first searches Indeed.com, and will continue to gather inputs and produce results as the user continues searching.

#### Capturing search requests
The brower extension will use the chrome.webRequest API to observe the search requests made by the user at the Indeed.com site.  It will forward this search request to a Python program by posting it to the Flask API.  The Python program will record the search terms, interpreting them as, "Skills I have."

#### Entering skills via context menu
The browser extension will add two new options to the context menu (accessed with a right mouse click): "I have this skill," and, "I don't have this skill." As the user is reviewing a job listing, they can select any word or phrase in the listing and then choose, "I have this skill," or, "I don't have this skill."  The extension will forward the selected word or phrase through the Flask API to the appropriate list in the Mongo DB.  These lists will be used in several ways as explained below.  Here is an example of how the context menu might appear:
![alt text](/Context%20menu%20example.PNG "Context menu example")


#### Scraping www.indeed.com
While Chrome shows only one page of search results to the user at a time, the Python program will silently scrape Indeed.com, using the constraints and search terms entered by the user and observed through the chrome.webRequest API.  The Python program will gather all results, for each search, into a Mongo DB.  Any word or phrase identified by the user, either by being manually entered as a search term into the Indeed.com website, or selected through the context menu as, "I have this skill," will be used by the Python program as a search term to scrape job listings from the site.

### Analysis
#### nltk
Python's nltk package will be used to search each job description for mentions of each word or phrase identified as, "Skills I have," and, "Skills I don't have."

#### Pandas
Python's pandas package will be used to tabulate and tally the total number of mentions of each skill in each job description.  By adding a positive score to each mention of, "Skills I have," and a negative score to each mention of, "Skills I don't have," it will assign an overall relevance score to each job listing scraped.  It will keep this table sorted so that the most relevant jobs appear first.

Pandas will also use this table to identify which of the user's skills are the most valuable, by calculating which skills are yielding the most relevant job opportunities for the user.  All scraped job listings are included in this calculation, but each mention of a skill in a job with higher relevance has a higher weight, in the total score for each skill, than mentions of the skill in jobs with lower relevance.

Similarly, pandas will also use this table to identify, of the skills in the, "Skills I don't have," list, which lacking skills are most limiting the user's opportunities.  Here again, although all scraped listings are included, mentions in jobs with higher relevance to the user have more weight than mentions in jobs with lower relevance.

### Outputs
#### Skill phrase highlighting
Skills selected by the user via the browser extension context menu will be collected into two lists stored in the Mongo DB: "Skills I have," and, "Skills I don't have."  Whenever the user is browsing Indeed.com, the browser extension will then find these words or phrases in each job listing as it is displayed, and highlight these skills, in green, for, "Skills I have," or in red, for, "Skills I don't have."  Here is an example of how the highlighting for, "Skills I have," might appear:
![alt text](/Highlighting%20example.PNG "Highlighting example")

#### Locally hosted web page
##### Most relevant listings
A locally hosted web page will list jobs determined by the Python program to be the most relevant to the user's skills.  It will be similar in appearance to Indeed's search results page, showing a few lines summarizing each job, and linking to the full listing on the Indeed site.  Its findings will be superior, however, to the findings of any single search using Indeed's search tools, because its scoring will be based on having collected multiple inputs from the user, as they continue to enter data using the extension.

##### Most valuable skills
The locally hosted web page will also present two bar charts, drawn by Plotly, for visualizing the relative value of each of the user's skills, and lacked skills, in terms of the number of relevant job listings requiring each skill.  This informs the user of the relative significance of each of their own strengths and weaknesses.

### Bonus
After the core project requirements are accomplished, if time allows, the project could be expanded by allowing the user to assign an importance score to each skill.  For example, the user might include both, "Python," and "HTML," in the list of, "Skills I have," but they may prefer Python to HTML, and therefore want to give job listings mentioning, "Python," a higher ranking than job listings mentioning, "HTML."  An advanced version of the project could include development of this capability.
