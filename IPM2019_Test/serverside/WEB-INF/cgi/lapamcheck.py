#######################################################################

########################################################################
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc
import configparser
import os,shutil

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
DATA_PATH = parser.get('Upload','Oflpath')

''' declare variables '''
form = cgi.FieldStorage()
user_id = form.getvalue('user_id')
reportname = form.getvalue('reportname')

##user_id = "44"
##reportname = "dealtest24"

dir_path = DATA_PATH + "Cache\\" + user_id + "\\" + reportname+ '\\' +"TradeInsertion"

if os.path.exists(dir_path):
        print(dir_path)
        print("true")

                
