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
import shutil
from itertools import islice
import re
import pyodbc,datetime
import tarfile
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


# check given testname alerady exists in database
def is_test_existing(userid, test_name):
    query = 'select REP_NAME FROM REPORT_INFO WHERE REP_NAME = "'+test_name+'" and user_id="'+userid+'";'
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    res = cursor.execute(query).fetchall()
    if len(res) == 0:
        return True
    return False    

# upload log file into data folder
def run_upload(fileitem,test_name,logtype):
    # fn = os.path.basename(fileitem.filename)
##    fn = fileitem
    if not os.path.exists(DATA_PATH + "Cache\\" + userid):
        os.mkdir(DATA_PATH + "Cache\\" + userid)
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\"+str(logtype)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    full_dir_path = dir_path + "\\"

    try:
        if fileitem.endswith(".zip"):
            zip_handler = zipfile.ZipFile(fileitem, "r")
            if any(x.find("/")>0 for x in zip_handler.namelist()):
                return "FUP 0,Please Upload The Valid File"
##		exit(1)

            zip_handler.extractall(full_dir_path)
            
            zip_handler.close()
        elif fileitem.endswith(".tar"):
            # g = open(full_dir_path + fn, 'wb').write(fileitem.file.read())
            tar_handler = tarfile.TarFile(fileitem, "r")
            if any(x.find("/")>0 for x in tar_handler.getnames()):
                shutil.rmtree(fileitem)
##                os.remove(full_dir_path + fn)
                return "FUP 0,Please Upload The Valid File"
##		exit(1)
            tar_handler.extractall(full_dir_path)
            tar_handler.close()
            shutil.rmtree(fileitem)
##            os.remove(full_dir_path + fn)
            return "FUP 1 File Uploaded Successfully"
        else:
            # if fileitem.endswith((".log",".txt",".xlsx",".csv",".001")):
            #     g = open(full_dir_path + fn, 'wb').write(fileitem.file.read())
            #     print(full_dir_path)
            #     return "FUP 1 File Uploaded Successfully"
            # else:
            return "FUP 0,Please Upload The Valid File"
            exit(1)

    except Exception as e:
        return 'FUP 0,Unexpected error:{exception}'.format(exception=e)
        exit(1)

# main function
if __name__ == "__main__":
       print("Content-type: text/html \n");
       form = cgi.FieldStorage()
       fileitems = form.getvalue('filepath')
       username = form.getvalue('username')
       userid = form.getvalue('userid').strip()
       test_name = form.getvalue('Txt_reportname')
       Logtypes = form.getvalue('Log_type')
##       print(type(fileitems))
        #manual execution
##       fileitems = ["abc.txt"]
##       username = "demo"
##       userid = "9"
##       test_name = "t5"
##       Logtypes = "WebSphere-SystemOut.log,JVM-native_stderr.log.20181116.112811.93240.001"
##       test_name = test_name.strip().lower()
       logtype_i=0
       try:
           if is_test_existing(userid, test_name):
               if type(fileitems) is list:
                   Logtypes_arr = Logtypes.split(',')
                   for fileitem in fileitems:
                       typelog = Logtypes_arr[logtype_i].split('-')[0]
                       msg = run_upload(fileitem,test_name,typelog)
                       print(msg)
                       logtype_i = logtype_i+1
               else:
                   typelog = Logtypes.split('-')[0].replace('\\r','')
                   msg = run_upload(fileitems,test_name,typelog)
                   print(msg)
               if msg!= "FUP 0,Please Upload The Valid File":
                   insert_uploadlogentry(username, userid, test_name) 
           else:
               print("TAP 0, Report name already exists")
       except Exception as e:
           print(e)
