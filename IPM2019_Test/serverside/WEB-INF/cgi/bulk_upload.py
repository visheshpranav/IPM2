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
from bucket_access import file_download

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
            return "FUP 1 File Uploaded Successfully"
        elif fileitem.endswith(".tar"):
            print(full_dir_path)
            # g = open(full_dir_path + fn, 'wb').write(fileitem.file.read())
    ##        enc = sys.getdefaultencoding()
            tar_handler = tarfile.open(fileitem, "r", encoding="utf-8")
    ##            if any(x.find("/")>0 for x in tar_handler.getnames()):
    ##                shutil.rmtree(fileitem)
    ####                os.remove(full_dir_path + fn)
    ##                return "FUP 0,Please Upload The Valid File"
    ####		exit(1)
            tar_handler.extractall(full_dir_path)
            tar_handler.close()
            delete_folder = []
            for root,folders,files in os.walk(full_dir_path):
                for folder in folders:
                    delete_folder.append(root+'\\'+folder)
                for file in files:
                    try:
                        shutil.move(root+'\\'+file,full_dir_path)
                    except Exception:
                        continue
            for folder in delete_folder:
                if os.path.exists(folder):
                    shutil.rmtree(folder)

            
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
       fileitems = form.getvalue('filenames').split(',')
       username = form.getvalue('username')
       userid = form.getvalue('userid').strip()
       test_name = form.getvalue('Txt_reportname')
       Logtypes = form.getvalue('Log_type')
       print(type(fileitems))
        #manual execution
##       fileitems = "rb.100k.1.tar"
##       username = "murex"
##       userid = "44"
##       test_name = "rd2"
##       Logtypes = "TradeInsertion-rb.100k.1.tar"
##       test_name = test_name.strip().lower()
       logtype_i=0
       try:
           if is_test_existing(userid, test_name):
               if type(fileitems) is list:
                   Logtypes_arr = Logtypes.split(',')
                   for fileitem in fileitems:
                       typelog = Logtypes_arr[logtype_i].split('-')[0]
                       full_file_path = file_download(fileitem,userid,test_name,typelog)
                       msg = run_upload(full_file_path,test_name,typelog)
                       print(msg)
                       logtype_i = logtype_i+1
               else:
                   typelog = Logtypes.split('-')[0].replace('\\r','')
                   full_file_path = file_download(fileitems,userid,test_name,typelog)
                   print(full_file_path)
                   msg = run_upload(full_file_path,test_name,typelog)
                   print(msg)
               if msg!= "FUP 0,Please Upload The Valid File":
                   insert_uploadlogentry(username, userid, test_name) 
           else:
               print("TAP 0, Report name already exists")
       except Exception as e:
           print(e)
