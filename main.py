#!/bin/python3

from Scrapper.Scanner import Scanner
from Analyser.Analyser import Analyser

scanx = Scanner()
url = input("Kindly enter url to scan:\n")

scanx.get_url(url)

print("URL scan complete, ur approved *****")

scanx.check_if_scanned(url)

print("url scan check complete *****")

html = scanx.scrap_page(url)

print("page scrap complete *****")

clean_block = scanx.deobfuscate(html)

print("deobfuscation1 \n")

scripts = scanx.get_js(clean_block)

print("js code extracted *****")

analysis_x = Analyser(url, scripts)

print("Analyser component initialised *****")

code_tokens = analysis_x.tokenize()

print("code tokenization completed \n*****")

clean_blocks = analysis_x.deobfuscate(code_tokens)

print("code deobfuscation completed *****")

analysis_x.compare(clean_blocks)
print("code comparison completed *****")

analysis_x.update_report()
print("report updating complete *****")
