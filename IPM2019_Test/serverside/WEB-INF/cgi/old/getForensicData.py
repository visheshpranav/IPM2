#######################################################################
#Application : LAPAM
#Build : 2019
#Desc: get forensic values
#Modified by: Rajkumar
#Date of Modification:20/2/2019
########################################################################
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc
import configparser

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAME = parser.get('DSN','DSN_NAME')
 
''' database connection '''
def fetch_forensic(user_id, rep_id):
        con = pyodbc.connect("DSN="+DSN_NAME)
        cur = con.cursor()
        query = "SELECT IFNULL(description,'') from forensic where user_id="+user_id+" and rep_id="+rep_id+";"
        cur.execute(query)
        res = cur.fetchall()
        for val in res:
                print(val[0])
    
#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    user_id = form.getvalue('user_id')
    rep_id = form.getvalue('rep_id')
##    user_id="1"
##    rep_id="81"
##    Imperative_Id = "IMP001"
    fetch_forensic(user_id, rep_id)
