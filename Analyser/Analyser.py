import re
from Model.model import *
import time

class Analyser:
    def __init__(self, url, js_code=['']):
        self.regex = ""
        self.js_code = js_code
        self.code_blocks = []
        self.tokens = []
        self.xss_result = ""
        self.remedy = ""
        self.obfuscated = ""
        self.xss_payload_regexes = get_payloads()
        self.discovered_xss = []
        self.url = url

    def tokenize(self):
        #need to take care of the optional semicolon present during htmlencoding
        #for code in self.js_code:
         #   code = str(code)
          #  self.code_blocks.append(code.split(";"))
        for block in self.js_code:
            block = str(block)
            self.tokens.append(block.split(" "))
        return self.tokens            
       
    def deobfuscate(self,tokens):
        #for now we'll have to work with only html_encoded strings, for simplicity
        #theres also superflous use of escape characters
        
        #when the agent has been positively identified, deobfuscation will be attempted using the agent's technique in reverse
        #the deobfuscation should ideally be done multiple times
        #once the obfuscation technique has been identified, the string in question is substituted as appropriate in the code block
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
                    print("unsuported obfuscation")
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
                        old_code = re.findall('&#[x1]\d+', code)[0].split("#")[1]
                        if x in old_code:
                            new_code = chr(eval('0'+old_code+'c'))
                        else:
                            new_code = chr(eval(old_code))
                    for block in self.code_blocks:
                        new_block = str(block).replace("\\"+old_code+"c", new_code)
                        clean_blocks.append(new_block)

        if not self.obfuscated: clean_blocks = self.code_blocks 
        return clean_blocks 
        
    def compare(self, clean_blocks):
        #function looks up database for similar entries on js payloads
        #the db should thus already be populated with some payload samples
        #how to establish the entry point of an xss payload?
        #how to craft the remedy, sucha as to tell the developer/admin which lines should be escaped/looked at keenly
        url = self.url
        for js_code in clean_blocks:            
            for xss_payload_regex in self.xss_payload_regexes:
                if re.search(xss_payload_regex, js_code, re.I):
                    code_index = self.clean_blocks.index(js_code)
                    self.discovered_xss.append(self.code_blocks[code_index])
                    string = re.findAll(xss_payload_regex, js_code)
                    effect_of_js = get_effect_of_js(xss_payload_regex)
                    remedy = "Enter line number of problematic code"
                    insert_positive_scan(get_scan_id(self.url), self.url, string, js_code, effect_of_js, remedy)
                    return "Positive"
                else:
                    return "Negative"
                    
                    
    def update_report(self):
        #this function is supposed to populate 2 tables;
        #i) is the scan_report, where a result will be either positive or negative
        #ii) is the positive_scan, where details on a positive scan will be entered
        if self.discovered_xss:
            insert_scan_report(self.url,"Positive", time.strftime("%H:%M:%S %d/%m/%Y"))
           
        else:
            insert_scan_report(self.url, "Negative", time.strftime("%H:%M:%S %d/%m/%Y"))
        pass

    
    
        
