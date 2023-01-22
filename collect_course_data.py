import csv
import os
import requests
import tqdm
from bs4 import BeautifulSoup

base_url = "http://catalog.mit.edu"
catalog_soup = BeautifulSoup(requests.get(base_url).text, features="html.parser")
subjects = catalog_soup.find_all(id="/subjects/")[0].find_all("a")

print("Gathering course info...")

keys = set()
courses = []
pbar = tqdm.tqdm()
for subject_item in subjects:
    url = base_url + subject_item.get_attribute_list("href")[0] # href is short for hypertext reference, used to specify the destination of the link. Create hyperlinks that link to other web pages or to specific locations within the same page
    subject_soup = BeautifulSoup(requests.get(url).text, features="html.parser")
    subj_courses = subject_soup.find_all("div", class_="courseblock")
    for course in subj_courses:
        item = {}
        title = course.find_all("strong")[0].text
        title_tokens = title.split()
        course_number = title_tokens[0]
        title = " ".join(title_tokens[1:])
        item["title"] = title
        item["course_number"] = course_number
        for info in course.find_all("p"):
            attr = info.get_attribute_list("class")[0].replace("courseblock", "")
            addl = info.find_all("span")
            if len(addl) > 0:
                for addl_info in addl:
                    text = addl_info.get_text().split("\n")
                    text = text[0] if len(text) == 1 else text
                    try:
                        addl_attr = addl_info.get_attribute_list("class")[0].replace(
                            "courseblock", ""
                        )
                        item[addl_attr] = text
                    except:
                        try:
                            assert attr not in item
                            item[attr] = text
                        except:
                            if type(item[attr]) is not list:
                                item[attr] = [item[attr]]
                            item[attr].append(text)
            else:
                text = info.get_text().split("\n")
                text = text[0] if len(text) == 1 else text
                item[attr] = text
        keys.update(item.keys())
        courses.append(item)
        pbar.update()
print("Writing course catalog...")
with open("mit_course_catalog_raw.csv", "w", newline="\n", encoding="utf8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=keys)
    writer.writeheader()
    for c in tqdm.tqdm(courses):
        writer.writerow(c)
