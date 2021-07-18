#This script will scrape all job postings for a given position and location, for example: 'data scientist' 'New York, NY'
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from pandas import ExcelWriter
import pandas as pd
import re

'''
class Patient(object):
    Medical center patient
    
    status = 'patient'
    
    def  __init__(self, name, age):
        self.name = name
        self.age = age
        self.conditions = []
    
    def get_details(self):
        print(f'Patient record: {self.name}, {self.age} years'\
              f'Current information: {self.conditions}.')
    
    def add_info(self, information):
        self.conditions.append(information)

steve = Patient('Steve Mescouilles', 23)
dimitri = Patient('Dimitri Bouvier', 25)
'''

class Website:
     def __init__(self, name, url, titleTag, bodyTag):
        self.name = name
        self.url = url
        self.titleTag = titleTag
        self.bodyTag = bodyTag
        

def get_url(position,location):
    '''generate indeed url from position and location'''
    template = 'https://www.indeed.com/jobs?q={}&l={}'
    url = template.format(position,location)
    url = re.sub(' ','%20',url)
    url = re.sub(',','%2C',url)
    
    return url

url = get_url('economics','New York, NY')
            
print(url)

liste = []
job_title_list = []
company_list = []
job_location_list = []
job_posting_age_list = []
liste5 = []

def Url_Opener(url):
    try:    
        html = urlopen(url)
    except HTTPError as e:
        print(e)
            #return null, break, or do some other "Plan B"
    except URLError:
        print('The server could not be found!')
    try:
        return BeautifulSoup(html.read(),'html.parser')
    except AttributeError as e:
        return print(e)
    
    
#bs1 = Url_Opener('https://www.indeed.com/jobs?q=analytics&l=New+York%2C+NY')
bs1 = Url_Opener(url)

vision = str(bs1)
ExcelFile = pd.DataFrame({'job_title':['Null'],'company_name':['Null']
                          ,'job_location':['Null'],'posting_age_(days)':[0]
                          ,'href':['Null']})

job_id = bs1.find_all('a',{'id':re.compile('job\_.+')})
jobs_title = bs1.find_all('span',{'title':re.compile('[a-zA-z]+')})
all_the_text_data = bs1.find_all('span',{'class':'companyName'})
location_data = bs1.find_all('div',{'class':'companyLocation'})
posted_since = bs1.find_all('span',{'class':'date'})
#next_button = bs1.find_all('a',{'href':re.compile(r'/jobs?')})


for i in job_id:
        liste.append(i.attrs)


for i in jobs_title:
        job_title_list.append(i.attrs)
if len(liste) == len(job_title_list):
    for a in range(0,len(job_title_list)):
        liste[a]['job_title'] = job_title_list[a]['title']
    
#response = requests.get('https://www.indeed.com/jobs?q=analytics&l=New+York%2C+NY')
#soup = BeautifulSoup(response.text, 'html.parser')
#all_the_text_data = soup.find_all('span','companyName')

def find_str(s, char):
    index = 0
    
    if char in s:
        c = char[0]
        for ch in s:
            if ch == c:
                if s[index:index+len(char)] == char:
                    return index
            index += 1
    return -1

for b in all_the_text_data:
    if str(b).endswith('</a></span>'):
        company_list.append(str(b)[(find_str(str(b), '_blank">')+8):-11])  
    else:
        company_list.append(str(b)[(find_str(str(b), 'Name">')+6):-7])
for b in range(0,len(company_list)):
    if 'amp;' in company_list[b]:
        company_list[b] = re.sub('amp;', '', company_list[b])
    liste[b]['company_name'] = company_list[b]
    
for a in location_data:
    if 'span' not in str(a):
        job_location_list.append(str(a)[(find_str(str(a), 'tion">')+6):-6])
    elif '<!-- -->' in str(a):
        job_location_list.append(str(a)[(find_str(str(a), 'tion">')+6):(find_str(str(a), '<!-- -->'))])
    else:
        job_location_list.append(str(a)[(find_str(str(a), 'tion">')+6):(find_str(str(a), '<span'))])
for a in range(0,len(job_location_list)):
    if '<!-- -->' in job_location_list[a]:
        job_location_list[a] = job_location_list[a][:(find_str(job_location_list[a], '<!-- -->'))]
    liste[a]['job_location'] = job_location_list[a]

for a in posted_since:
    job_posting_age_list.append(str(a)[(find_str(str(a), 'te">')+4):-7])
for a in range(0,len(job_posting_age_list)):
    if job_posting_age_list[a] == 'Today' or job_posting_age_list[a] == 'Just posted':
        job_posting_age_list[a] = 0
    else:
        job_posting_age_list[a] = int(re.sub('[^0-9]', '', job_posting_age_list[a]))
    liste[a]['posting_age_(days)'] = job_posting_age_list[a]
count = 1

next_button = bs1.find_all('a',{'aria-label':'Next'})

