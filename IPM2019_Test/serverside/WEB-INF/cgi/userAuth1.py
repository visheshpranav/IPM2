#######################################################################
#Application : LAPAM2019
#Build : v0
#Desc: Check the user authentication 
#Created by : Muthu
#Modified by: 
#Date of Modification:25/01/2019
#code developed as part of story ST003 - Login
########################################################################

import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc
import configparser

parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

# database connection 
def create_connection():
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    return cur

# validate the given user credential
def authenticate_user(conn,user,passwd):
    query = 'SELECT USER_ID from user_info where USER_NAME="'+str(user)+'" and Password = "'+str(passwd)+'" and Status=1;'
    res = conn.execute(query)
    if len(conn.fetchall()) != 0:
        return True
    return False

# main function
if __name__ == "__main__":
    form = cgi.FieldStorage()
    user = form.getvalue('Txt_Username')
    passwd = form.getvalue('Txt_Password')
##    user = "LAPAMd"
##    passwd="lapam@123"
    conn = create_connection()
    print ("Content-type: text/html \n\n");
    if authenticate_user(conn,user,passwd):
        query = 'SELECT USER_ID,App_name, Role from user_info where USER_NAME="'+str(user)+'" and Password = "'+str(passwd)+'";'
        conn.execute(query)
        res = conn.fetchone()
        userid,app_name,Role = res[0],res[1], res[2]
        print ("UAP1", userid, app_name, Role)
    else:
        print("UAP0")
