import re
from Model.model import *
from urllib.request import urlopen
import time

class Analyser:

    """
responsible for breaking up the extracted javascript into tokens,
for easier comparison against the databas
"""
    
    def __init__(self, url, js_code=['']):
        self.regex = ""
        self.js_code = js_code
        self.code_blocks = []
        self.tokens = []
        self.effect_of_js = []
        self.remedy = []
        self.obfuscated = ""
        self.xss_payload_regexes = get_payloads()
        self.discovered_xss = []
        self.url = url
        self.code_index = []

    #breaks jsvascript code into tokens, then compares against database
    def tokenize(self):
        for block in self.js_code:
            block = str(block).strip()
            self.tokens.append(block.split(" "))
        return self.tokens            

    #performs further deobfuscation against the tokens
    def deobfuscate(self,tokens):
        #theres also superflous use of escape characters
        clean_blocks = []
        for code in tokens:
            code = str(code)
            unicode_escape_re = re.search(r'.*\\[U1X]\d+', code, re.I)
            html_encode_re = re.search('.*&#[x1]\d+', code, re.I)
            null_byte_re = re.search('.*\[%00\]', code, re.I)
            char_code_re = re.search('String.fromCharCode', code, re.I)
            if unicode_escape_re or html_encode_re or null_byte_re or char_code_re:
                self.obfuscated = True
                if not html_encode_re and not unicode_escape_re:
                    #print("unsuported obfuscation")
                    pass
                else:
                    #print("found ==>", code)
                    if unicode_escape_re:
                        old_code = re.findall(r'.*\\[U1X]\d+', code, re.I)[0].split('\\')[1]
                        if old_code[0] is 'u' or old_code[0] is 'x':
                            old_code2 = old_code.replace('u', 'x')
                            new_code = chr(eval('0'+old_code2+'c'))
                        else:
                            new_code = old_code
                    elif html_encode_re:                        
                        old_code = re.findall('&#[x1]\d+', code)[0].split("#")[1]
                        if x in old_code:
                            new_code = chr(eval('0'+old_code+'c'))
                        else:
                            new_code = chr(eval(old_code))
                    for block in self.code_blocks:
                        new_block = str(block).replace("\\"+old_code+"c", new_code)
                        clean_blocks.append(new_block)
        if not self.obfuscated: clean_blocks = self.tokens
        return clean_blocks 

    #compares javascript code tokens against the xss payloads in the database
    def compare(self, clean_blocks):
        #how to establish the entry point of an xss payload?
        url = self.url
        #print(clean_blocks)
        for js_code in clean_blocks:
            for js_code2 in js_code:
                js_code2 = str(js_code2).strip()
                if js_code2 == "":
                    continue 
                #print("clean js_code: ", js_code2)
                for xss_payload_regex in self.xss_payload_regexes:
                    xss_payload_regex = str(xss_payload_regex[0])
                    if re.search(xss_payload_regex, js_code2, re.I):
                        code = re.findall(xss_payload_regex, js_code2, re.I)[0]
                        try:
                            try:
                                code_index = clean_blocks.index(code)
                            except ValueError:
                                code_index = clean_blocks.index(eval("['"+code+"']"))
                        except:
                            continue                            
                        self.code_index.append(self.get_script_location(url,code))
                        current_code_index = self.get_script_location(url,code)
                        string = re.findall(xss_payload_regex, js_code2)[0]
                        effect_of_js = get_effect_of_js(xss_payload_regex)
                        remedy = "Enter line number of problematic code"
                        self.discovered_xss.append(self.tokens[code_index])
                        self.effect_of_js.append(effect_of_js)
                        self.remedy.append(remedy)
                        insert_positive_scan(get_scan_id(self.url), self.url, string, code, current_code_index, effect_of_js, remedy)
                    else:
                        continue

    #gets the particular line in which an identified string is in memory
    def get_script_location(self, url, script):
        html = urlopen(url).read().decode(encoding='utf-8')
        html_code_list = html.split("\n")
        for html_line in html_code_list:
            if re.search(re.escape(script), html_line, re.I):                
                code_index = html_code_list.index(html_line)
                #print("Found ", script, " at ", code_index)
                return code_index +1
        
                  
    def update_report(self):
        link = self.url
        payload_used = self.discovered_xss
        effect_of_payload = self.effect_of_js
        script_location = self.code_index
        possible_entry_point = ["point x"]
        remedy = self.remedy
        time_value = time.strftime("%d/%m/%Y %H:%M:%S %Z")
        #print("payload_used ===>>> ", payload_used)
        if self.discovered_xss:
            xss_result = "Positive"
            insert_scan_report(link,xss_result,time_value)
            results = {'link': self.url, 'xss_result': xss_result, 'payload_used': payload_used, 'effect_of_payload': effect_of_payload, 'script_location': script_location, 'possible_entry_point': possible_entry_point, 'remedy': remedy}
        else:
            xss_result = "Negative"
            insert_scan_report(link, xss_result, time_value)
            results = {'link': link, 'xss_result': xss_result}
        return results

    
    
        
