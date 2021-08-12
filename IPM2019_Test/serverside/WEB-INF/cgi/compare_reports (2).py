# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 17:15:34 2020

@author: v.a.subhash.krishna
"""

import xml.etree.ElementTree as ET
import glob, json, math
import pandas as pd
from datetime import datetime
import os, cgi, configparser
from report_merger import output_merger

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def recursive_csv_list(xml_file_path, master_df):
    patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
    if not os.path.exists(patterns_path):
        patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
    patterns = json.load(open(patterns_path))
    # patterns = json.load(open('C:\\Users\\v.a.subhash.krishna\\Downloads\\murex_log_parsing\\patterns.json'))
    try:
        tree = ET.parse(xml_file_path)
    except:
        return master_df
##    print(tree)
    try:
        root = tree.getroot()
        # root_tag = root.tag.split('}')[-1]
        parent_map = [[p,c] for p in root.iter() for c in p]
        for child in root.findall('.//tradeFamily'):
            tag_list = ['Trade']
            tag_list.append(child.text)
            parent = [val[0] for val in parent_map if val[1] == child][0]
            tag_list.append(parent.findall('.//tradeGroup')[0].text)
            typology = parent.findall('.//typology')[0].text
            # print(typology)
            # if typology == 'Spot':
            #     print(xml_file_path)
            tag_list.append(typology)
            pattern_keys = list(patterns.keys())
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
            # key = typology.replace(' ','_')
            if typology not in pattern_keys:
                patterns[typology] = {}
                for val in patterns['Contract Id']:
                    obj_list = root.findall(val)
                    if obj_list:
                        patterns[typology]['Contract Id'] = val
                # master_df=master_df.append(new_row,ignore_index=True)
                # continue
            for val in patterns[typology]:
                obj_list = root.findall(patterns[typology][val])
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
            break
        json.dump(patterns, open(patterns_path,'w'))
    except Exception as e:
        print(e)
##    print(master_df)
    return master_df

def generate_dendo(master_df,output_path,dendo_keys,test_name,report_type):
    if report_type == 'Compare':
        test_name = test_name + '_compare'
    dendo_master_df = master_df[dendo_keys]
    dendo_list = []
    unique_typology_list = []
    groupby_df = dendo_master_df.groupby(['Category','tradeFamily','tradeGroup','typology','Trade Characteristics'])
    # print(groupby_df)
    unique_typology_df = dendo_master_df.groupby('typology')
    for df in unique_typology_df:
        cid_list = df[1]['Contract Id'].unique()
        cid_list = [value if value else 'nan' for value in cid_list]
        cid_list = [value for value in cid_list if not math.isnan(float(value))]
        unique_typology_list.append([df[0],len(cid_list)])
        # print(df[0],len(df[1]['tradeInternalId'].unique()))
    for row in groupby_df:
        level4_df = row[1]
        # print(row[0])
        level4_df.drop(columns=['Category','tradeFamily','tradeGroup','typology','Trade Characteristics'],inplace=True)
        # print(level4_df.columns)
        column_names = list(level4_df.columns)
        level4_df = level4_df.fillna('')
        if "tradeInternalId" in column_names :
            column_names.remove('tradeInternalId')
        column_names.remove('Contract Id')
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
                        val_list.extend([column, val_level6, '', len(count_df['Contract Id'].unique())])
                        # print(count_df['tradeInternalId'])
                    else:                    
                        val_list.extend([column, val_level6, len(count_df['tradeInternalId'].unique())])
                    # print(val_list)
                    dendo_list.append(val_list)
    dendo_df = pd.DataFrame(dendo_list, columns = ['Category','Level1','Level2','Level3','Level4','Level5','Level6','Count'])
    dendo_df.to_csv(output_path+'/IMP035_usage.csv', index=False, header=True)
    typology_df = pd.DataFrame(unique_typology_list,columns = ['Typology', 'Count'])
    typology_df.to_csv(output_path+'/typology.csv', index=False, header=True)
    download_df = pd.DataFrame(dendo_list, columns = ['Category','Trade Family','Trade Group','Typology','Trade Characteristics','Value1','Value2','Count'])
    download_master_df = master_df.drop(columns='Category')
    download_master_df.rename(columns={'tradeFamily':'Trade Family','tradeGroup':'Trade Group',
                                       'typology':'Typology','lastContractEventReference':'Last Contract Event Reference',
                                       'tradeInternalId':'Trade Internal Id'},inplace=True)
    download_df.drop(columns='Category',inplace = True)
    with pd.ExcelWriter(output_path+'/'+test_name+'_TradeEvents.xlsx') as writer:
        download_df.to_excel(writer, sheet_name='Count', index=False, header=True)
        download_master_df.to_excel(writer, sheet_name='Master', index=False, header=True)
        # break
    

if __name__ == '__main__':	
    print("Content-type: text/html \n");	
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id').strip()
    test_name = form.getvalue('report_name').strip()
    logtype = form.getvalue('logtype').split("\n")[0].strip()
    old_report = form.getvalue('existing_report_name').strip()
    # print(logtype)	
##    userid="44"	
##    test_name="test_trade41"	
##    logtype="TradeInsertion"
##    old_report =""
##    print(userid,test_name,logtype,old_report)
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
##        print(file)
        master_df = recursive_csv_list(file, master_df)	
    folder_name=userid+"_"+test_name
    old_folder = userid+"_"+old_report
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    old_report_path = "../../../WEB-INF/classes/static/html/Reports/"+old_folder
    # output_path = "C:\\Users\\v.a.subhash.krishna\\Documents\\RE_223_MxmlTrades"
    if not os.path.exists(output_path):	
        os.mkdir(output_path)	
    
    patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
    if not os.path.exists(patterns_path):
        patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
    # patterns = json.load(open('C:\\Users\\v.a.subhash.krishna\\Downloads\\murex_log_parsing\\patterns.json'))
##    print(patterns_path)
    patterns = json.load(open(patterns_path))
##    print(master_df.columns)
    dendo_keys = [ val for val in patterns['Dendo_list'] if val in master_df.columns]
##    print(userid,test_name,logtype,old_report)
    # output_path = 'C:\\Users\\v.a.subhash.krishna\\Documents\\RE_223_MxmlTrades'
    
    generate_dendo(master_df,output_path,dendo_keys,test_name,'normal')
    master_df.drop_duplicates(inplace = True)
    master_df.to_csv(output_path+'\\murex_master.csv', index=False)
    if old_report:
        file_list = ['IMP035_usage.csv','typology.csv','murex_master.csv']
        output_merger(file_list, output_path, old_report_path, logtype)
        master_df = pd.read_csv(output_path+'\\murex_master.csv')
        download_df = pd.read_csv(output_path+'/IMP035_usage.csv')
        download_df.rename(columns={'Level1':'Trade Family','Level2':'Trade Group',
                                           'Level3':'Typology','Level4':'Trade Characteristics',
                                           'Level5':'Value1','Level6':'Value2'},inplace=True)
        download_master_df = master_df.drop(columns='Category')
        download_master_df.rename(columns={'tradeFamily':'Trade Family','tradeGroup':'Trade Group',
                                           'typology':'Typology','lastContractEventReference':'Last Contract Event Reference',
                                           'tradeInternalId':'Trade Internal Id'},inplace=True)
        download_df.drop(columns='Category',inplace = True)
        with pd.ExcelWriter(output_path+'/'+test_name+'_TradeEvents.xlsx') as writer:
            download_df.to_excel(writer, sheet_name='Count', index=False, header=True)
            download_master_df.to_excel(writer, sheet_name='Master', index=False, header=True)
##    print(userid,test_name,logtype,old_report)
    # df_gen(csv_list, output_path)
    # my_df_new = pd.DataFrame(csv_list, columns = ['Category','Level1','Level2','Level3','Level4','Level5','Level6','Count'])	
    # filename = 'IMP035_usage.csv'	
    # my_df_new.to_csv(filename, index=False, header=True)
    # shutil.move(filename, output_path+"/"+filename)
    # shutil.copy(output_path+"/"+filename, output_path+"/TradeInsertionEvents.csv")
