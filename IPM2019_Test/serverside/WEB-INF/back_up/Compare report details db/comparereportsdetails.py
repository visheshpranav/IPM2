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

def Getcomparereports():
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    report_query = 'SELECT distinct(REP_ID) FROM uat.report_imperatives_patterns WHERE USER_ID="44" and CompareRP IS NOT NULL;'
    rep_id= cursor.execute(report_query).fetchall()
    listToStr = ' '.join(map(str, rep_id))
    s1=re.sub("[',()]","",listToStr)
    k2=s1.split()
    for username in k2:
        query = 'SELECT distinct(`REP_NAME`),(`DATE`) FROM report_info where rep_id ="'+username+'";'
        REP_NAME = cursor.execute(query).fetchall()
        comp=str(REP_NAME)
        comp1=comp.replace('datetime.date(', '')
        comp2 = comp1.replace('[]', '')
        if(comp2 != "" ):
             comp3=comp2.replace(',', '/')
             comp4=comp3.replace('/', ',', 1)
             print(comp4)
             
             
##        j= comp.split('\'')[4].replace('datetime.date(', '')
##        f = j.replace(',', '/')
##        t = f.replace(')', '')
##        print(comp.split('\'')[3],",",t[1:].strip())
        
# main function
if __name__ == "__main__":
       print("Content-type: text/html \n");

##       insert_uploadlogentry(username, userid, test_name)
##       insert_ImpDetails("IMP043", userid, test_name,"P72","csv", "Customization","WebSphere", Base_name, Comp_name, TempNM)
       Getcomparereports()
    
