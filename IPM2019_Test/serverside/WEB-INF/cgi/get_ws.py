#######################################################################
#Application : LAPAM
#Build : v3
#Desc: Get the TestName form DB for dropdown
#Created by : Rajkumar
#Date of Modification:8/9/2018
########################################################################

import cgi, cgitb,sys
import cgitb; cgitb.enable()
import pyodbc
import configparser

from elasticsearch import Elasticsearch
import elasticsearch.helpers

parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

form = cgi.FieldStorage()
user_id = form.getvalue("user_id")
build1 = form.getvalue("build1")
build2 = form.getvalue("build2")
##user_id="42"
##build1="STAD_18Jun"
##build2="STAD_19_Jun"
build1 = user_id + "_" + build1.lower()
build2 = user_id + "_" + build2.lower()

def get_ws(build1, build2):
    es = Elasticsearch('localhost', port=9200)

##    res1 = es.search(index='sap_stad', body={"size":0,"query":{"bool":{"must":[{"match":{"LOG_NAME.keyword":build1}}]}}})
##    res2 = es.search(index='sap_stad', body={"size":0,"query":{"bool":{"must":[{"match":{"LOG_NAME.keyword":build2}}]}}})
    
    res1 = es.search(index='sap_stad', body={ "size": 0,"query": {"bool": {"must": [{"match":{"LOG_NAME.keyword":build1}}]}},"aggs": {"uniqtcode" : {"terms": {"field" : "TRANSACTION_OR_JOBNAME.keyword","size": 10000}}}})
    res2 = es.search(index='sap_stad', body={ "size": 0,"query": {"bool": {"must": [{"match":{"LOG_NAME.keyword":build2}}]}},"aggs": {"uniqtcode" : {"terms": {"field" : "TRANSACTION_OR_JOBNAME.keyword","size": 10000}}}})

    stad_tcode=[]
##    print(res1)
    for val in res1['aggregations']['uniqtcode']['buckets']:        
        stad_tcode.append(val['key'])

    for val in res2['aggregations']['uniqtcode']['buckets']:
        stad_tcode.append(val['key'])

    res = es.search(index='sap_workstream', body={"size":10000, "query": {"match_all": {}}})

    tcode2ws_dict={}

    for val in res['hits']['hits']:
        ws=val['_source']['Workstream']
        tcode=val['_source']['Tcode']
        tcode2ws_dict[tcode]=ws

##    tcode2ws_dict={"T1":"W1", "T2":"W2", "T3":"W3"}
##    stad_tcode=["T1", "T2"]
    
    ws_list=set()

    for val in stad_tcode:
        if val in tcode2ws_dict:
                ws_list.add(tcode2ws_dict[val])

    return ws_list



ws_list=get_ws(build1, build2)
print ("Content-type: text/html \n\n");
print(str(ws_list))
#print("[W1, W2, W3, W4]")

	
	
