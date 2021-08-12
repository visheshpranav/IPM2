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
from re_checking import *

parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')


#fetch test values from quaifier table
def get_values(con,user_id, report_name):
        report_query = 'SELECT rep_id FROM report_info where user_id='+user_id+' and rep_name ="'+report_name+'";'
        try:
                rep_id= con.execute(report_query).fetchone()[0]
                print("REP_ID - " + str(rep_id))
##                if user_id == "44":
##                        query = 'select  concat(IMP_ID ," - " , IMP_DESCRIPTION) from imperative_info where IMP_ID in (select imp_id from report_imperatives_patterns where Rep_id = '+str(rep_id)+' and user_id='+user_id+') order by imp_id desc;'
##                else:
                query = 'select  concat(IMP_ID ," - " , IMP_DESCRIPTION) from imperative_info where IMP_ID in (select imp_id from report_imperatives_patterns where Rep_id = '+str(rep_id)+' and user_id='+user_id+');'
                con.execute(query)
                res = con.fetchall()
                return res
        except:
                print("Invalid report")
                
                

#database connection
def create_connectionReport(user_id, report_name):
        db1 = pyodbc.connect("DSN="+DSN_NAMEE)
        cur = db1.cursor()
        if authenticate_user(cur,user_id):
                ret = get_values(cur, user_id, report_name)
                return ret
        else:
               print("Invalid User")
               
# validate the given user credential
def authenticate_user(conn,user):
    query = 'SELECT USER_ID from user_info where user_id="'+str(user)+'" and Status=1;'
    res = conn.execute(query)
##    print(res)
##    print(len(conn.fetchall()))
    if len(conn.fetchall())!= 0:
        return True
    return False


if __name__ == "__main__":
        print ("Content-type: text/html \n");
        form = cgi.FieldStorage()
        user_id=""
        report_name=""
        if numeric_check(form.getvalue("user_id")) and alphanumeric_hypen_check(form.getvalue("report_name")):
        #if form.getvalue("user_id") and form.getvalue("report_name"):
                user_id = form.getvalue("user_id").strip()
                report_name = form.getvalue("report_name").strip()
##        user_id="42"
##        report_name="STAD_3007"
        ret = create_connectionReport(user_id, report_name)
        if ret:
                for Imperative_name in ret:
                        print(str(Imperative_name).split('\'')[1])
        else:
                print('Kindly provide the User ID and Report Name \n')

	
	
