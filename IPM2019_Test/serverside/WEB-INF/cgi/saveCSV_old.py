import pandas as pd 
import numpy as np
import cgi, os
import csv, shutil

form = cgi.FieldStorage()
##prj_name = form.getvalue("prj_name")
csv_list = form.getvalue("csv_list")
down_csv_list = form.getvalue("down_csv_list")
filename = form.getvalue("filename")
userid = form.getvalue('user_id')
test_name = form.getvalue('report_name')
folder_name=str(userid)+"_"+str(test_name)
tradeval = form.getvalue("tradename")

print ("Content-type: text/html \n\n")
output_path = '../../../WEB-INF/classes/static/html/Reports/'+folder_name
if not os.path.exists(output_path):
    os.mkdir(output_path)

 
with open('../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/'+filename+ '.csv', "w") as output:
    output.write(csv_list)

if filename.split('_')[0] == 'Delvy':
    shutil.copy('../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/'+filename+ '.csv', '../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/DeliveryWF_Rearrange.csv')
    shutil.copy('../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/DeliveryWF_Rearrange.csv', '../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/DeliveryWF_'+tradeval+'_Rearrange.csv')
else:
    #shutil.copy('../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/'+filename+ '.csv', '../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/TradeEvents_'+tradeval+'_Rearrange.csv')
    with open('../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/TradeEvents_'+tradeval+'_Rearrange.csv', "w") as down_output:
        down_output.write(down_csv_list)