for a in range(0,len(liste)):
    liste[a]['href'] = f"https://www.indeed.com{liste[a]['href']}"
    for attribute in ['class','data-hide-spinner','data-jk','data-mobtk'
                      ,'rel','target','id']:
        del liste[a][attribute]       
    ExcelFile = ExcelFile.append(liste[a],ignore_index=True,sort=False)

ExcelFile = ExcelFile.iloc[1:,:]

#next_url_full = str(next_button)

#next_pp = str(next_button)[(find_str(str(next_button), 'data-pp="')+9):(find_str(str(next_button), '" href="'))]

#next_url = 'https://indeed.com' + str(next_button)[(find_str(str(next_button), 'href="')+6):(find_str(str(next_button), '" onmousedown'))] + ''

#for a in next_button:
pages_count = 10
while(len(str(next_button)[(find_str(str(next_button), 'href="')+6):(find_str(str(next_button), '" onmousedown'))])) >0:
#while count < 1000:
    next_button = bs1.find_all('a',{'aria-label':'Next'})
    #next_url = 'https://indeed.com' + str(next_button)[(find_str(str(next_button), 'href="')+6):(find_str(str(next_button), '" onmousedown'))] #+ '&pp=' + str(next_button)[(find_str(str(next_button), 'data-pp="')+9):(find_str(str(next_button), '" href="'))]
    next_url = url + f'&start={pages_count}'
    print(next_url)
    pages_count = pages_count +10
    bs1 = Url_Opener(next_url)
    job_id = bs1.find_all('a',{'id':re.compile('job\_.+')})
    jobs_title = bs1.find_all('span',{'title':re.compile('[a-zA-z]+')})
    all_the_text_data = bs1.find_all('span',{'class':'companyName'})
    location_data = bs1.find_all('div',{'class':'companyLocation'})
    posted_since = bs1.find_all('span',{'class':'date'})
    next_button = bs1.find_all('a',{'aria-label':'Next'})
    
    liste_loop = []
    job_title_list_loop = []
    company_list_loop = []
    job_location_list_loop = []
    job_posting_age_list_loop = []
    
    
    
    for i in job_id:
        liste_loop.append(i.attrs)

    
    for i in jobs_title:
            job_title_list_loop.append(i.attrs)
    if len(liste_loop) == len(job_title_list_loop):
        for a in range(0,len(job_title_list_loop)):
            liste_loop[a]['job_title'] = job_title_list_loop[a]['title']
            
    for b in all_the_text_data:
        if str(b).endswith('</a></span>'):
            company_list_loop.append(str(b)[(find_str(str(b), '_blank">')+8):-11])  
        else:
            company_list_loop.append(str(b)[(find_str(str(b), 'Name">')+6):-7])
    for b in range(0,len(company_list_loop)):
        liste_loop[b]['company_name'] = company_list_loop[b]
        
    for a in location_data:
        if 'span' not in str(a):
            job_location_list_loop.append(str(a)[(find_str(str(a), 'tion">')+6):-6])
        elif '<!-- -->' in str(a):
            job_location_list_loop.append(str(a)[(find_str(str(a), 'tion">')+6):(find_str(str(a), '<!-- -->'))])
        else:
            job_location_list_loop.append(str(a)[(find_str(str(a), 'tion">')+6):(find_str(str(a), '<span'))])
    for a in range(0,len(job_location_list_loop)):
        if '<!-- -->' in job_location_list_loop[a]:
            job_location_list_loop[a] = job_location_list_loop[a][:(find_str(job_location_list_loop[a], '<!-- -->'))]
        liste_loop[a]['job_location'] = job_location_list_loop[a]
    #for i in range(0,len(liste_loop)):
        #print(liste_loop[i]['id'])
    for a in posted_since:
        job_posting_age_list_loop.append(str(a)[(find_str(str(a), 'te">')+4):-7])
    for a in range(0,len(job_posting_age_list_loop)):
        if job_posting_age_list_loop[a] == 'Today' or job_posting_age_list_loop[a] == 'Just posted':
            job_posting_age_list_loop[a] = 0
        else:
            job_posting_age_list_loop[a] = int(re.sub('[^0-9]', '', job_posting_age_list_loop[a]))
        liste_loop[a]['posting_age_(days)'] = job_posting_age_list_loop[a]
    #for a in range(0,len(liste_loop)):
        #liste.append(liste_loop[a][1:])
    for a in range(0,len(liste_loop)):
        liste_loop[a]['href'] = f"https://www.indeed.com{liste_loop[a]['href']}"
        for attribute in ['class','data-hide-spinner','data-jk','data-mobtk'
                          ,'rel','target','id']:
            del liste_loop[a][attribute]       
        ExcelFile = ExcelFile.append(liste_loop[a],ignore_index=True,sort=False)
    print(f'page passed : {count}, job listings count:{len(ExcelFile)}')
    count= count +1
