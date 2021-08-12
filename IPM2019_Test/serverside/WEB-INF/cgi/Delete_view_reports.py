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
import json
import os, cgi, configparser
import zipfile
import cgi, cgitb
from itertools import islice
import re
import pyodbc,datetime
import os,shutil
output_string = ""
value = ""
imp_name=[]
import configparser

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')
DSN_NAME = parser.get('DSN','DSN_NAMEE')

#insert upload details into log_info table


def deletereports():
    db1 = pyodbc.connect("DSN="+DSN_NAME)
    cursor = db1.cursor()
    for report in reportname:
        query = 'DELETE FROM report_info WHERE USER_ID="'+userid+'" and REP_NAME ="'+report+'";'
        cursor.execute(query)
        db1.commit()
        if os.path.exists(report_path+report):
            shutil.rmtree(report_path+report)
        if os.path.exists(dir_path+report+'\\'):
            shutil.rmtree(dir_path+report+'\\')
        
# main function
if __name__ == "__main__":
       print("Content-type: text/html \n");
       form = cgi.FieldStorage()
       userid = form.getvalue('user_id').strip()
       log_type = form.getvalue('logtype').strip()
       reportname = json.loads(form.getvalue('reportlist'))

##       userid = "44"
##       log_type = "TradeInsertion"
##       reportname = ["tesgh"]
       
       report_path = "../../../WEB-INF/classes/static/html/Reports/44_"
       dir_path = DATA_PATH + "Cache\\" + userid + "\\"
       deletereports()
       print("Reports Deleted")
