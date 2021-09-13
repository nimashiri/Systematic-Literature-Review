import logging, pexpect
from web_scraper import write_to_csv
import random
import requests
from urllib.parse import urlencode
import os, time, pandas as pd
from utils import GCloudConnection
import csv

def saveCSV(data):
    with open("scholar_jobs.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(data)


class Master(GCloudConnection):

    def __init__(self, URL):
        GCloudConnection.__init__(self, URL, LOG_NAME= "master-scraper")
        self.pending_jobs = []
        self.current_job = None
        self.is_restarting = False

    def restart_machine(self):
        # execute these commands locally to manually re deploy instance
        try:
            logging.info("Re-deploying instance")
            deploy = pexpect.spawn('gcloud app deploy orchestra.yaml --version v1')
            deploy.expect('Do you want to continue (Y/n)?')
            deploy.sendline('Y')
            deploy.expect("Deployed service", timeout=100)
            self.is_restarting = True
        except  Exception as  e:
            self.is_restarting = False
            logging.error(f"Problem re-deploying: {e}")

    def start(self):
        try:
            requests.get(f"{self.URL}/start", timeout=3)
        except Exception:
            logging.error("Slave not running")

    def check_slave_state(self):
        try:
            response = requests.get(f"{self.URL}/state", timeout=10)
            state = response.content.decode("utf-8")
        except Exception:
            state = "no-answer"
        return state

    def send_job(self, job):
        url = self.URL + "/job?" + urlencode(job)
        requests.get(url, timeout=10)
        logging.info(f"Sending job = {job} to {url}")

    def orchestrate(self):
        while(len(self.pending_jobs) > 0):
            state = self.check_slave_state()
            logging.info(f"Current state of slave: {state}")
            next_job_ready = False # wont change if state == "busy" or "no-answer"
            if state == "not-started":
                self.start()
            if state == "scraping-detected" and self.is_restarting == False:  # Error 429 in slave.
                self.pending_jobs.insert(0, self.current_job)
                self.restart_machine()
            elif state == "idle":
                next_job_ready = True
            if next_job_ready:
                self.current_job = self.pending_jobs.pop(0)
                self.send_job(self.current_job)
            time.sleep(3)

    def create_jobs(self):
        self.pending_jobs.append('https://scholar.google.com/scholar?q=Vulnerability+detection&hl=en&as_sdt=0%2C5&as_ylo=2010&as_yhi=2021')
        for i in range(10, 1000, 10):
            url = 'https://scholar.google.com/scholar?start='+str(i)+'&q=Vulnerability+detection&hl=en&as_sdt=0,5&as_ylo=2010&as_yhi=2021'
            self.pending_jobs.append(url)

    def make_jobs_readable(self):
        data = []
        data.append(['q', 'start', 'hl', 'as_sdt', 'as_ylo', 'as_yhi'])
        j = 0
        for i in range(10, 1000, 10):
            data.append([j,'Vulnerability detection',i, 'en', '0,5', '2010', '2021' ])
            j += 1
        saveCSV(data)


    def import_jobs(self):
        df_jobs = pd.read_csv("./scholar_jobs.csv", index_col = 0)
        self.pending_jobs = list(df_jobs.to_dict("index").values())


if __name__ == "__main__":
    url = os.getenv("URL")
    if url is None:
        url = "http://0.0.0.0:8080" #local mode
    master = Master(url)
    master.import_jobs()
    #master.create_jobs()
    #master.make_jobs_readable()
    master.orchestrate()