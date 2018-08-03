#!/bin/python3

from Scrapper.Scanner import Scanner
from Analyser.Analyser import Analyser
from Reporter.Reporter import Reporter
from Model.model import *
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug import secure_filename
from flask_wtf import Form
from wtforms import *
from wtforms.validators import DataRequired
import _thread

app = Flask(__name__)

#come up with way of calculating the progress across scans
#since we have a general idea of what functions run for how long, we'll update the progress bar to change automatically, but give it an upper limit depending on the section of code that is being executed at the moment

list_of_links = ['']
timeCheckValidUrl = 0
timeCheckIfScanned = 0
timePageScrap = 0
timeDeobfuscate = 0
timeGetJS = 0
timeTokenize = 0
timeDeobfuscate2 = 0
timeCompare = 0
timeUpdateResult = 0
endMainFunc = 0
MainFuncResults = ''
link_iterator_results = ''
current_link_index = 0

def link_iterator(url):
    scan = Scanner()
    results_list = []
    global list_of_links, current_link_index
    list_of_links = scan.link_iterator(url)
    if url not in list_of_links:
        list_of_links.append(url)
    if not list_of_links:
        return False
    get_links_list(list_of_links)
    #print("links = ******************************************", list_of_links)
    for link in list_of_links:
        results_list.append(mainFunc(link))
        current_link_index = list_of_links.index(link) + 1
    global link_iterator_results
    link_iterator_results = results_list
    return results_list

def get_links_list(list_of_links):
    return list_of_links

def mainFunc(link):
    global timeCheckValidUrl, timeCheckIfScanned, timePageScrap, timeDeobfuscate, timeGetJS, timeTokenize, timeDeobfuscate2, timeCompare, timeUpdateResult, endMainFunc, MainFuncResults
    timeCheckValidUrl = 0
    timeCheckIfScanned = 0
    timePageScrap = 0
    timeDeobfuscate = 0
    timeGetJS = 0
    timeTokenize = 0
    timeDeobfuscate2 = 0
    timeCompare = 0
    timeUpdateResult = 0
    endMainFunc = 0
    startMainFunc = time.clock()
    scanx = Scanner()    
    url = link
    valid_url = scanx.check_url(url)
    endCheckValidUrl = time.clock()
    timeCheckValidUrl = endCheckValidUrl - startMainFunc
    if not valid_url:
        return False
    #print("URL approved *****")
    scanned_earlier = scanx.check_if_scanned(url)
    endCheckIfScanned = time.clock()
    timeCheckIfScanned = endCheckIfScanned - endCheckValidUrl
    if scanned_earlier:        
        results = get_negative_scan_report(url)
        results3 = {}
        try:
            results2 = get_positive_scan_report(url)
            results3['xss_result'] = "Positive"
            results3['link'] = [results2[2]]
            results3['payload_used'] = [results2[3]]
            results3['effect_of_payload'] = [results2[6]]
            results3['script_location'] = [results2[5]]
            results3['possible_entry_point'] = ['point x']
            results3['remedy'] = [results2[7]]
        except :
            results2 = None
        #print("Results  = ", results , " Results2 = ", results2, " Results3 = ", results3)
        return results3 if results2 is not None else results
    #print("url scan check complete *****")
    html = scanx.scrap_page(url)
    endPageScrap = time.clock()
    timePageScrap = endPageScrap - endCheckIfScanned
    #print("page scrap complete *****")
    clean_block = scanx.deobfuscate(html)
    endDeobfuscate = time.clock()
    timeDeobfuscate = endDeobfuscate - endPageScrap
    #print("deobfuscation1 \n")
    scripts = scanx.get_js(clean_block)
    endGetJS = time.clock()
    timeGetJS = endGetJS - endDeobfuscate
    #print("js code extracted *****")
    analysis_x = Analyser(url, scripts)   
    #print("Analyser component initialised *****")
    code_tokens = analysis_x.tokenize()
    endTokenize = time.clock()
    timeTokenize = endTokenize - endGetJS
    #print("code tokenization completed \n*****")
    clean_blocks = analysis_x.deobfuscate(code_tokens)
    endDeobfuscate2 = time.clock()
    timeDeobfuscate2 = endDeobfuscate2 - endTokenize
    #print("code deobfuscation completed ***** ")
    analysis_x.compare(clean_blocks)
    endCompare = time.clock()
    timeCompare = endCompare - endDeobfuscate2
    #print("code comparison completed *****")
    results_ = analysis_x.update_report()
    endUpdateReport = time.clock()
    timeUpdateResult = endUpdateReport - endCompare
    endMainFunc = time.clock() - startMainFunc
    #print("report updating complete *****")
    report = Reporter(url, scripts)
    results = report.get_results() 
    #print("checkValidUrl function => ",timeCheckValidUrl, " => ", (timeCheckValidUrl/endMainFunc) * 100)
    #print("CheckIfScanned function => ",timeCheckIfScanned, " => ", (timeCheckIfScanned/endMainFunc) * 100)
    #print("PageScrap function => ",timePageScrap, " => ", (timePageScrap/endMainFunc) * 100)
    #print("Deobfuscation function => ",timeDeobfuscate, " => ", (timeDeobfuscate/endMainFunc) * 100)
    #print("GetJS function => ",timeGetJS, " => ", (timeGetJS/endMainFunc) * 100)
    #print("Tokenize function => ",timeTokenize, " => ", (timeTokenize/endMainFunc) * 100)
    #print("Deobfuscate2 function => ",timeDeobfuscate2, " => ", (timeDeobfuscate2/endMainFunc) * 100)
    #print("Compare function => ",timeCompare, " => ", (timeCompare/endMainFunc) * 100)
    #print("UpdateReport function => ",timeUpdateResult, " => ", (timeUpdateResult/endMainFunc) * 100)
    print("Main function => ",endMainFunc, " => ", (endMainFunc/endMainFunc) * 100)
    #return results_    
    MainFuncResults = results_
    return results_
    
