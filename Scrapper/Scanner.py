from bs4 import BeautifulSoup
import requests, time, re, hashlib
from Model.model import *

class Scanner:
    """
    Responsible for getting the URL from the user, along with other specifications user may specify. Will then check the date the page was last modified, and check if the page was processed before. It extracts javascript from the page
    """

    
       
    def __init__(self, parameters=None):
        self.url = ""
        self.parameters = parameters
        self.pages = []
        self.current_hash = ''
        self.initial_hash = ''
        self.html = None
        self.error_message = ''

    def link_iterator(self, url):        
        if "Error Occurred" in self.check_url(url):
            return False
        bsObj = BeautifulSoup(self.html, "html.parser")
        domain_name = url.split("//")[1].split("/")[0]
        links1 = bsObj.findAll("a", href=re.compile("^("+domain_name+")"))
        links2 = bsObj.findAll("a", href=re.compile("^[/.][a-zA-Z]"))
        try:
            links1[0].split()
            links_in_current_page = links1
        except:
            links_in_current_page = links2
        print("current link: ",url)
        for link in links_in_current_page:
            if 'href' in link.attrs:
                try:
                    links1[0].split()
                    newPage = link.attrs['href']                    
                except:
                    newPage = url.split("//")[0]+"//"+domain_name+link.attrs['href']
            
                if newPage not in self.pages:                   
                    print(newPage)
                    self.pages.append(newPage)
                    self.link_iterator(newPage)
        return self.pages
                
    #to retrieve the url to be scanned, checks if it is valid, and link is active

    def get_html(self, url):
        try:
            session = requests.Session()
            headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36 (KHTML, like Gecko) Chrome","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
            #html = session.get(url, timeout=7)
            if self.parameters:
                html = session.post(url, self.parameters)              
            else:
                html = session.get(url, timeout=7)
            self.html = html.content
            html.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            self.error_message = "Connection Error"
            self.html = None
        except requests.exceptions.HTTPError as e:
            self.error_message =  "Page not Found"
            self.html = None
        except requests.exceptions.Timeout as e:
            self.error_message = "Request Timeout"
            self.html = None
        except requests.exceptions.TooManyRedirects as e:
            self.error_message = "Too many Redirects"
            self.html = None
    
        return self.html
        
    def check_url(self, url):
        #we need to come up with a way of handling page redirects        
        if self.get_html(url) is None:
            self.url = ""
            return ["Error Occurred", self.error_message]
        else:            
            self.url = url
            print("url approved, looking up db")
            html = self.html
            page_hash = hashlib.sha224(html).hexdigest()            
            self.current_hash = page_hash
            return "Success, Url Valid"

    #checks if url has already been scanned, and if so, compares scan date with last modification date
    def check_if_scanned(self, url):
        #to do the whole last_modified thing, we could get away with calculating the page's hash during an initial scan, then comparing this against subsequent scans to check against any modifications in the page
        print("Initial hash is  ====>", get_initial_hash(url))
        print("Current hash is ", self.current_hash)
        #last_modified = time.strptime(self.last_modified, "%d/%m/%Y %H:%M:%S %Z")
        current_hash = self.current_hash
        get_initial_hash(url)
        if not get_initial_hash(url):
            self.initial_hash = current_hash
        else:
            self.initial_hash = get_initial_hash(url)
        print("Initial hash is now ", self.initial_hash)
        if get_url(url) and self.initial_hash == current_hash:
            print("page not modified since last scan")
           # print(get_report(url))
            return True
        else:           
            print("no recent scan found, beginning scraping")
            self.initial_hash = current_hash
            return False
            

    #scraps page pointed to by url
    def scrap_page(self, url):
        bsObj = BeautifulSoup(self.html, "html.parser")
        #last_modified = self.last_modified
        #current_hash = hashlib.sha224(html.read()).hexdigest()
        current_hash = self.current_hash
        print("current hash is ==============>", current_hash)
        print("previous hash is ===============>", self.initial_hash)
        
        scan_date = time.strftime("%d/%m/%Y %H:%M:%S %Z")               
        insert_scan(url, scan_date, current_hash, self.initial_hash)
        print("scrapping complete, beginning js extraction")
        page_html = bsObj.prettify()
        return page_html

    #function moved from analyser component
    def deobfuscate(self,page_html):        
        #theres also superflous use of escape characters
      
        #the deobfuscation should ideally be done multiple times
        print("attempting preliminary deobfuscation")
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
                    print("unsuported obfuscation =>>", code)
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
                    print(code, " transformed to ==> ", code2)

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
        print("getting page js from page: \n")
        if self.script:
            print("scripts include: ")
            for script in self.script:
                print(script.get_text())
                self.scripts.append(script.get_text())
        tags = bsObj.findAll(lambda tag: len(tag.attrs) >0, recursive=False)
        attributes = ["onreadystatechange","onpropertychange","onbeforeactivate","onactivatein","onfocusin","onscroll","onmousemove","onmouseover", "onblur", "onload", "onerror","data","src","formaction"]
        print("tags with attributes include: ")
        for tag in tags:
            for attribute in attributes:
                if attribute in str(tag):
                    try:
                        script = str(tag).split(attribute)[1].split(">")[0].split("=")[1].split(" ")[0]
                        self.scripts.append(script)
                        print("Script is ", script)
                    except IndexError:
                        continue
                    
        return self.scripts
      
