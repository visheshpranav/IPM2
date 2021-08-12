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

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
STAD_INDEX_NAME = parser.get('Upload','STAD_INDEX_NAME')
NFR_INDEX_NAME = parser.get('Upload','NFR_INDEX_NAME')

def process(logList,prjid,userid):
    es = Elasticsearch('localhost', port=9200)
    raw_data = []
    exp_rtlist = []
    Tcodes = []
    nfr_tcode_dict={}
    NFR_Log_Name = str(userid)+"_"+logList[0]
##    print(NFR_Log_Name)
    res_nfr = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["TCODE","TARGET_RES_TIME"],"query": {"match": {"LOG_NAME.keyword":NFR_Log_Name}}}, 
                index = NFR_INDEX_NAME)
    for doc in res_nfr:
        nfr_tcode_dict[doc['_source']['TCODE']]= doc['_source']['TARGET_RES_TIME']
    i=0    
    for logName in logList:
        Log_Name = str(userid) +"_"+logName
        res=es.search(index=STAD_INDEX_NAME,body={ "size":0, "query": {"bool": {"must": [{"match":{"LOG_NAME.keyword":Log_Name}}]}},\
                                               "aggs": {"uniqtcode" : {"terms": {"field" : "TRANSACTION_OR_JOBNAME.keyword", "size":10000},\
                                               "aggs": {"avg_res": {"avg": {"field": "RESPONSE_TIME"}}}}}})
        agg_val=res['aggregations']['uniqtcode']['buckets']
        for s in agg_val:
            if s['key'] in nfr_tcode_dict.keys():
                tcode = s['key']
                data_str = logName+","+s['key'] + "," + nfr_tcode_dict[tcode] + "," + str(round(s['avg_res']['value'],2))
                str_val = logName+","+",".join(data_str)
                exp_rtlist.append(tcode+","+nfr_tcode_dict[tcode])
                raw_data.append(data_str)
                Tcodes.append(tcode)
        i=i+1

    seen = set()
    seen_add = seen.add
    logList =  [x for x in logList if not (x in seen or seen_add(x))]
    head = ",".join(logList)
    Tcodes = set(Tcodes)
    exp_rtlist = set(exp_rtlist)
    final_data = []
    for tcode in Tcodes:
        match_rt = [s for s in exp_rtlist if tcode+"," in s]
        exp_rt = match_rt[0].split(",")[1]
        str_val = tcode+","+exp_rt
        for logName in logList:
##            print(logName)
            match_list = [s for s in raw_data if logName+","+tcode+"," in s]
            if match_list:
                #print("match - " + str(match_list))
                for i in match_list:
                    spli_arr = i.split(",")
                    act_rt = spli_arr[3]
                str_val = str_val+","+str(round(float(act_rt)/1000,2))
            else:
                str_val = str_val+","+"-"
        final_data.append(str_val)
    return final_data,head

if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
##    prjid = form.getlist('prjid')#form.getvalue('prjid').strip()
##    userid = form.getvalue('userid').strip()    
##    logList = form.getlist('log_List')

##    userid = sys.argv[1].strip()
##    prjid = sys.argv[2].strip()
##    logList = sys.argv[3]
##    
##    prjid = prjid.split(";")
##    logList = logList.split(";")
##    logList = [s.strip().lower() for s in logList] 

    logList = ['pr9,pr10']
    logList = logList[0].split(",")
    logList = [s.strip().lower() for s in logList] 
    prjid = ['732,733']
    prjid = prjid[0].split(",")
    userid = "41"
    
    final_data,head = process(logList,prjid,userid)
    print("Tcode"+","+"ExpResTime"+","+head)
    print(final_data)
    #print(data)
    #print("endprocess - " + str(datetime.datetime.now()))
