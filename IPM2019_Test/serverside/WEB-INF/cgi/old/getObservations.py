#######################################################################
#Application : LAPAM
#Build : 2019
#Desc: get observation values
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
def fetch_Obs(user_id, rep_id, Imperative_Id):
        con = pyodbc.connect("DSN="+DSN_NAME)
        cur = con.cursor()
        query = "SELECT IFNULL(observation, ''), IFNULL(recommendation, '') from recommendations where user_id="+user_id+" and rep_id="+rep_id+" and imp_id='"+Imperative_Id+"';"
        cur.execute(query)
        res = cur.fetchall()
        for val in res:
                print(val)
    
#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    user_id = form.getvalue('user_id')
    rep_id = form.getvalue('rep_id')
    Imperative_Id = form.getvalue('Imperative_Id')
##    user_id="5"
##    rep_id="276"
##    Imperative_Id = "IMP001"
    fetch_Obs(user_id, rep_id, Imperative_Id)
