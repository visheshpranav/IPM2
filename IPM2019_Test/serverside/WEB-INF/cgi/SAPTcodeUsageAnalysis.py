import os,openpyxl,re,pyodbc,shutil
import cgi, cgitb
from pprint import pprint
from collections import Counter
import configparser
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import datetime
from itertools import groupby
from operator import itemgetter

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
##STAD_INDEX_NAME = parser.get('Upload','STAD_INDEX_NAME')
STAD_INDEX_NAME = "sap_stad"

def ws_process(test_name,prjid,userid, workstream):
    Log_Name = str(userid) + "_"+str(prjid)+"_"+test_name
    Index_Name = str(userid)+"_"+test_name
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
    for doc in agg_val:
        value = [doc['key'], doc['doc_count']]
        value = tuple(value)
        tcode_arr.append(value)
        
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
        #print(tcode_val[0].strip())
        if tcode_val[0].strip() in ws_tcode_dict.keys():
            value = [ws_tcode_dict[tcode_val[0]], tcode_val[0].strip(), str(tcode_val[1])]
            value = tuple(value)
            workstream_lst.append(value)
##    print(workstream_lst)
    sorted_ws = sorted(workstream_lst, key=itemgetter(0))
    #print(sorted_ws)
    TopWorkstream=[]
    #groups = groupby(workstream_lst,lambda i:(i[0]))
    for key, group in groupby(sorted_ws, lambda x: x[0]):
        if key == workstream:
            for thing in group:
                if thing is not None:
                    tcodeVal = [thing[1], thing[2]]
                    tcodeVal = tuple(tcodeVal)            
                    TopWorkstream.append(tcodeVal)
    TopWorkstream_val = sorted(TopWorkstream, key=itemgetter(0))
    print(TopWorkstream_val)

    write_csv(TopWorkstream, Log_Name, workstream)

#function to write csv file 
def write_csv(usage,Log_Name, workstream):
    #usage = [list(i) for i in usage]
    #usage = sorted(usage, key=lambda x: x[1], reverse=True)
    usage = usage[:10]
    print(usage)
    filename = workstream.replace('/','_').replace('\\x96','')+".csv"
    usagefile = open(filename,"w")
    usagefile.write("Tcode,Transaction Count\n")
    for i in usage:
        usagefile.write(i[0]+","+str(i[1])+"\n")
    usagefile.close()
    shutil.move(filename, "../../../WEB-INF/classes/static/html/Reports/"+Log_Name+"/"+filename)

def removechar(workstream, from_start=0, from_end=0):
    return workstream[from_start:len(workstream) - from_end]


if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    test_name = form.getvalue('Txt_testname').strip()
    prjid = form.getvalue('prjid').strip()
    userid = form.getvalue('userid').strip()
    workstream = form.getvalue('workstream').strip()
    userid = sys.argv[1].strip()
    prjid = sys.argv[2].strip()
    test_name = sys.argv[3]
    workstream = sys.argv[4].strip()
    
##    test_name = "STAD_19_Jun"
##    prjid = "805"
##    userid = "42"
##    workstream="FI"
##    test_name = test_name.lower()
##    print("Start process - " + str(datetime.datetime.now()))
    ws_process(test_name,prjid,userid, workstream)
##    print("endprocess - " + str(datetime.datetime.now()))

