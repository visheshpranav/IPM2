#######################################################################
#Application : LAPAM
#Build : v0
#Desc: Upload the log 
#Created by : Karpagam
#Modified by: Karpagam
#Date of Modification:13/6/2018
#Reason for modification:DSN Input variable changed
########################################################################

import os
import zipfile
import cgi, cgitb
from itertools import islice
import re
import pyodbc,datetime
from datetime import date
import datetime 
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

def insert_ImpDetails(userid,username):
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    report_query = 'SELECT rep_id FROM report_info where user_id='+userid+' and rep_name ="'+report_name+'";'
    rep_id= cursor.execute(report_query).fetchone()[0]
    query = """INSERT INTO report_imperatives_patterns (`USER_ID`, `REP_ID`, `IMP_ID`, `PAT_LIST`, `LOG_TYPE`, `OUTPUT`, `LOGIC`)
                VALUES (%s,%s,'%s','%s','%s','%s','%s');"""
    cursor.execute(query %(userid,rep_id,impid,pattern,logtype_val,outcome, logic))
    db1.commit()
    return rep_id

def insert_ImpDetails2(userid,username):
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    report_query = 'SELECT PASSWORDDATE FROM user_info where user_id='+userid+' and USER_NAME ="'+username+'";'
    PD= cursor.execute(report_query).fetchone()[0]
    date_time_str = PD
    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')
##    print('Date:', date_time_obj.date())
##    print('Time:', date_time_obj.time())
##    print('Date-time:', date_time_obj)
##    k=PD.split('-')
##    year=(k[0])
##    month=(k[1])
##    dates=(k[2])
##    print(year,month,date)
    date1 = date_time_obj.date()
    date2 = date.today()
##    print(numOfDays(date1, date2), "days")
    if(numOfDays(date1, date2)>=30 and numOfDays(date1, date2)<=34):
        print("Password going to expire soon!Kindly Reset your password")
    elif(numOfDays(date1, date2)==35):
        print("Password going to expire in 5 days, Kindly Reset your password")
    elif(numOfDays(date1, date2)==36):
        print("Password going to expire in 4 days, Kindly Reset your password")
    elif(numOfDays(date1, date2)==37):
        print("Password going to expire in 3 days, Kindly Reset your password")
    elif(numOfDays(date1, date2)==38):
        print("Password going to expire in 2 days, Kindly Reset your password")
    elif(numOfDays(date1, date2)==39):
        print("Password going to expire tomorrow, Kindly Reset your password")
    elif(numOfDays(date1, date2)==40):
        print("Password will expire today and get disable, Kindly Reset your password")
    elif(numOfDays(date1, date2)>40):
        print("Password Expired Already so you cant proceed till reset")
    else:
        pass
    
   

##    query = """INSERT INTO report_imperatives_patterns (`USER_ID`, `REP_ID`, `IMP_ID`, `PAT_LIST`, `LOG_TYPE`, `OUTPUT`, `LOGIC`)
##                VALUES (%s,%s,'%s','%s','%s','%s','%s');"""
##    cursor.execute(query %(userid,rep_id,impid,pattern,logtype_val,outcome, logic))
##    db1.commit()
##    return rep_id

def numOfDays(date1, date2):
    return (date2-date1).days


# main function
if __name__ == "__main__":
       print("Content-type: text/html \n");
       form = cgi.FieldStorage()
       username = form.getvalue('username')
       userid = form.getvalue('user_id').strip()
##       test_name = form.getvalue('Txt_reportname')
        #manual execution
##       fileitems = ["abc.txt"]
##       username = "murex"
##       userid = "44"
##       test_name = "Karte"
##       Logtypes = "WebSphere-SystemOut.log,JVM-native_stderr.log.20181116.112811.93240.001"
##       test_name = test_name.strip().lower()
##       insert_uploadlogentry(username, userid, test_name)
       insert_ImpDetails2(userid,username)
