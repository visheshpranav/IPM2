#######################################################################
#Application : CBOL
#Build : v3
#Desc: Get the TestName form DB for dropdown
#Created by : Rajkumar
#Date of Modification:8/9/2018
########################################################################

import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc
import configparser

parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAME = parser.get('DSN','DSN_NAME')

form = cgi.FieldStorage()
user_id = form.getvalue("user_id").strip()
appname = form.getvalue("appname").strip()
##appname = "twa"
##user_id="1"

#fetch test values from quaifier table
def get_values(con,user_id):
        query = 'select  concat(IMP_ID ," - " , IMP_DESCRIPTION) from imperative_info where IMP_ID in (select imp_id from online_imperative_info where app_name = "'+appname+'");'
        con.execute(query)
        res = con.fetchall()
        return res	

#database connection
def create_connection(user_id):
	db1 = pyodbc.connect("DSN="+DSN_NAME)
	cur = db1.cursor()
	ret = get_values(cur, user_id)
	return ret	

print ("Content-type: text/html \n\n");
ret = create_connection(user_id)
for Imperative_name in ret:
        print(str(Imperative_name).split('\'')[1])


	
	
