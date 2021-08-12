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
import configparser
import cgi, os
import cgi, configparser, glob


def get_temp():
        arr = os.listdir(output_path)
        temp_names = []
        for i in arr:
                print(i.replace('.json', ''))
                
##                temp_name = i.replace(".json", "")
##                temp_names.append(temp_name)
##        x=','
##        x = x.join(temp_names)
##        print(x)

form = cgi.FieldStorage()
logtype = form.getvalue("logtype").strip()
##logtype = "TradeInsertion"

print ("Content-type: text/html \n\n")
output_path = "C:/LAPAM2019/DataLake/Templates2/44/"+logtype+"/";



if os.path.exists(output_path):
        get_temp()
else:
        print("No Data")
                
            



	
	
