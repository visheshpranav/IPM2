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
import cgi, os

parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAME = parser.get('DSN','DSN_NAME')

form = cgi.FieldStorage()
user_name = form.getvalue("user_name").strip()
type = form.getvalue("type").strip()
##user_name = "Murex"
#fetch test values from quaifier table
def get_values(con,user_name):
        query = 'SELECT CAST(`USER_ID` as CHAR(11)) as USER_ID,`REP_Name`,`DATE` FROM report_info WHERE\
        `USER_ID` = (select distinct(`USER_ID`) from user_info where `USER_NAME` = "'+str(user_name)+'") order by DATE asc;'
        con.execute(query)
        res = con.fetchall()
        return res	

#database connection
def create_connection(user_name):
	db1 = pyodbc.connect("DSN="+DSN_NAME)
	cur = db1.cursor()
	ret = get_values(cur,user_name)
	return ret	

print ("Content-type: text/html \n\n");
ret = create_connection(user_name)
##print(ret)
for username in ret:
        #print(str(username).split('\'')[1]+","+str(username).split('\'')[3])
        k=str(username).split('\'')[3]
        #print(k)
        output_path = "C:/LAPAM2019/DataLake/Cache/44/"+k+"/"+type;
        #print(output_path)
        if os.path.exists(output_path):
            z= str(username)
            #z.split('\'')[3]
            j= z.split('\'')[4].replace('datetime.date(', '')
            f = j.replace(',', '/')
            t = f.replace(')', '')
            print(z.split('\'')[3],",",t[1:].strip())
            
            
            

	
	
