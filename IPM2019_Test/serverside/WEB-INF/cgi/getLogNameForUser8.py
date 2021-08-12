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
import re
import configparser
from datetime import date
import datetime

parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

form = cgi.FieldStorage()
user_name = form.getvalue("user_name").strip()
Currentpass = form.getvalue("Currentpass").strip()
Npass = form.getvalue("Npass").strip()
##user_name = "Murex"
##Currentpass = "Murex@123"
##Npass = "takle"
##userid = "44"
#fetch test values from quaifier table
def get_values(con):
        query = 'SELECT PASSWORD FROM lapam2019.user_info WHERE USER_NAME ="'+user_name+'";'
        con.execute(query)
        res = con.fetchall()
        return res

def updatepass():
        db1 = pyodbc.connect("DSN="+DSN_NAMEE)
        cur = db1.cursor()
        query1 = 'SELECT user_id FROM lapam2019.user_info WHERE USER_NAME ="'+user_name+'";'
        cur.execute(query1)
        res = cur.fetchall()
        ter = ' '.join(map(str, res))
        s1=re.sub("[',()]","",ter)
        query = 'UPDATE lapam2019.user_info SET PASSWORD = "'+Npass+'"  WHERE user_id="'+s1+'" and user_name="'+user_name+'";'
        cur.execute(query)
        query2 = 'UPDATE lapam2019.user_info SET PASSWORDDATE = "'+str(date.today())+'"  WHERE user_id="'+s1+'" and user_name="'+user_name+'";'
        cur.execute(query2)
        db1.commit()
        print("Password changed sucessfully")

def checkpass():
        db1 = pyodbc.connect("DSN="+DSN_NAMEE)
        cur = db1.cursor()
        query = 'SELECT PASSHISTONE,PASSHISTTWO,PASSWORD FROM lapam2019.user_info WHERE USER_NAME ="'+user_name+'";'
        cur.execute(query)
        res = cur.fetchall()
        listToStr = ' '.join(map(str, res))
        s1=re.sub("[',()]","",listToStr)
        if Npass in s1:
                print("You cant! use the same password which was used last times")
##        if any(Npass in s for s in res):
##                print("you cant use the same password which was used last time")
        else:
                query1 = 'SELECT user_id FROM lapam2019.user_info WHERE USER_NAME ="'+user_name+'";'
                cur.execute(query1)
                res = cur.fetchall()
                ter = ' '.join(map(str, res))
                s1=re.sub("[',()]","",ter)
                query = 'SELECT PASSHISTONE FROM lapam2019.user_info WHERE USER_NAME ="'+user_name+'";'
                cur.execute(query)
                res = cur.fetchall()
                ter = ' '.join(map(str, res))
                s2=re.sub("[',()]","",ter)
                query3 = 'UPDATE lapam2019.user_info SET PASSHISTTWO = "'+s2+'"  WHERE user_id="'+s1+'" and user_name="'+user_name+'";'
                cur.execute(query3)
                query4 = 'SELECT PASSWORD FROM lapam2019.user_info WHERE USER_NAME ="'+user_name+'";'
                cur.execute(query4)
                res = cur.fetchall()
                ter = ' '.join(map(str, res))
                s3=re.sub("[',()]","",ter)
                query3 = 'UPDATE lapam2019.user_info SET PASSHISTONE = "'+s3+'"  WHERE user_id="'+s1+'" and user_name="'+user_name+'";'
                cur.execute(query3)
                db1.commit()
                updatepass()        
        
     

#database connection
def create_connection():
	db1 = pyodbc.connect("DSN="+DSN_NAMEE)
	cur = db1.cursor()
	ret = get_values(cur)
	return ret


print ("Content-type: text/html \n\n");
ret = create_connection()
listToStr = ' '.join(map(str, ret))
s1=re.sub("[',()]","",listToStr)
if(s1.strip()!=Currentpass):
        print("Current password for the user is wrong! kindly check it")
else:
        checkpass()
##        updatepass()
##        print("Password changed sucessfully")
	
