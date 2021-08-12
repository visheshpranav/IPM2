#######################################################################
#Application : LAPAM
#Build : v3
#Desc: Get the TestName form DB for dropdown
#Created by : Rajkumar
#Date of Modification:8/9/2018
########################################################################

import cgi, cgitb,sys
import cgitb; cgitb.enable()
import pyodbc
import configparser

parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

form = cgi.FieldStorage()
##prj_name = form.getvalue("prj_name")
user_id = form.getvalue("user_id")
##user_id = "42"

#fetch test values from quaifier table
def get_values(con,user_id):
        query = 'SELECT `REP_NAME`,`REP_ID` FROM report_info WHERE `USER_ID` = "'+str(user_id)+'" order by `REP_ID` desc;'
        con.execute(query)
        res = con.fetchall()
        return res	

#database connection
def create_connection(user_id):
	db1 = pyodbc.connect("DSN="+DSN_NAMEE)
	cur = db1.cursor()
	ret = get_values(cur,user_id)
	return ret	

ret = create_connection(user_id)
print ("Content-type: text/html \n\n");
print(ret)


	
	
