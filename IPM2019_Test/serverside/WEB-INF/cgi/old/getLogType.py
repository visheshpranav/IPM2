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

#fetch test values from quaifier table
def get_values(con,app_name):
        query = 'SELECT LOG_TYPE from project_pattern_info where `APP_NAME` = "'+str(app_name)+'";'
        con.execute(query)
        res = con.fetchall()
        return res	

#database connection
def create_connection(app_name):
	db1 = pyodbc.connect("DSN="+DSN_NAME)
	cur = db1.cursor()
	ret = get_values(cur,app_name)
	return ret

if __name__ == "__main__":        
        print ("Content-type: text/html \n\n");
        form = cgi.FieldStorage()
        app_name = form.getvalue("app_name").strip()
        #app_name = "TWA"
        ret = create_connection(app_name)
        for appname in ret:
                print(str(appname).split('\'')[1])


	
	
