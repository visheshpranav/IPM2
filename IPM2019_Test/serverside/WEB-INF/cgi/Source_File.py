#######################################################################
#Application : LAPAM
#Build : v0
#Desc: Upload the log 
#Created by : Manohar
#Modified by: Manohar
#Date of Modification:13/6/2018
#Reason for modification:DSN Input variable changed
########################################################################

import os
import zipfile
import cgi, cgitb
from itertools import islice
import re
import pyodbc,datetime
output_string = ""
value = ""
imp_name=[]
import configparser

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

#insert upload details into log_info table
def insert_uploadlogentry(username, userid, test_name):
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    query = """INSERT INTO REPORT_INFO (`USER_ID`, `STATUS`, `REP_NAME`, `DATE`)
                VALUES ('%s','1','%s',now());"""
    cursor.execute(query %(userid,test_name))
    db1.commit()

def insert_ImpDetails(impid, userid, report_name,pattern,outcome, logic,logtype_val,Brp,Crp,Tnm):
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    report_query = 'SELECT rep_id FROM report_info where user_id='+userid+' and rep_name ="'+report_name+'";'
    rep_id= cursor.execute(report_query).fetchone()[0]
    query = """INSERT INTO report_imperatives_patterns (`USER_ID`, `REP_ID`, `IMP_ID`, `PAT_LIST`, `LOG_TYPE`, `OUTPUT`, `LOGIC`, `BaseRP`, `CompareRP`, `TemplateNM`)
                VALUES (%s,%s,'%s','%s','%s','%s','%s','%s','%s','%s');"""
    cursor.execute(query %(userid,rep_id,impid,pattern,logtype_val,outcome, logic, Brp, Crp, Tnm))
    db1.commit()
    return rep_id

def sourcetest(userid,reportname,sourcefile):
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    query = 'UPDATE report_info SET `Source_File` ="'+sourcefile+'" WHERE user_id='+userid+' and  REP_NAME = "'+reportname+'";'
    cursor.execute(query)
    db1.commit()


# main function
if __name__ == "__main__":
       print("Content-type: text/html \n");
       form = cgi.FieldStorage()
       userid = form.getvalue('user_id')
       reportname = form.getvalue('report_name')
       sourcefile = form.getvalue('source_file')
        #manual execution
##       fileitems = ["abc.txt"]
##       username = "murex"
##       userid = "44"
##       test_name = "Karte"
##       Logtypes = "WebSphere-SystemOut.log,JVM-native_stderr.log.20181116.112811.93240.001"
##       test_name = test_name.strip().lower()
##       Base_name = "test_trade40"
##       Comp_name = "test_trade41"
       ##       username = "murex"
##       username = "murex"
       

##       Base_name = "rs12"
##       Comp_name = "rs1"
##       TempNM = "TRD_ContractID_ONLY"
       sourcetest(userid,reportname,sourcefile)
##       insert_uploadlogentry(username, userid, test_name)
##       insert_ImpDetails("IMP043", userid, test_name,"P72","csv", "Customization","WebSphere", Base_name, Comp_name, TempNM)
       print("Report created you can see it in View Reports")
