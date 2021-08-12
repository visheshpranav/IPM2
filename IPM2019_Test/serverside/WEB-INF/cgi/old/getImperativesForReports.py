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
def get_values(con,user_id, report_name):
        report_query = 'SELECT rep_id FROM report_info where user_id='+user_id+' and rep_name ="'+report_name+'";'
        rep_id= con.execute(report_query).fetchone()[0]
        print("REP_ID - " + str(rep_id))
        query = 'select  concat(IMP_ID ," - " , IMP_DESCRIPTION) from imperative_info where IMP_ID in (select imp_id from report_imperatives_patterns where Rep_id = '+str(rep_id)+' and user_id='+user_id+');'
        con.execute(query)
        res = con.fetchall()
        return res

#database connection
def create_connectionReport(user_id, report_name):
        db1 = pyodbc.connect("DSN="+DSN_NAME)
        cur = db1.cursor()
        ret = get_values(cur, user_id, report_name)
        return ret


if __name__ == "__main__":
        form = cgi.FieldStorage()
        user_id = form.getvalue("user_id").strip()
        report_name = form.getvalue("report_name").strip()
##        user_id="5"
##        report_name="check"
        print ("Content-type: text/html \n");
        ret = create_connectionReport(user_id, report_name)
        for Imperative_name in ret:
                print(str(Imperative_name).split('\'')[1])


	
	
