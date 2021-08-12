# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 10:51:10 2021

@author: v.a.subhash.krishna
"""

import os, cgi, configparser
import json
import pandas as pd
from compare_reports_dendo import compare_reports_dendo

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
TEMPLATE_PATH = parser.get('Upload','templatepath')


def compare_reports_typo(base_typology_df, compare_typology_df):
    result_csv = []
    for index,row in base_typology_df.iterrows():
        compare_row = compare_typology_df[compare_typology_df['Typology'] == row['Typology']]
        if len(compare_row):
            count = row['Count']-compare_row['Count'].tolist()[0]
            if count > 0:
                each_row = [row['Typology'],row['Count']-compare_row['Count'].tolist()[0]]
            else:
                each_row = [row['Typology'],row['Count']]
        else:
            each_row = [row['Typology'],row['Count']]
        result_csv.append(each_row)
##    print(result_csv)
    return result_csv


def compare_reports_master(base_dendo_df,compare_dendo_df,template_json):
    result_csv = []
    for key,val in template_json.items():
        each_row = []
        header_list = list(val.keys())
        if key != 'Common Tags':
            type_base_df = base_dendo_df[base_dendo_df['Level3'] == key]
            type_compare_df = compare_dendo_df[compare_dendo_df['Level3'] == key]
            if len(type_base_df) and len(type_compare_df):
                for header in header_list:
                    base_header_df = type_base_df[type_base_df['Level4'] == header]
                    unique_values = list(base_header_df['Level5'].values)
                    # print(key,header)
                    compare_header_df = type_compare_df[type_compare_df['Level4'] == header]
                    if len(base_header_df) and len(compare_header_df):
                        for index,row in base_header_df.iterrows():
                            # print(row)
                            compare_row = compare_header_df[compare_header_df['Level5'] == row['Level5']]
                            if len(compare_row):
                                # print(compare_row)
                                each_row = [key,header,row['Level5'],row['Count'],list(compare_row['Count'].values)[0]]
                            else:
                                each_row = [key,header,row['Level5'],row['Count'],0]
                            result_csv.append(each_row)
                        compare_row = compare_header_df[~compare_header_df['Level5'].isin(unique_values)]
                        for index,row in compare_row.iterrows():
                            each_row = [key,header,row['Level5'],0,row['Count']]
                            result_csv.append(each_row)
                    elif len(base_header_df):
                        for index,row in base_header_df.iterrows():
                            each_row = [key,header,row['Level5'],row['Count'],0]
                            result_csv.append(each_row)
                    elif len(compare_header_df):
                        for index,row in compare_header_df.iterrows():
                            each_row = [key,header,row['Level5'],0,row['Count']]
                            result_csv.append(each_row)
                    else:
                        each_row = [key,header,'',0,0]
                        result_csv.append(each_row)
            elif len(type_base_df):
                for header in header_list:
                    base_header_df = type_base_df[type_base_df['Level4'] == header]
                    if len(base_header_df):
                        for index,row in base_header_df.iterrows():
                            each_row = [key,header,row['Level5'],row['Count'],0]
                            result_csv.append(each_row)
                    else:
                        each_row = [key,header,'',0,0]
                        result_csv.append(each_row)
            elif len(type_compare_df):
                for header in header_list:
                    compare_header_df = type_base_df[type_base_df['Level4'] == header]
                    if len(compare_header_df):
                        for index,row in compare_header_df.iterrows():
                            each_row = [key,header,row['Level5'],0,row['Count']]
                            result_csv.append(each_row)
                    else:
                        each_row = [key,header,'',0,0]
                        result_csv.append(each_row)
            else:
                for header in header_list:
                    each_row = [key,header,'',0,0]
                    result_csv.append(each_row)
        else:
            for header in header_list:
                base_header_df = base_dendo_df[base_dendo_df['Level4'] == header]
                unique_values = []
                compare_header_df = compare_dendo_df[compare_dendo_df['Level4'] == header]
                cols = list(base_header_df.columns)[:-2]
                if len(base_header_df) and len(compare_header_df):
                    base_group_df = base_header_df.groupby(cols)
                    compare_group_df = compare_header_df.groupby(cols)
                    for b_row in base_group_df:
                        unique_values.append(list(b_row[0]))
                        flag = 1
                        index = list(b_row[0])[-1]
                        for c_row in compare_group_df:
                            # print(c_row)
                            if b_row[0] == c_row[0]:
                                flag=0
                                each_row = [list(b_row[0])[3],header,index,list(b_row[1]['Count'].values)[0],list(c_row[1]['Count'].values)[0]]
                                break
                        if flag:
                            each_row = [list(b_row[0])[3],header,index,list(b_row[1]['Count'].values)[0],0]
                        result_csv.append(each_row)
                    for c_row in compare_group_df:
                        if list(c_row[0]) not in unique_values:
                            index = list(c_row[0])[-1]
                            each_row = [list(c_row[0])[3],header,index,0,list(c_row[1]['Count'].values)[0]]
                            result_csv.append(each_row)
                elif len(base_header_df):
                    base_group_df = base_header_df.groupby(cols)
                    for b_row in base_group_df:
                        index = list(b_row[0])[-1]
                        each_row = [list(b_row[0])[3],header,index,list(b_row[1]['Count'].values)[0],0]
                        result_csv.append(each_row)
                elif len(compare_header_df):
                    compare_group_df = compare_header_df.groupby(cols)
                    for c_row in compare_group_df:
                        index = list(c_row[0])[-1]
                        each_row = [list(c_row[0])[3],header,index,0,list(c_row[1]['Count'].values)[0]]
                        result_csv.append(each_row)
    return result_csv

if __name__ == '__main__':
    print("Content-type: text/html \n");	
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')
    log_type = form.getvalue('log_type')
    template_name = form.getvalue('template_name')
    base_name = form.getvalue('base_report')
    compare_name = form.getvalue('compare_report')
    comparison_reportname = form.getvalue('comparison_reportname')

##    userid = "44"
##    log_type = "TradeInsertion"
##    template_name = "TRD_Testtemp"
##    base_name = "murex_log_prod"
##    compare_name = "raboset1"
##    comparison_reportname = "report6"
    
    base_folder_name = userid+"_"+base_name
    compare_folder_name = userid+"_"+compare_name
    output_folder_name = userid+"_"+comparison_reportname
    template_path = TEMPLATE_PATH + '\\' + userid + '\\' + log_type
    # template_name = ''
    # template_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\template1\\'
    # template_json = json.load(open(template_path+'\\'+template_name+'.json'))
    if template_name:
        template_json = json.load(open(template_path+'\\'+template_name+'.json'))
    else:
        template_json = dict()
        patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
        if not os.path.exists(patterns_path):
            patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
        # patterns_path = 'C:\\Users\\v.a.subhash.krishna\\Downloads\\murex_log_parsing\\patterns.json'
        template_json = json.load(open(patterns_path))
        template_json.pop('internalId')
        template_json.pop('Contract Id')
        template_json.pop('Dendo_list')
        template_json.pop('events')
        # for key,value in patterns_json.items():
        #     if len(key.split('_'))>1:
        #         updated_key = ' '.join(key.split('_'))
        #     else:
        #         updated_key = key
        #     template_json[updated_key] = value
        template_json['Common Tags'] = template_json['common_tags']
        template_json.pop('common_tags')
    base_path = "../../../WEB-INF/classes/static/html/Reports/"+base_folder_name
    compare_path = "../../../WEB-INF/classes/static/html/Reports/"+compare_folder_name
    compare_output_path = "../../../WEB-INF/classes/static/html/Reports/"+output_folder_name
    # base_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\PattrnMing-Rabobnk_Output\\Output\\mxdev21_trade_xmls_set1'
    # compare_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\PattrnMing-Rabobnk_Output\\Output\\mxdev21_trade_xmls_set2'
    # compare_output_path = template_path
    base_dendo_df = pd.read_csv(base_path+'/IMP035_usage.csv')
    compare_dendo_df = pd.read_csv(compare_path+'/IMP035_usage.csv')
    cols = list(base_dendo_df.columns)
    if not os.path.exists(compare_output_path):
        os.mkdir(compare_output_path)
    result_master_csv = compare_reports_master(base_dendo_df,compare_dendo_df,template_json)
    final_master_df = pd.DataFrame(result_master_csv, columns = ['Typology','Header','Value','Base Report Count','Compare Report Count'])
    final_master_df.dropna(how='all',inplace=True)
    final_master_df.to_csv(compare_output_path+'/murex_master.csv', index=False, header=True)
    result_dendo_csv = compare_reports_dendo(base_dendo_df,compare_dendo_df,template_json)
    final_dendo_df = pd.DataFrame(result_dendo_csv, columns = cols)
    final_dendo_df.dropna(how='all',inplace=True)
    final_dendo_df.to_csv(compare_output_path+'/IMP035_usage.csv', index=False, header=True)
    download_dendo_df = pd.DataFrame(result_dendo_csv, columns = ['Category','Trade Family','Trade Group','Typology','Trade Characteristics','Value1','Value2','Count'])
    download_dendo_df.drop(columns=['Category','Value2'],inplace = True)
    download_dendo_df.dropna(how='all',inplace=True)
    with pd.ExcelWriter(compare_output_path+'/TradeEvents_Master.xlsx') as writer:
        download_dendo_df.to_excel(writer, sheet_name='Count', index=False, header=True)
        final_master_df.to_excel(writer, sheet_name='Master', index=False, header=True)
    base_typology_df = pd.read_csv(base_path+'/typology.csv')
    compare_typology_df = pd.read_csv(compare_path+'/typology.csv')
    result_typo_csv = compare_reports_typo(base_typology_df, compare_typology_df)
    final_typo_df = pd.DataFrame(result_typo_csv, columns = ['Typology','Count'])
    final_typo_df.to_csv(compare_output_path+'/typology.csv', index=False, header=True)
    # if not os.path.isdir(temp_path):
    #     os.makedirs (temp_path)
    # final_df.to_csv(temp_path+'/compare.csv', index=False, header=True)
    # print("Compare report created, Download report here")
