

import os, shutil, cgi, configparser
import json, copy

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
TEMPLATE_PATH = parser.get('Upload','templatepath2')

if __name__ == '__main__':	
    print("Content-type: text/html \n")
    form = cgi.FieldStorage()		
    logtype = form.getvalue('log_type')
    temname = form.getvalue('template_name') + ".json"
    userid = "44"	
##    logtype = "TradeInsertion"
##    temname = "TRD_sub_test1"+ ".json"
    final_list = []
    template_path = TEMPLATE_PATH + str(userid) + '\\' + logtype + '\\' + temname
    if os.path.exists(template_path):
        os.remove(template_path)
        print("Template deleted")
