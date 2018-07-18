#!/bin/python3

from Scrapper.Scanner import Scanner
from Analyser.Analyser import Analyser
from Reporter.Reporter import Reporter
from Model.model import *
import io 
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from flask_wtf import Form
from wtforms import *
from wtforms.validators import DataRequired

app = Flask(__name__)

#come up with way of calculating the progress across scans

list_of_links = ['']

def link_iterator(url):
    scan = Scanner()
    results_list = []
    global list_of_links
    list_of_links = scan.link_iterator(url)
    if url not in list_of_links:
        list_of_links.append(url)
    if not list_of_links:
        return False
    get_links_list(list_of_links)
    for link in list_of_links:
        results_list.append(mainFunc(link))
    return results_list

def get_links_list(list_of_links):
    return list_of_links
    
def mainFunc(link):    
    scanx = Scanner()
    url = link
    valid_url = scanx.check_url(url)
    if not valid_url:
        return False
    print("URL approved *****")
    scanned_earlier = scanx.check_if_scanned(url)
    if scanned_earlier:        
        results = get_negative_scan_report(url)
        results3 = {}
        try:
            results2 = get_positive_scan_report(url)
            results3['xss_result'] = "Positive"
            results3['link'] = [results2[2]]
            results3['payload_used'] = [results2[3]]
            results3['effect_of_payload'] = [results2[5]]
            results3['script_location'] = ['location x']
            results3['possible_entry_point'] = ['point x']
            results3['remedy'] = [results2[6]]
        except :
            results2 = None
        print("Results  = ", results , " Results2 = ", results2, " Results3 = ", results3)
        return results3 if results2 is not None else results
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
    print("code deobfuscation completed ***** ")
    analysis_x.compare(clean_blocks)
    print("code comparison completed *****")
    results_ = analysis_x.update_report()
    print("report updating complete *****")
    report = Reporter(url, scripts)
    results = report.get_results()
    
    return results_
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/link', methods = ['GET', 'POST'])
def link():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        link = request.form['url']
        try:
            scan_domain = request.form['domain_search']
            links = list_of_links
            print("links = ", links)
        except:
            scan_domain = False
            links = [link]
        if not scan_domain:
            results = [mainFunc(link)]
        else:
            results = link_iterator(link)
        if results is False:
            return render_template('500.html'), 500
        return render_template('result.html', results=results, links=links, links_len=len(links))
            

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run( )