@app.route('/')
def index():    
    return render_template('index.html')

def progress_status(arg):
    #return jsonify(timeCheckValidUrl, timeCheckIfScanned, timePageScrap, timeDeobfuscate, timeGetJS, timeTokenize, timeDeobfuscate2, timeCompare, timeUpdateResult, endMainFunc)
    print("Thread succesfully spawned?")
    return "really long text message"

@app.route('/ajax')
def ajax():
    return jsonify(len(list_of_links), current_link_index, timeCheckValidUrl, timeCheckIfScanned, timePageScrap, timeDeobfuscate, timeGetJS, timeTokenize, timeDeobfuscate2, timeCompare, timeUpdateResult, endMainFunc)
    
    #return get_status()

#@celery.task
#def get_status():
 #   return jsonify(timeCheckValidUrl, timeCheckIfScanned, timePageScrap, timeDeobfuscate, timeGetJS, timeTokenize, timeDeobfuscate2, timeCompare, timeUpdateResult, endMainFunc)

@app.route('/link', methods = ['GET', 'POST'])
def link():
    global MainFuncResults, link_iterator_results
    MainFuncResults = ''
    link_iterator_results = ''
    if request.method == 'GET':
        return render_template('index.html')
    else:
        print("processing form output")
        link = request.form['url']
        try:
            scan_domain = request.form['domain_search']
            links = list_of_links
            #print("links = ******************************************", links)
        except:
            scan_domain = False
            links = [link]
        if not scan_domain:
            #_thread.start_new_thread(mainFunc, (link,))
            #while MainFuncResults == '':
                #pass
            results = [mainFunc(link)]
            #results = MainFuncResults
        else:
            #_thread.start_new_thread(link_iterator, (link,))
            
            #while link_iterator_results == '':
                #pass            
            results = link_iterator(link)
            #results = link_iterator_results
        if results is False:
            return render_template('500.html'), 500
        #print("results is ===================>>>>>>>>> ", results)
        print(timeCheckValidUrl, timeCheckIfScanned, timePageScrap, timeDeobfuscate, timeGetJS, timeTokenize, timeDeobfuscate2, timeCompare, timeUpdateResult, endMainFunc)
        return render_template('result.html', results=results, links=links, links_len=len(results))
            

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run( threaded=True)

#app.run()
