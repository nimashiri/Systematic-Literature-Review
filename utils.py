from urllib.parse import urlencode
from google.cloud import logging as gc_logging
import pandas as pd
import numpy as np
import os, logging, re, csv, json, bs4, random, requests, time
from bs4 import BeautifulSoup as soup
import urllib.parse

def jsonWriter(file, filename):
  with open(filename+'.json', 'a', encoding='utf-8') as f:
      json.dump(file, f, ensure_ascii=False)

def newWriter(paper_list, filename):
  result_file = open(filename+".csv",'a', newline='')
  wr = csv.writer(result_file, dialect='excel')
  wr.writerows([[item] for item in paper_list])


def write_to_csv(paper_list, filename):
  with open(filename+".csv", "a", newline="") as f:
      writer = csv.writer(f, dialect='excel', delimiter='\n')
      writer.writerow(paper_list)

def parse_title(title_list):
  string_list = []
  for item in title_list:
    if isinstance(item, bs4.element.Tag):
      string_list.append(item.contents[0])
    if isinstance(item, bs4.element.NavigableString):
      string_list.append(item)
  string_list = ' '.join(string_list)
  return string_list


def parse_selenium_text(whole_text):
  new_list = []
  lo = whole_text.splitlines()
  for item in lo:
    if re.search(r'(vulnerability|detection)', item):
      new_list.append(item)
  return new_list

def randomize_user_agent():
  user_agent_list = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
  ]

  for i in range(4):
    user_agent = random.choice(user_agent_list)
  
  headers = {'User-Agent': user_agent}
  return headers

class GCloudConnection:

    def __init__(self, URL, LOG_NAME):
        # env variable declared only for gcloud authentication during local tests. Not necessary at deployed instances
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './literaturereview-325215-dff8defafb5a.json'
        logging.getLogger().setLevel(logging.INFO)
        self.connect_cloud_services(LOG_NAME)
        self.URL = URL

    def connect_cloud_services(self, LOG_NAME):
            # connect gcloud logger to default logging.
            logging_client = gc_logging.Client()
            logging_client.get_default_handler()
            logging_client.setup_logging()
            logging_client.logger(LOG_NAME)

class Scraper:
    def __init__(self) -> None:
        self.init_url = 'https://scholar.google.com/scholar?q=Vulnerability+detection&hl=en&as_sdt=0%2C5&as_ylo=2010&as_yhi=2021'
        self.pager_number = 1
        self.scholar_pgsize = 0

    def googleScholarScraper(self, job):
        current_header = randomize_user_agent()
        llist = []
        job = 'https://scholar.google.com/scholar?' + urllib.parse.urlencode(job)
        content = requests.get(job, headers=current_header)

        page_soup = soup(content.text, "html.parser")

        paper_list = page_soup.contents[1].contents[1].contents[0].contents[13].contents[1].contents[2].contents[1]
        for item in paper_list.contents:
            if isinstance(item, bs4.element.Tag):
                if len(item.contents) > 1:
                    if len(item.contents[1].contents[0].contents) == 3:
                        for i, sub_item in enumerate(item.contents[1].contents[0].contents[2].contents):
                            if isinstance(sub_item, bs4.element.Tag):
                                item.contents[1].contents[0].contents[2].contents[i] = sub_item.contents[0]
                        _ttl = ' '.join(item.contents[1].contents[0].contents[2].contents)
                        print(_ttl)
                        llist.append([_ttl, item.contents[1].contents[1].contents[-1]])
                    else:
                        if len(item.contents[1].contents[0].contents[0].contents) == 1:
                            if isinstance(item.contents[1].contents[0].contents[0].contents[0], bs4.element.Tag):
                                llist.append(item.contents[1].contents[0].contents[0].contents[0].contents[0])
                                print(item.contents[1].contents[0].contents[0].contents[0].contents[0])
                            else:
                                llist.append(item.contents[1].contents[0].contents[0].contents[0])
                                print(item.contents[1].contents[0].contents[0].contents[0])
                        if len(item.contents[1].contents[0].contents[0].contents) > 1:
                            for i, sub_item in enumerate(item.contents[1].contents[0].contents[0].contents):
                                if isinstance(sub_item, bs4.element.Tag):
                                    item.contents[1].contents[0].contents[0].contents[i] = sub_item.contents[0]
                            _ttl = ' '.join(item.contents[1].contents[0].contents[0].contents)
                            print(_ttl)
                            llist.append([_ttl, item.contents[1].contents[1].contents[-1]])
              
        write_to_csv(llist, 'scholar')

        print('Analysis of page {} finished'.format(self.pager_number))
        print('Total number of papers extracted so far:', len(paper_list))
        self.pager_number += 1
        #self.scholar_pgsize += 10

        #self.init_url = 'https://scholar.google.com/scholar?start='+str(self.scholar_pgsize)+'&q=Vulnerability+detection&hl=en&as_sdt=0,5&as_ylo=2010&as_yhi=2021'
  
        #time.sleep((130-5)*np.random.random()+5)
        #self.googleScholarScraper()

if __name__ == '__main__':
    sc = Scraper()
    sc.googleScholarScraper()