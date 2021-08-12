# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:35:27 2021

@author: v.a.subhash.krishna
"""

import pandas as pd
import string,cgi, glob, os
import configparser, copy, json
# from datetime import datetime

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')

def get_dict(file, day_json, month_json, week_json, master_df):
    if file.endswith(".csv"):
        datamart_df = pd.read_csv(file)
    # data = pd.read_csv(file_path)
    else:
        datamart_df = pd.read_excel(file)
    master_df = pd.concat([master_df,datamart_df])
    datamart_df = datamart_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    #data = pd.read_csv("dendo_new.csv")
    req_columns = ['PROCESSING SCRIPTS', 'JOB_DATE', 'ENTRY_TIME', 'EXIT_TIME',
                   'REPORT_TABLE', 'FEEDER', 'BATCH OF FEEDER', 'EXTRACTION',
                   'BATCH OF EXTRACTION']
    
    datamart_df = datamart_df[req_columns]
    datamart_df['JOB_DATE'] = pd.to_datetime(datamart_df['JOB_DATE'])
    datamart_df['JOB_DATE'] = datamart_df['JOB_DATE'].dt.strftime('%Y-%m-%d')
    datamart_df['ENTRY_TIME'] = pd.to_datetime(datamart_df['ENTRY_TIME'])
    datamart_df['ENTRY_TIME'] = datamart_df['ENTRY_TIME'].dt.strftime('%H:%M:%S')
    datamart_df['EXIT_TIME'] = pd.to_datetime(datamart_df['EXIT_TIME'])
    datamart_df['EXIT_TIME'] = datamart_df['EXIT_TIME'].dt.strftime('%H:%M:%S')
    # print(datamart_df['JOB_DATE'].dt.strftime('%Y-%m-%d'))
    # print(pd.to_datetime(datamart_df['JOB_DATE']))
    # datamart_df['EXTRACTION'].str.strip().fillna('-',inplace=True)
    datamart_df.replace(to_replace=r'^ *$', value='-', regex=True,inplace=True)
    # print(datamart_df['EXTRACTION'])
    datamart_df.fillna('-',inplace=True)
    for index, row in datamart_df.iterrows():
        val_list = {}
        val_list['type'] = row['PROCESSING SCRIPTS']+'|'+row['REPORT_TABLE']
        val_list['task']=(row['FEEDER']+'|'+row['BATCH OF FEEDER']+'|'+row['EXTRACTION']+'|'+row['BATCH OF EXTRACTION'])
        day_val = copy.deepcopy(val_list)
        month_val = copy.deepcopy(val_list)
        week_val = copy.deepcopy(val_list)
        day_val['startTime'] = row['ENTRY_TIME']
        day_val['endTime'] = row['EXIT_TIME']
        day_val['details'] = row['JOB_DATE']
        day_json.append(day_val)
        week_val['startTime'] = row['JOB_DATE']
        week_val['endTime'] = row['JOB_DATE']
        week_val['details'] = f'starttime {row["ENTRY_TIME"]} endtime {row["EXIT_TIME"]}'
        week_json.append(week_val)
        month_val['startTime'] = row['JOB_DATE']
        month_val['endTime'] = row['JOB_DATE']
        month_val['details'] = f'starttime {row["ENTRY_TIME"]} endtime {row["EXIT_TIME"]}'
        month_json.append(month_val)
        # print(f'starttime {row["ENTRY_TIME"]} endtime {row["EXIT_TIME"]}')
        # break
        # final_list.append(val_list)
    return day_json, month_json, week_json, master_df

if __name__ == '__main__':	
    print("Content-type: text/html \n");	
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')	
    test_name = form.getvalue('report_name')
##    userid = "44"	
##    test_name = "fdfsfsdfsjdhasdj"
    # logtype = form.getvalue('logtype').split("\n")[0].strip()
    logtype="DATAMART"
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\"+str(logtype)	
    file_path = dir_path + "\\*"
    # file_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_Input\\Datamart_R_28042021_100k.csv'
    files = glob.glob(file_path)
    final_list = []
    day_json = []
    month_json = []
    week_json = []
    master_df = pd.DataFrame()
    
    for file in files:
##        print(file)
        day_json, month_json, week_json, master_df = get_dict(file, day_json, month_json, week_json, master_df)

    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name	
    # output_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_output\\'
    
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    json.dump(day_json,open(output_path + '\\Day.json','w'))
    json.dump(month_json,open(output_path + '\\Month.json','w'))
    json.dump(week_json,open(output_path + '\\Week.json','w'))
    # df = pd.DataFrame(final_list,columns=['name', 'starttime', 'endtime', 'feedervalue'])
    # df.to_csv(output_path+'//datamart_gant_chart.csv',index=False, header=True)
    master_df.to_csv(output_path+'//datamart_gant_chart_download.csv',index=False, header=True)
