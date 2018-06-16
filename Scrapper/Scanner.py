from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
from Model.model import *
import time

#use this to generate random last_modifieds
import random

class Scanner:
    """
    Responsible for getting the URL from the user, along with other specifications user may specify. Will then check the date the page was last modified, and check if the page was processed before. It extracts javascript from the page
    """

        
    def __init__(self, scan_domain=False, username="", password="", last_modified="" ):
        self.url = ""
        self.last_modified = last_modified
        self.scan_domain = scan_domain
        self.username = username
        self.password = password
        print("attempting db connection")
                
    #to retrieve the url to be scanned, checks if it is valid, and link is active
    def get_url(self, url):
        #we need to come up with a way of handling page redirects
        try:
            html = urlopen(url)
            self.url = url
        except HTTPError as e:
            print(url, " 404, page not found")
            html = None
        except ValueError as e:
            print(url, " invalid url")
            html = None
            
        if html is None:
            print(url, " page not found")
            self.url = ""
            return False
        else:
            print("url approved, looking up db")
            self.check_if_scanned(self.url)
        

    #checks if url has already been scanned, and if so, compares scan date with last modification date
    def check_if_scanned(self, url):
        #come up with a function for last_modified
        last_modified = random.random() * 10000000000
        #if get_url(url):
         #   if last_modified > float(get_scan_date(url)):
          #      print("page not modified since last scan")
           #     print(get_report(url))
        #else:
         #   if url:
          #      print("no earlier scan found, beginning scraping")
           #     self.scrap_page(url)                
        print("no earlier scan found, beginning scraping")
        self.scrap_page(url)            

    #scraps page pointed to by url
    def scrap_page(self, url):
        #work yet to be done on the recussion of pages, should a whole domain be scanned
        html = urlopen(url)
        bsObj = BeautifulSoup(html.read(), "html.parser")
        last_modified = random.random() * 10000000000
        scan_date = time.time()
        insert_scan(url, scan_date, last_modified)
        print("scrapping complete, beginning js extraction")
        self.get_js(bsObj)
        
    #extracts js from the HTML source
    def get_js(self, bsObj):       
        self.page_html = bsObj.prettify()
        self.scripts = []
        self.script = bsObj.findAll('script')
        print("getting page js from page: \n")
        if self.script:
            print("scripts include: ")
            for script in self.script:
                print(script.get_text(), "\n")
                self.scripts.append(script.get_text())
        tags = bsObj.findAll(lambda tag: len(tag.attrs) >0, recursive=False)
        attributes = ["onmouseover", "onblur", "onload", "onerror"]
        print("tags with attributes include: ")
        for tag in tags:
            for attribute in attributes:
                if attribute in str(tag):
                    script = str(tag).split(attribute)[1].split(">")[0].split("=")[1].split(" ")[0]
                    self.scripts.append(script)
                    print("Script is ", script)
      
