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
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

##form = cgi.FieldStorage()
##user_name = form.getvalue("user_name").strip()
##user_name = "LAPAMd"
#fetch test values from quaifier table
def get_values(con):
        query = 'SELECT USER_NAME FROM lapam2019.user_info;'
        con.execute(query)
        res = con.fetchall()
        print(res)

#database connection
def create_connection():
	db1 = pyodbc.connect("DSN="+DSN_NAMEE)
	cur = db1.cursor()
	ret = get_values(cur)
	return ret	

print ("Content-type: text/html \n\n");
ret = create_connection()



	
	
