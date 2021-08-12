import os,openpyxl,re,pyodbc,shutil,sys
import cgi, cgitb
from pprint import pprint
from collections import Counter
import configparser
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import datetime
from itertools import groupby
from operator import itemgetter
from SAPTcodeUsageAnalysis import ws_process

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
##STAD_INDEX_NAME = parser.get('Upload','STAD_INDEX_NAME')
STAD_INDEX_NAME = "sap_stad"

def process(test_name,prjid,userid):
    Log_Name = str(userid) + "_"+str(prjid)+"_"+test_name
    Index_Name = str(userid) + "_"+test_name
    es = Elasticsearch('localhost', port=9200)
    dir_path = "../../../WEB-INF/classes/static/html/Reports/"+Log_Name
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    #fetch distinct tcode value from stad 
    res=es.search(index=STAD_INDEX_NAME,body={ "size": 0, "query": {"match":{"LOG_NAME.keyword":Index_Name}}, "aggs" : {"uniqsc1" : {"terms" : { "field" : "TRANSACTION_OR_JOBNAME.keyword","size": 10000}}}})
    agg_val=res['aggregations']['uniqsc1']['buckets']
    stad_tcode_arr = []
    tcode_arr = []
    ws_tcode_dict={}
    pattern = r'[^=<>(){}\\/!]'
    for doc in agg_val:
        match = re.match(pattern,doc['key'])
        if  match and ("=" not in doc['key']):
            tcode_arr.append(doc['key'])
    #get workstream value from elasticsearch
    res_ws = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["Tcode","Workstream"]}, 
                index = "sap_workstream")
    workstream_lst = []
    for doc in res_ws:
        ws_tcode_dict[doc['_source']['Tcode']]= doc['_source']['Workstream']
    for tcode_val in tcode_arr:
        if tcode_val.strip() in ws_tcode_dict.keys():
            value = [ws_tcode_dict[tcode_val], tcode_val.strip()]
            value = tuple(value)
            workstream_lst.append(value)
    #print(workstream_lst)
    sorted_ws = sorted(workstream_lst, key=itemgetter(0))
    TopWorkstream=[]
    #groups = groupby(workstream_lst,lambda i:(i[0]))
    for key, group in groupby(sorted_ws, lambda x: x[0]):
        listOfThings = [thing[1] for thing in group]
        if listOfThings is not None:
            tcodeVal = [key, len(listOfThings)]
            tcodeVal = tuple(tcodeVal)
            TopWorkstream.append(tcodeVal)
            TopWorkstream = sorted(TopWorkstream, key=itemgetter(0))
    write_csv(TopWorkstream, Log_Name,test_name,prjid,userid)

#function to write csv file 
def write_csv(usage,Log_Name,test_name,prjid,userid):
    #usage = [list(i) for i in usage]
    usage = sorted(usage, key=lambda x: x[1], reverse=True)
    usage = usage[:10]
    print(usage)
    filename = "All Workstreams.csv"
    usagefile = open(filename,"w")
    usagefile.write("WorkStream,Unique Tcode Count\n")
    for i in usage:
        print(i[0], i[1])
        usagefile.write(i[0]+","+str(i[1])+"\n")
        ws_process(test_name,prjid,userid,i[0])
    usagefile.close()
    shutil.move(filename, "../../../WEB-INF/classes/static/html/Reports/"+Log_Name+"/"+filename)

if __name__ == "__main__":
    print("Content-type: text/html \n")
    form = cgi.FieldStorage()
##    userid = sys.argv[1].strip()
##    prjid = sys.argv[2].strip()
##    test_name = sys.argv[3]
    test_name = "STAD_2707"
    prjid = "831"
    userid = "42"
    test_name = test_name.lower()
    print("Start process - " + str(datetime.datetime.now()))
    process(test_name,prjid,userid)
##    print("endprocess - " + str(datetime.datetime.now()))
