import pandas as pd 
import numpy as np
import cgi, os
import csv, shutil

form = cgi.FieldStorage()
Report = form.getvalue("Reportname")
userid = form.getvalue('user_id')


print ("Content-type: text/html \n\n")
output_path = "C:/LAPAM2019/DataLake/Cache/"+userid+"/"+Report+"/"+"OSP"

if not os.path.exists(output_path):
    print("This report does not contain OSP")
   

if os.path.exists(output_path):
    print("Report Contains OSP")


