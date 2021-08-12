#######################################################################
#Application : LAPAM
#Build : 2019
#Desc: delete value from table
#Created by: Rajkumar
#Date of Modification:8/2/2018
########################################################################
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc
import configparser

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAME = parser.get('DSN','DSN_NAME')

''' declare variables '''
form = cgi.FieldStorage()
tablename = form.getvalue('tablename')
fieldname = form.getvalue('fieldname')
id_val = form.getvalue('id_val')

''' update user details in databse '''
def delete_value(con):
        i = 0
        query = 'delete from '+tablename+' WHERE '+fieldname+' = "'+id_val+'";'
        con.execute(query)
        ret = "success"
        
''' database connection '''
def create_connection():
        con = pyodbc.connect("DSN="+DSN_NAME)
        cur = con.cursor()
        delete_value(cur)
        con.commit()
        print ("Success");

print ("Content-type: text/html \n\n");
con = create_connection()
