import re,os
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc,shutil
import configparser
from collections import Counter
from datetime import datetime

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

def observation(data,rep_id,user_id,imp_id):
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    query = """INSERT INTO recommendations (`REP_ID`, `USER_ID`, `IMP_ID`, `OBSERVATION`)
                VALUES (%s,%s,'%s','%s');"""
    cur.execute(query %(rep_id,user_id,imp_id,data))
    cur.commit()


#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
