#######################################################################
#Application : LAPAM
#Desc: Insert User
#Created by : Vinotha
#Modified by : Rajkumar
#Date of Modification:16/8/2018
#Reason for modification:Column name change due to DB re-design
########################################################################
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc, html
import configparser
from datetime import datetime

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAME = parser.get('DSN','DSN_NAME')

# variable declaration
form = cgi.FieldStorage()
tab_arr = []
row_arr_list = form.getlist("row_list")
header_arr_list = form.getlist("header_list")
tablename = form.getvalue('tablename')
##row_arr_list = ['IMP001,P1~P2,csv,None']
##header_arr_list = ['IMPERATIVE_ID,PATTERNS,OUTCOME,LOGIC']
##tablename = "Mapping"
row_arr = row_arr_list[0].split(",")
header_arr = header_arr_list[0].split(",")

#insert values into User database table
def update_values(con):
        row_i=0
        update_str = ""
        for val in range(len(header_arr)):
                if val == (len(header_arr)-1):
                        update_str += header_arr[val] +"='"+html.unescape(row_arr[val].replace('~',',')) +"'"
                else:
                        if not val == 0:
                                update_str += header_arr[val] +"='"+html.unescape(row_arr[val].replace('~',',')) +"', "
        query = 'update '+tablename+' set '+update_str+' WHERE '+header_arr[0]+' = "'+row_arr[0]+'";'
        print(query)
        con.execute(query)
        ret = "success"

# validate the given input value
def value_exists(con):
        query = 'SELECT '+header_arr[0]+' from '+tablename+' where '+header_arr[1]+'="'+row_arr[1]+'" and '+header_arr[0]+'!="'+row_arr[0]+'";'
        res = con.execute(query)
        if len(con.fetchall()) == 0:
                return True
        return False

# database connection
def create_connection():
    con = pyodbc.connect("DSN="+DSN_NAME)
    cur = con.cursor()
    if(value_exists(cur)):
                update_values(cur)
                con.commit()
                print ("Success")
    else:
                print("FAP 1")

print ("Content-type: text/html \n");    
con = create_connection()
