#######################################################################
#Application : LAPAM
#Desc: Insert User
#Created by : Vinotha
#Modified by : Rajkumar
#Date of Modification:16/8/2018
#Reason for modification:Column name change due to DB re-design
########################################################################
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc, html
import configparser
from elasticsearch import Elasticsearch



#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
STAD_INDEX_NAME = parser.get('Upload','STAD_INDEX_NAME')

# variable declaration
form = cgi.FieldStorage()
tab_arr = []
row_arr = form.getlist("bfc_list")
userid = form.getvalue('userid').strip()
test_name = form.getvalue('repid')
log_name = userid +"_"+ test_name
##log_name = "42_stad_3007"
##row_arr = ['dfd,VA01,1,STAD_3007']

#insert values into User database table
def insert_values(con):
    es = Elasticsearch('localhost', port=9200)
    STAD_INDEX_NAME = parser.get('Upload','STAD_INDEX_NAME')
    row_arr_list = row_arr[0].split(",")
    i=0
    for bfc_leval in range(int(len(row_arr_list)/4)):
        res = es.search(index=STAD_INDEX_NAME, body={"query":{"bool":{"must":[{ "match":{"LOG_NAME.keyword": ""+log_name+"" }},
                                                                                     {"match": {"TRANSACTION_OR_JOBNAME.keyword": ""+row_arr_list[i+1]+"" }}]}}, "aggs":{"avg_res":{"avg":{"field": "RESPONSE_TIME" }}}})
        avg_val = round(res["aggregations"]["avg_res"]["value"],2)
        print(avg_val)
        query = 'insert into bfc(BusinessFlowName, Tcode, Responsetime, Report_Name) values("'+row_arr_list[i]+'","'+row_arr_list[i+1]+'","'+str(avg_val)+'","'+row_arr_list[i+3]+'");'
        con.execute(query)
        con.commit()
        i=i+4

# database connection
def create_connection():
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    insert_values(cur)
    con.commit()
    print ("Success")

print ("Content-type: text/html \n");   
con = create_connection()
