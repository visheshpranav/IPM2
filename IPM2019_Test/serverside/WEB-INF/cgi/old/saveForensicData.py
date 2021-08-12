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
import configparser, shutil

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAME = parser.get('DSN','DSN_NAME')
 
''' database connection '''
def update_obs(con, user_id, rep_id, description):
        cur = con.cursor()
        query = "update forensic set description = '"+description+"' where user_id="+user_id+" and rep_id="+rep_id+";"
        cur.execute(query)
        cur.commit()

''' database connection '''
def insert_obs(con, user_id, rep_id, description):
        cur = con.cursor()
        query = "insert into forensic values("+rep_id+","+user_id+",'"+description+"');"
        cur.execute(query)
        cur.commit()
# validate the given user credential
def check_imp_exist(conn,user_id, rep_id):
        cur = conn.cursor()
        query = "SELECT * from forensic where user_id="+user_id+" and rep_id="+rep_id+";"
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
    description = form.getvalue('description')
    con = pyodbc.connect("DSN="+DSN_NAME)
##    user_id="5"
##    rep_id="291"
##    description = "Test1adf23dfdsfsdfsdfsdf"
    if check_imp_exist(con, user_id, rep_id):
            update_obs(con, user_id, rep_id, description)
    else:
            insert_obs(con, user_id, rep_id, description)
    file_name = user_id +"_"+ rep_id + "_summaryreport.txt"
    with open(file_name, 'w') as txt_file:
        txt_file.write(description)
    shutil.move(file_name, "../../../html/Reports/"+str(user_id)+"_"+str(rep_id)+"/"+file_name)
