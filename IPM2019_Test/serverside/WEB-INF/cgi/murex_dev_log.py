# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 17:15:34 2020

@author: v.a.subhash.krishna
"""

import xml.etree.ElementTree as ET
import itertools
import glob, json, copy
import pandas as pd
from datetime import datetime
import os, cgi, configparser, shutil
from report_merger import output_merger

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def recursive_csv_list(xml_file_path, master_df):
    
    patterns = json.load(open('C:\\LAPAM2019\\Config\\Deliver.json'))
    # patterns = json.load(open('C:\\Users\\v.a.subhash.krishna\\Downloads\\Murex files_old\\OUTPUT\\Deliver.json'))
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    new_row={}
    for key,val in patterns['Fields'].items():
        obj_list = root.findall(val)
        for obj in obj_list:
            # print(key,val, obj.text)
            new_row[key] = obj.text
    master_df=master_df.append(new_row,ignore_index=True)
    return master_df

def generate_dendo(master_df,output_path,test_name):
    # print(master_df.columns)
    dendo_list = []
    unique_typology_list = []
    if 'OSP_Contract_ID' in master_df.columns:
        dendo_master_df = master_df.drop(columns='OSP_Contract_ID')
    else:
        dendo_master_df = master_df
    unique_typology_df = master_df.groupby(['Trade Typology'])
    groupby_df = dendo_master_df.groupby(["Trade Family","Trade Group",'Trade Typology'])
    for df in unique_typology_df:
        unique_typology_list.append([df[0],len(df[1]['Contract ID'].unique())])
    for row in groupby_df:
        level4_df = row[1]
        # print(row[0])
        level4_df.drop(columns=["Trade Family","Trade Group",'Trade Typology'],inplace=True)
        # print(level4_df.columns)
        column_names = list(level4_df.columns)
        level4_df = level4_df.fillna('')
        column_names.remove('Contract ID')
        # print(column_names)
        for column in column_names:
            unique_level6 = level4_df[column].unique()
            if unique_level6[0] != '':
                for val_level6 in unique_level6:
                    count_df = level4_df[level4_df[column] == val_level6]
                    val_list = ['murex']
                    val_list.extend(row[0])
                    # print(len(count_df['internalId'].unique()))
                    val_list.extend([column, val_level6, len(count_df['Contract ID'].unique())])
                    # print(val_list)
                    dendo_list.append(val_list)
                    # print(val_list)
    dendo_df = pd.DataFrame(dendo_list, columns = ['Category','Level1','Level2','Level3','Level4','Level5','Count'])
    dendo_df.to_csv(output_path+'/IMP036_Delivery.csv', index=False, header=True)
    typology_df = pd.DataFrame(unique_typology_list,columns = ['Typology', 'Count'])
    typology_df.to_csv(output_path+'/typology.csv', index=False, header=True)
    download_df = pd.DataFrame(dendo_list, columns = ['Category',"Trade Family","Trade Group",'Trade Typology','Delivarable Characteristics','Value','Count'])
    # download_master_df = master_df.drop(columns='Category')
    download_df.drop(columns='Category',inplace = True)
    with pd.ExcelWriter(output_path+'//'+test_name+'_DeliverableWF_Master.xlsx') as writer:
        download_df.to_excel(writer, sheet_name='Count', index=False, header=True)
        dendo_master_df.to_excel(writer, sheet_name='Master', index=False, header=True)
        # break
    

if __name__ == '__main__':	
    print("Content-type: text/html \n");	
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')	
    test_name = form.getvalue('report_name')	
    old_report = form.getvalue('existing_report_name')
##    logtype = form.getvalue('logtype').split("\n")[0].strip()	
    # print(logtype)	
##    userid="44"	
##    test_name="testdelosp"	
    logtype="DeliverableMXML" 	
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\"+str(logtype)	
    file_path = dir_path + "\\*.xml"
    # file_path = "C:\\Users\\v.a.subhash.krishna\\Downloads\\Murex files_old\\DeliverablesMxml_15072020\\*.xml"	
    # print(file_path)	
    files = glob.glob(file_path)	
##    print(files)	
    val = 0	
    csv_list = []	
    status_count = {}
    master_df = pd.DataFrame(columns = ["Trade Family","Trade Group","Trade Typology","Contract ID","Delivarable Primary system",
                                        "Portfolio","Flow type(Send or receive)","Flow amount",
                                        "Instrument","To be Netted",
                                        "Flow currency","Position Type(nostro or Vostro)",
                                        "Counterparty name","Flow Settlement Date","Flow Value Date"])
    
    for file in files:
        master_df = recursive_csv_list(file, master_df)	
    folder_name=userid+"_"+test_name
    old_folder = userid+"_"+old_report
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name+"/"
    old_report_path = "../../../WEB-INF/classes/static/html/Reports/"+old_folder+'/'
    if not os.path.exists(output_path):	
        os.mkdir(output_path)	
    # output_path = 'C:\\Users\\v.a.subhash.krishna\\Downloads\\Murex files_old\\OUTPUT'
    generate_dendo(master_df,output_path,test_name)
##    master_df = master_df.drop_duplicates()
    master_df.to_csv(output_path+'\\Del_master.csv', index=False)
    if old_report:
        file_list = ['IMP036_Delivery.csv','typology.csv','Del_master.csv']
        output_merger(file_list, output_path, old_report_path, logtype)
        master_df = pd.read_csv(output_path+'\\Del_master.csv')
        download_df = pd.read_csv(output_path+'/IMP036_Delivery.csv')
        download_df.rename(columns={'Level1':'Trade Family','Level2':'Trade Group',
                                           'Level3':'Typology','Level4':'Delivarable Characteristics',
                                           'Level5':'Value'},inplace=True)
        download_df.drop(columns='Category',inplace = True)
        dendo_master_df = master_df.drop(columns='OSP_Contract_ID')
        with pd.ExcelWriter(output_path+'//'+test_name+'_DeliverableWF_Master.xlsx') as writer:
            download_df.to_excel(writer, sheet_name='Count', index=False, header=True)
            dendo_master_df.to_excel(writer, sheet_name='Master', index=False, header=True)
    # df_gen(csv_list, output_path)
    # my_df_new = pd.DataFrame(csv_list, columns = ['Category','Level1','Level2','Level3','Level4','Level5','Level6','Count'])	
    # filename = 'IMP035_usage.csv'	
    # my_df_new.to_csv(filename, index=False, header=True)
    # shutil.move(filename, output_path+"/"+filename)
    # shutil.copy(output_path+"/"+filename, output_path+"/TradeInsertionEvents.csv")
