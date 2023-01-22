import csv
import os
import requests
import tqdm.auto
import time
import re
import os
import pandas as pd
from get_faculty_info import *
from bs4 import BeautifulSoup

base_url = "http://catalog.mit.edu"
catalog_soup = BeautifulSoup(requests.get(base_url).text, features="html.parser")
schools = catalog_soup.find_all(class_="nav levelthree")[3:29] # doing 3:29 because that currently gives all of the links to school sites

# check if csv file for professors already exists
if os.path.exists('mit_professor_data_raw.csv'):
    exist_flag = True
    df = pd.read_csv('mit_professor_data_raw.csv')
else:
    exist_flag = False

# obtain all strings like /schools/{school_name}/{sub_school}
string = str(catalog_soup)
pattern = re.compile(r"/schools/(\w+[-\w]+)/(\w+[-\w]+)/")
matches = pattern.finditer(string)
school_hrefs = list(set([x.group() for x in matches]))

print("Gathering professor info...")

keys = set()
professors = []
pbar = tqdm.tqdm()
for school_href in school_hrefs:
    school_name = school_href.split('/')[-2] # get the sub_school name
    url = base_url + school_href + "#facultystafftext" # get the url of all faculty
    page = ''
    while page == '':
        try:
            page = requests.get(url)
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    faculty_soup = BeautifulSoup(page.text, features="html.parser")
    faculty_list = faculty_soup.find_all(class_="noindent name")
    for faculty in faculty_list:
        item = {}
        name = faculty.text.split(',')[0]
        item["name"] = name
        item["school_affiliation"] = school_name
        if not exist_flag:
            # get_faculty_info() -> This function should be able to obtain a brief description about a faculty member given the faculty name. Should return a string containing keywords or brief description of their research interests.
            keywords = get_faculty_info(name,school_name)
            item["keywords"] = keywords
            keys.update(item.keys())
            professors.append(item)
        else:
            if name not in df.name.to_numpy(): # only continue if the name is not already in the datafrane
                # get_faculty_info() -> This function should be able to obtain a brief description about a faculty member given the faculty name. Should return a string containing keywords or brief description of their research interests.
                keywords = get_faculty_info(name,school_name)
                item["keywords"] = keywords
                keys.update(item.keys())
                professors.append(item)
        pbar.update()

print("Writing professor data...")
if not exist_flag:
    with open("mit_professor_data_raw.csv", "w", newline="\n", encoding="utf8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for c in tqdm.tqdm(professors):
            writer.writerow(c)
else:
    with open("mit_professor_data_raw.csv", "a", newline="\n", encoding="utf8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        for c in tqdm.tqdm(professors):
            writer.writerow(c)
