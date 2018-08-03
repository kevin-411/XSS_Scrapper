from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
from Model.model import *
import time
import re
import hashlib

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
        #print("attempting db connection")
        self.pages = []
        self.current_hash = ''
        self.initial_hash = ''

    #to generate a list of links available in a particular webpage
    def link_iterator(self, url):
        if not self.check_url(url):
            return False
        html = urlopen(url)
        bsObj = BeautifulSoup(html.read(), "html.parser")
        domain_name = url.split("//")[1].split("/")[0]
        links1 = bsObj.findAll("a", href=re.compile("^("+domain_name+")"))
        links2 = bsObj.findAll("a", href=re.compile("^[/.][a-zA-Z]"))
        try:
            links1[0].split()
            links_in_current_page = links1
        except:
            links_in_current_page = links2
        #print("current link: ",url)
        for link in links_in_current_page:
            if 'href' in link.attrs:
                try:
                    links1[0].split()
                    newPage = link.attrs['href']                    
                except:
                    newPage = url.split("//")[0]+"//"+domain_name+link.attrs['href']            
                if newPage not in self.pages: 
                    self.pages.append(newPage)
                    self.link_iterator(newPage)
        return self.pages
                
    #to retrieve the url to be scanned, checks if it is valid, and link is active
    def check_url(self, url):
        #we need to come up with a way of handling page redirects
        try:
            html = urlopen(url)
            self.url = url
        except HTTPError as e:
            #print(url, " 404, page not found")
            html = None
        except ValueError as e:
            #print(url, " invalid url")
            html = None            
        if html is None:
            #print(url, " page not found")
            self.url = ""
            return False
        else:
            #print("url approved, looking up db")
            page_hash = hashlib.sha224(html.read()).hexdigest()            
            self.current_hash = page_hash
            return self.url

    #checks if url has already been scanned, and if so, compares current_hash with previous hash
    def check_if_scanned(self, url):
        get_initial_hash(url)
        if not get_initial_hash(url):
            self.initial_hash = self.current_hash
        else:
            self.initial_hash = get_initial_hash(url)
        #print("Initial hash is now ", self.initial_hash)
        if get_url(url) and self.initial_hash == self.current_hash:
            #print("page not modified since last scan")
            #return True
            return False
        else:           
            #print("no recent scan found, beginning scraping")
            self.initial_hash = self.current_hash
            return False
            
    #scraps page pointed to by url
    def scrap_page(self, url):
        html = urlopen(url)
        bsObj = BeautifulSoup(html.read(), "html.parser")
        current_hash = self.current_hash
        scan_date = time.strftime("%d/%m/%Y %H:%M:%S %Z")               
        insert_scan(url, scan_date, current_hash, self.initial_hash)
        #print("scrapping complete, beginning js extraction")
        page_html = bsObj.prettify()
        return page_html

    #function moved from analyser component
    def deobfuscate(self,page_html):        
        #theres also superflous use of escape characters      
        #the deobfuscation should ideally be done multiple times
        #print("attempting preliminary deobfuscation")
        clean_block = ""
        html_code = page_html
        for code in html_code.split(" "):            
            unicode_escape_re = re.search(r'.*\\[U1X]\d+', code, re.I)
            html_encode_re = re.search('.*&#[x1]\d+', code, re.I)
            null_byte_re = re.search('.*\[%00\]', code, re.I)
            char_code_re = re.search('String.fromCharCode', code, re.I)
            if unicode_escape_re or html_encode_re or null_byte_re or char_code_re:
                self.obfuscated = True
                if not html_encode_re and not unicode_escape_re:                    
                    #print("unsuported obfuscation =>>", code)
                    code2 = code
                else:
                    print("found ==>", code)
                    if unicode_escape_re:
                        old_code = re.findall(r'.*\\[U1X]\d+', code, re.I)[0].split('\\')[1]
                        if old_code[0] is 'u' or old_code[0] is 'x':
                            old_code2 = old_code.replace('u', 'x')
                            new_code = chr(eval('0'+old_code2+'c'))
                        else:
                            new_code = old_code
                    elif html_encode_re:       
                        old_code = re.findall('&#[x1]\d+', code, re.I)[0].split("#")[1]
                        if x in old_code:
                            new_code = chr(eval('0'+old_code+'c'))
                        else:
                            new_code = chr(eval(old_code))                    
                    code2 = code.replace("\\"+old_code+"c", new_code)
                    #print(code, " transformed to ==> ", code2)
            else:
                code2 = code                
            clean_block = clean_block + code2.lower() + " "
        return clean_block 
        
    #extracts js from the HTML source
    def get_js(self, html):
        bsObj = BeautifulSoup(html, "html.parser")
        self.page_html = bsObj.prettify()
        self.scripts = []
        self.script = bsObj.findAll('script')
        #print("getting page js from page: \n")
        if self.script:
            #print("scripts include: ")
            for script in self.script:
                #print(script.get_text())
                self.scripts.append(script.get_text())
        tags = bsObj.findAll(lambda tag: len(tag.attrs) >0, recursive=False)
        attributes = ["onreadystatechange","onpropertychange","onbeforeactivate","onactivatein","onfocusin","onscroll","onmousemove","onmouseover", "onblur", "onload", "onerror","data","src","formaction"]
        #print("tags with attributes include: ")
        for tag in tags:
            for attribute in attributes:
                if attribute in str(tag):
                    try:
                        script = str(tag).split(attribute)[1].split(">")[0].split("=")[1].split(" ")[0]
                        self.scripts.append(script)
                        #print("Script is ", script)
                    except IndexError:
                        continue
        return self.scripts
      
