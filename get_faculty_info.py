import requests
import time
from bs4 import BeautifulSoup
from extract_keywords import *

def get_faculty_info(name,school_name):
    base_url = "https://dspace.mit.edu/discover"
    query = f'?scope=%2F&query="{name.replace(" ", "+")}"+"{school_name}"&submit=Go&rpp=20&sort_by=dc.date.issued_dt&order=desc'
    url = base_url + query
    res = ''
    while res == '':
        try:
            res = requests.get(url)
            if name not in res.text:
                raise('An error has occurred.')
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    soup = BeautifulSoup(res.text, 'html.parser')
    faculty_info = soup.find_all(class_="artifact-title")
    keywords = "; ".join([x.text.strip() for x in faculty_info])
    time.sleep(3) # had to add this due to rate limits...
    return keywords