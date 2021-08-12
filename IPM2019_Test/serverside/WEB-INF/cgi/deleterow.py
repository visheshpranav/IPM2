#######################################################################
#Application : LAPAM
#Build : 2019
#Desc: delete value from table
#Created by: Rajkumar
#Date of Modification:8/2/2018
########################################################################
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc
import configparser
import os,shutil

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
DATA_PATH = parser.get('Upload','Oflpath')

''' declare variables '''
form = cgi.FieldStorage()
tablename = form.getvalue('tablename')
fieldname = form.getvalue('fieldname')
id_val = form.getvalue('id_val')

##tablename = "Report_Info"
##fieldname = "REP_NAME"
##id_val = "test31_03"

userid ="44"
##print(tablename,fieldname,id_val)
report_path = "../../../WEB-INF/classes/static/html/Reports/44_"+id_val
dir_path = DATA_PATH + "Cache\\" + userid + "\\" + id_val+'\\'


''' update user details in databse '''
def delete_value(con):
        i = 0
        query = 'delete from '+tablename+' WHERE '+fieldname+' = "'+id_val+'";'
        con.execute(query)
        ret = "success"
        
''' database connection '''
def create_connection():
        con = pyodbc.connect("DSN="+DSN_NAMEE)
        cur = con.cursor()
        delete_value(cur)
        con.commit()
        if os.path.exists(report_path):
##                print(report_path)
                shutil.rmtree(report_path)
        if os.path.exists(dir_path):
##                print(dir_path)
                shutil.rmtree(dir_path)
        print ("Success");

print ("Content-type: text/html \n\n");
con = create_connection()
