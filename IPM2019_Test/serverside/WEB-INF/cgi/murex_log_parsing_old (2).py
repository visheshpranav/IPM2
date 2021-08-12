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

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def recursive_csv_list(xml_file_path, master_df):
    
    patterns = json.load(open('C:\\LAPAM2019\\Config\\patterns.json'))
    # patterns = json.load(open('C:\\Users\\v.a.subhash.krishna\\Downloads\\murex_log_parsing\\patterns.json'))
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    root_tag = root.tag.split('}')[-1]
    parent_map = [[p,c] for p in root.iter() for c in p]
    for child in root.findall('.//tradeFamily'):
        tag_list = ['Trade']
        tag_list.append(child.text)
        parent = [val[0] for val in parent_map if val[1] == child][0]
        tag_list.append(parent.findall('.//tradeGroup')[0].text)
        typology = parent.findall('.//typology')[0].text
        tag_list.append(typology)
        pattern_keys = [val.replace('_',' ') for val in patterns.keys()]
        for val in patterns['events']:
            obj_list = root.findall(patterns['events'][val])
            internal_id = root.findall(patterns['internalId'])
            for obj in obj_list:
                new_row={'Category':tag_list[0],'tradeFamily':tag_list[1],
                         'tradeGroup':tag_list[2],'typology':tag_list[3],'Trade Characteristics':'Events'}
                new_row[obj.tag] = val
                new_row[internal_id[0].tag] = internal_id[0].text
                master_df=master_df.append(new_row,ignore_index=True)

        new_row={'Category':tag_list[0],'tradeFamily':tag_list[1],
                 'tradeGroup':tag_list[2],'typology':tag_list[3],'Trade Characteristics':'Trade Characteristics'}
        
        for val in patterns['common_tags']:
            obj_list = root.findall(patterns['common_tags'][val])
            # obj_list = root.findall(val)
            for obj in obj_list:
                new_row[val] = obj.text
                break
        if typology in pattern_keys:
            key = typology.replace(' ','_')
        else:
            master_df=master_df.append(new_row,ignore_index=True)
            continue
        for val in patterns[key]:
            obj_list = root.findall(patterns[key][val])
            # obj_list = root.findall(val)
            for obj in obj_list:
                if obj.tag == 'maturity':
                    maturity_date = datetime.strptime(obj.text,'%Y%m%d')
                    present_date = datetime.now()
                    difference = maturity_date - present_date
                    difference = int(difference.days/365)
                    if difference < 1:
                        new_row['Maturity Status'] = 'Short term'
                        # tag_list_1.append('physicalStatus')
                    elif difference > 1 and difference <= 5:
                        new_row['Maturity Status'] = 'Medium term'
                        # tag_list_1.append('physicalStatus')    
                    else:
                        new_row['Maturity Status'] = 'Long term'
                        # tag_list_1.append('physicalStatus')
                        
                
                else:
                    new_row[val] = obj.text
                break
        master_df=master_df.append(new_row,ignore_index=True)
    return master_df

def generate_dendo(master_df,output_path):
    dendo_master_df = master_df[['Category','tradeFamily','tradeGroup','typology','Trade Characteristics',
                                       'lastContractEventReference','Counterparty',
                                       'Trade Status','Portfolio','Internal/External',
                                       'Maturity Status','Nominal','Instrument2',
                                       'Expiry','tradeInternalId','ContractId']]
    dendo_list = []
    unique_typology_list = []
    groupby_df = dendo_master_df.groupby(['Category','tradeFamily','tradeGroup','typology','Trade Characteristics'])
    # print(groupby_df)
    unique_typology_df = dendo_master_df.groupby('typology')
    for df in unique_typology_df:
        unique_typology_list.append([df[0],len(df[1]['tradeInternalId'].unique())])
        # print(df[0],len(df[1]['tradeInternalId'].unique()))
    for row in groupby_df:
        level4_df = row[1]
        # print(row[0])
        level4_df.drop(columns=['Category','tradeFamily','tradeGroup','typology','Trade Characteristics'],inplace=True)
        # print(level4_df.columns)
        column_names = list(level4_df.columns)
        level4_df = level4_df.fillna('')
        column_names.remove('tradeInternalId')
        column_names.remove('ContractId')
        # print(column_names)
        for column in column_names:
            unique_level6 = level4_df[column].unique()
            if unique_level6[0] != '':
                for val_level6 in unique_level6:
                    count_df = level4_df[level4_df[column] == val_level6]
                    # print(count_df)
                    val_list = list(row[0])
                    if val_list[-1] == 'Trade Characteristics':
                        val_list.pop(-1)
                        val_list.extend([column, val_level6, '', len(count_df['ContractId'].unique())])
                        # print(count_df['tradeInternalId'])
                    else:                    
                        val_list.extend([column, val_level6, len(count_df['tradeInternalId'])])
                    # print(val_list)
                    dendo_list.append(val_list)
    dendo_df = pd.DataFrame(dendo_list, columns = ['Category','Level1','Level2','Level3','Level4','Level5','Level6','Count'])
    dendo_df.to_csv(output_path+'/IMP035_usage.csv', index=False, header=True)
    typology_df = pd.DataFrame(unique_typology_list,columns = ['Typology', 'Count'])
    typology_df.to_csv(output_path+'/typology.csv', index=False, header=True)
    download_df = pd.DataFrame(dendo_list, columns = ['Category','tradeFamily','tradeGroup','typology','Trade Characteristics','Value1','Value2','Count'])
    download_master_df = master_df.drop(columns='Category')
    download_df.drop(columns='Category',inplace = True)
    with pd.ExcelWriter(output_path+'/TradeEvents_Master.xlsx') as writer:
        download_df.to_excel(writer, sheet_name='Count', index=False, header=True)
        download_master_df.to_excel(writer, sheet_name='Master', index=False, header=True)
        # break
    

if __name__ == '__main__':	
    print("Content-type: text/html \n");	
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')	
    test_name = form.getvalue('report_name')	
    logtype = form.getvalue('logtype').split("\n")[0].strip()	
    # print(logtype)	
##    userid="44"	
##    test_name="nov10_12"	
##    logtype="Trade"	
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\"+str(logtype)	
    file_path = dir_path + "\\*.xml"
    # file_path = "C:\\Users\\v.a.subhash.krishna\\Documents\\RE_223_MxmlTrades\\RE_223_MxmlTrades\\*.xml"	
    # print(file_path)	
    files = glob.glob(file_path)	
##    print(files)	
    val = 0	
    csv_list = []	
    status_count = {}
    master_df = pd.DataFrame(columns=['Category','tradeFamily','tradeGroup','typology','Trade Characteristics'])	
    for file in files:
        master_df = recursive_csv_list(file, master_df)	
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name	
    # output_path = "C:\\Users\\v.a.subhash.krishna\\Documents\\RE_223_MxmlTrades"
    if not os.path.exists(output_path):	
        os.mkdir(output_path)	
    
    # output_path = 'C:\\Users\\v.a.subhash.krishna\\Documents\\RE_223_MxmlTrades'
    generate_dendo(master_df,output_path)
    master_df.to_csv(output_path+'\\murex_master.csv', index=False)
    	
    # df_gen(csv_list, output_path)
    # my_df_new = pd.DataFrame(csv_list, columns = ['Category','Level1','Level2','Level3','Level4','Level5','Level6','Count'])	
    # filename = 'IMP035_usage.csv'	
    # my_df_new.to_csv(filename, index=False, header=True)
    # shutil.move(filename, output_path+"/"+filename)
    # shutil.copy(output_path+"/"+filename, output_path+"/TradeInsertionEvents.csv")
