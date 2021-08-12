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
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
 
''' database connection '''
def update_obs(con, user_id, rep_id, Imperative_Id, observation):
        cur = con.cursor()
        query = "update recommendations set recommendation = '"+observation+"' where user_id="+user_id+" and rep_id="+rep_id+" and imp_id='"+Imperative_Id+"';"
        cur.execute(query)
        cur.commit()

''' database connection '''
def insert_obs(con, user_id, rep_id, Imperative_Id, observation):
        cur = con.cursor()
        query = "insert into recommendations(rep_id, user_id, imp_id, recommendation) values("+rep_id+","+user_id+",'"+Imperative_Id+"','"+observation+"');"
        cur.execute(query)
        cur.commit()
# validate the given user credential
def check_imp_exist(conn,user_id, rep_id, Imperative_Id):
        cur = conn.cursor()
        query = "SELECT recommendation from recommendations where user_id="+user_id+" and rep_id="+rep_id+" and imp_id='"+Imperative_Id+"';"
        res = cur.execute(query)
        if len(cur.fetchall()) != 0:
                return True
        return False
    
#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    user_id = form.getvalue('user_id')
    rep_id = form.getvalue('rep_id')
    Imperative_Id = form.getvalue('Imperative_Id')
    observation = form.getvalue('Observation')
    con = pyodbc.connect("DSN="+DSN_NAMEE)
##    user_id="41"
##    rep_id="782"
##    Imperative_Id = "IMP029"
##    observation = "Test123"
    if check_imp_exist(con, user_id, rep_id, Imperative_Id):
            update_obs(con, user_id, rep_id, Imperative_Id, observation)
    else:
            insert_obs(con, user_id, rep_id, Imperative_Id, observation)
