"""
Analyzer
--
regex: String
js_code: String
code_blocks: String[]
xss_result: String
remedy: String
--
tokenize()
deobfuscate()
compare()
update_report()
--
Responsibilities
-- tokenize extracted javascript
-- establish whether code is obfuscated
-- check for similar entries in database
"""

class Analyzer:
    def __init__(self, js_code=['']):
        self.regex = ""
        self.js_code = js_code
        self.code_blocks = []
        self.xss_result = ""
        self.remedy = ""

    def tokenize(self):
        for code in self.js_code:
            self.code_blocks = code.split(";")
        for block in self.code_blocks:
            print("working on \n ", block)
            self.deobfuscate(block)

    def deobfuscate(self):
        pass

    def compare(self):
        pass

    def update_report(self):
        pass

    
    
        
