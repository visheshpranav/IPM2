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
dat = form.getvalue("dateTime")

print ("Content-type: text/html \n\n")
output_path = '../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/'+tradeval+"_"+dat
output_path2 = '../../../WEB-INF/classes/static/html/Reports/'+folder_name

if not os.path.exists(output_path):
    os.mkdir(output_path)

with open(output_path+'/'+filename+ '.csv', "w") as output:
    output.write(csv_list)
download_df = pd.read_csv(output_path+'/'+filename+ '.csv',header = 0)
if filename.split('_')[0] == 'Delvy':
    download_master_df = pd.read_excel(output_path2+'/DeliverableWF_Master.xlsx',sheet_name=1)
    download_master_df = download_master_df.loc[download_master_df['Trade Typology'] == tradeval]
    with pd.ExcelWriter(output_path+'/DeliveryWF_'+tradeval+'_Rearrange.xlsx') as writer:
        download_df.to_excel(writer, sheet_name='Count', index=False, header=True)
        download_master_df.to_excel(writer, sheet_name='Master', index=False, header=True)
    # shutil.copy('../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/'+filename+ '.csv', '../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/DeliveryWF_Rearrange.csv')
    # shutil.copy('../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/DeliveryWF_Rearrange.csv', '../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/DeliveryWF_'+tradeval+'_Rearrange.csv')
else:
    #shutil.copy('../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/'+filename+ '.csv', '../../../WEB-INF/classes/static/html/Reports/'+folder_name+'/TradeEvents_'+tradeval+'_Rearrange.csv')
    with open(output_path+'/TradeEvents_'+tradeval+'_Rearrange.csv', "w") as down_output:
        down_output.write(down_csv_list)
    download_master_df = pd.read_excel(output_path2+'/TradeEvents_Master.xlsx',sheet_name=1)
    download_master_df = download_master_df.loc[download_master_df['Typology'] == tradeval]
    download_df = pd.read_csv(output_path+'/TradeEvents_'+tradeval+'_Rearrange.csv',header = 0)
    with pd.ExcelWriter(output_path+'/TradeEvents_'+tradeval+'_Rearrange.xlsx') as writer:
        download_df.to_excel(writer, sheet_name='Count', index=False, header=True)
        download_master_df.to_excel(writer, sheet_name='Master', index=False, header=True)

