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
##prj_name = form.getvalue("prj_name")
user_id = form.getvalue("user_id")
##user_id = "42"

#fetch test values from quaifier table
def get_values(con,user_id):
        query = 'SELECT `REP_NAME`,`REP_ID` FROM report_info WHERE `USER_ID` = "'+str(user_id)+'" order by `REP_ID` desc;'
        con.execute(query)
        res = con.fetchall()
        return res

#database connection
def create_connection(user_id):
	db1 = pyodbc.connect("DSN="+DSN_NAMEE)
	cur = db1.cursor()
	ret = get_values(cur,user_id)
	return ret


def get_ws():
    es = Elasticsearch('localhost', port=9200)

    res = es.search(index='sap_stad', body={"size":10000, "query": {"match_all": {}}})

    stad_tcode=[]

    for val in res['hits']['hits']:
        stad_tcode.append(val['_source']['TRANSACTION_OR_JOBNAME'])

    es = Elasticsearch('localhost', port=9200)

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
    print(ws_list)

    return ws_list



ret = create_connection(user_id)
ws_list=get_ws()
print ("Content-type: text/html \n\n");
print(str(ret)+"&&"+str(ws_list))


	
	
