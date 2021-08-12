#######################################################################
#Application : CITI
#Build : v1
#Desc: Upload the log 
#Created by : Rajkumar
#Modified by: Rajkumar
#Date of Modification:23/1/2019
########################################################################
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc, html
import configparser

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

''' declare variables '''
form = cgi.FieldStorage()
#tablename = form.getvalue('tablename')
tablename = "report_info"

#get values from database table
def get_values(con, header_str):
        query = "select "+', '.join([str(x) for x in header_str])+" from "+tablename+" where user_id=44;"
        con.execute(query)
        res = con.fetchall()
        return res

#get header values from database
def get_headervalues(con):
        query = "SELECT column_name FROM information_schema.columns WHERE table_schema = 'LAPAM2019' AND table_name = '"+tablename+"';"
        con.execute(query)
        res = con.fetchall()
        return res

# database connection
def create_connection():
	con = pyodbc.connect("DSN="+DSN_NAMEE)
	cur = con.cursor()
	return cur

con = create_connection()
head_ret = get_headervalues(con)
header_str=[]
header_strval=[]
print ("Content-type: text/html \n\n");
for header_i in list(head_ret):
        header_strval.append('`' + header_i[0] + '`')
        header_str.append("CONCAT('`', "+header_i[0]+", '`')")
ret = get_values(con, header_str)
ret = list(ret)
print(header_strval)
for val in ret:
        print(val)
        htmlchar_str = str(val).split(",")
        escapedchar=[]
        for htmlstr in htmlchar_str:
                escapedchar.append(htmlstr)
        #print(escapedchar)
##        nonhtmlchar = ','.join(html.escape(htmlchar_str))
##        print(str(nonhtmlchar))
