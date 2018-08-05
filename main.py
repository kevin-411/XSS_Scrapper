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

def link_iterator(url, parameters):
    scan = Scanner()
    results_list = []
    global list_of_links
    list_of_links = scan.link_iterator(url)
    if not list_of_links:
        return False
    if url not in list_of_links:
        list_of_links.append(url)    
    get_links_list(list_of_links)
    print("links = ******************************************", list_of_links)
    for link in list_of_links:
        results = mainFunc(link, parameters)
        if "Error Occurred" in results:
            error_message = results[1]
            results = {}
            results['link'] = link
            results['xss_result'] = error_message
        results_list.append(results)    
    return results_list

def get_links_list(list_of_links):
    return list_of_links
    
def mainFunc(link, parameters):    
    scanx = Scanner(parameters)
    url = link
    results = {}
    check_validity_response = scanx.check_url(url)
    if "Error Occurred" in check_validity_response:
        return check_validity_response
    print("URL approved *****")
    scanned_earlier = scanx.check_if_scanned(url)
    if scanned_earlier:        
        negative_results = get_negative_scan_report(url)        
        try:
            positive_results = get_positive_scan_report(url)           
            results['xss_result'] = "Positive"
            results['link'] = [positive_results[2]]
            results['payload_used'] = [positive_results[3]]
            results['effect_of_payload'] = [positive_results[6]]
            results['script_location'] = [positive_results[5]]
            results['possible_entry_point'] = ['point x']
            results['remedy'] = [positive_results[7]]
        except :
            results['link'] = negative_results[1]
            results['xss_result'] = negative_results[2]        
        return results
    
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
            username_field = request.form['username_field']
            username = request.form['username']
        except:
            username_field = False
            username = False
            
        try:
            password_field = request.form['password_field']
            password = request.form['password']            
        except:
            password_field = False
            password = False
            
        try:
            scan_domain = request.form['domain_search']
            links = list_of_links
        except:
            scan_domain = False
            links = [link]

        if username_field and username and password_field and password:
            parameters = {username_field:username, password_field:password}
        else:
            parameters = None
        if not scan_domain:
            results = [mainFunc(link, parameters)]
            if "Error Occurred" in results[0]:
                return render_template('500.html', message = results[0][1]), 500
        else:
            results = link_iterator(link, parameters)
            if not results:
                results = [mainFunc(link, parameters)]
                if "Error Occurred" in results[0]:
                    return render_template('500.html', message = results[0][1]), 500
        print(results)
        return render_template('result.html', results=results, links=links, links_len=len(results))
            

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run( )


