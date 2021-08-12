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



def get_basecompdetail():
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
##    report_query = 'SELECT rep_id FROM report_info where user_id="44" and rep_name ="testrpnames"'
    report_query = 'SELECT rep_id FROM report_info where user_id='+userid+' and rep_name ="'+test_name+'";'
    rep_id= cursor.execute(report_query).fetchone()[0]
    k=str(rep_id)
    report_query = 'SELECT BaseRP,CompareRP,TemplateNM FROM report_imperatives_patterns where REP_ID ="'+k+'";'
    rep_id2= cursor.execute(report_query).fetchone()
    print(rep_id2)
    db1.commit()
    return rep_id



# main function
if __name__ == "__main__":
       print("Content-type: text/html \n");
       form = cgi.FieldStorage()
       userid = form.getvalue('user_id').strip()
       test_name = form.getvalue('Txt_reportname')
##       userid = "44"
##       test_name = "Testcompareeeee"
       get_basecompdetail()
