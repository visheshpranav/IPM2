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
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

# variable declaration
form = cgi.FieldStorage()
tab_arr = []
row_arr_list = form.getlist("row_list")
header_arr_list = form.getlist("header_list")
isIDCheck = form.getvalue("isIDCheck")
tablename = form.getvalue('tablename')
##row_arr_list = ['IMP30,P28~P29']
##header_arr_list = ['IMPERATIVE_ID,PATTERNS']
##tablename = "Mapping"
##isIDCheck = "false"
row_arr = row_arr_list[0].split(",")
header_arr = header_arr_list[0].split(",")

#insert values into User database table
def insert_values(con):
        row_i=0
        header_val = ""
        values = ""
        header_val = ', '.join('`{0}`'.format(hdr) for hdr in header_arr)
        values = ",".join('"{0}"'.format(val.replace('~',',')) for val in row_arr)
        
        query = 'INSERT INTO '+tablename+'('+header_val+') VALUES ('+html.unescape(values)+');'
        con.execute(query)
        ret = "success"       

# validate the given input value
def value_exists(con):
        isValidId = True
        if(isIDCheck == "true"):
                isValidId = checkIdExists(con)
                if(isValidId):
                        query = 'SELECT '+header_arr[0]+' from '+tablename+' where '+header_arr[1]+'="'+row_arr[1]+'";'
                        res = con.execute(query)
                        if len(con.fetchall()) == 0:
                                return True
                else:
                        return False
        else:
                query = 'SELECT '+header_arr[0]+' from '+tablename+' where '+header_arr[0]+'="'+row_arr[0]+'" and '+header_arr[1]+'="'+row_arr[1]+'";'
                res = con.execute(query)
                if len(con.fetchall()) == 0:
                        return True
                return False

def checkIdExists(con):
        query = 'SELECT '+header_arr[0]+' from '+tablename+' where '+header_arr[0]+'="'+row_arr[0]+'";'
        res = con.execute(query)
        if len(con.fetchall()) == 0:
                return True
        return False

# database connection
def create_connection():
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    if(value_exists(cur)):
                insert_values(cur)
                con.commit()
                print ("Success")
    else:
                print("FAP 1")

print ("Content-type: text/html \n");    
con = create_connection()
