# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 10:51:10 2021

@author: v.a.subhash.krishna
"""

import os, cgi, configparser
import json
import pandas as pd

#fetch the upload path from config	
# parser = configparser.ConfigParser() 	
# parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
# TEMPLATE_PATH = parser.get('Upload','templatepath')

def compare_reports_dendo(base_dendo_df,compare_dendo_df,template_json):
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
                    # unique_values = list(base_header_df['Level5'].values)
                    # print(key,header)
                    compare_header_df = type_compare_df[type_compare_df['Level4'] == header]
                    if len(base_header_df) and len(compare_header_df):
                        for index,row in base_header_df.iterrows():
                            # print(row)
                            compare_row = compare_header_df[compare_header_df['Level5'] == row['Level5']]
                            if len(compare_row):
                                # print(compare_row)
                                row['Count'] = row['Count']-list(compare_row['Count'].values)[0]
                                if row['Count'] > 0:
                                    each_row = list(row)
                            else:
                                each_row = list(row)
                            result_csv.append(each_row)
                    elif len(base_header_df):
                        for index,row in base_header_df.iterrows():
                            each_row = list(row)
                            result_csv.append(each_row)
            elif len(type_base_df):
                for header in header_list:
                    base_header_df = type_base_df[type_base_df['Level4'] == header]
                    if len(base_header_df):
                        for index,row in base_header_df.iterrows():
                            each_row = list(row)
                            result_csv.append(each_row)
                    # else:
                    #     each_row = [key,header,'',0,0]
                    #     result_csv.append(each_row)
        else:
            # print('entered')
            for header in header_list:
                # print(header)
                base_header_df = base_dendo_df[base_dendo_df['Level4'] == header]
                cols = list(base_header_df.columns)[:-2]
                # print(cols)
                # unique_values = list(base_header_df['Level5'].values)
                compare_header_df = compare_dendo_df[compare_dendo_df['Level4'] == header]
                if len(base_header_df) and len(compare_header_df):
                    # print(cols)
                    base_group_df = base_header_df.groupby(cols)
                    compare_group_df = compare_header_df.groupby(cols)
                    # print(compare_group_df.first())
                    
                    for b_row in base_group_df:
                        flag = 1
                        for c_row in compare_group_df:
                            # print(c_row)
                            if b_row[0] == c_row[0]:
                                flag=0
                                each_row = list(b_row[0])
                                count = list(b_row[1]['Count'].values)[0]-list(c_row[1]['Count'].values)[0]
                                if count > 0:
                                    each_row.extend(['',count])
                                    result_csv.append(each_row)
                                break
                        if flag:
                            each_row = list(b_row[0])
                            count = list(b_row[1]['Count'].values)[0]
                            each_row.extend(['',count])
                            result_csv.append(each_row)
                elif len(base_header_df):
                    base_group_df = base_header_df.groupby(cols)
                    for b_row in base_group_df:
                        each_row = list(b_row[0])
                        count = list(b_row[1]['Count'].values)[0]
                        each_row.extend(['',count])
                        result_csv.append(each_row)
                        
    return result_csv

if __name__ == '__main__':
    print("Content-type: text/html \n");	
    form = cgi.FieldStorage()	
    # userid = form.getvalue('user_id')
    # log_type = form.getvalue('log_type')
    # template_name = form.getvalue('template_name')
    # base_name = form.getvalue('base_report')
    # compare_name = form.getvalue('compare_report')
    # comparison_reportname = form.getvalue('comparison_reportname')

##    userid = "44"
##    log_type = "TradeInsertion"
##    template_name = "TRD_Testtemp"
##    base_name = "murex_log_prod"
##    compare_name = "raboset1"
##    comparison_reportname = "report6"
    
    # temp_path= "../../../WEB-INF/classes/static/html/Reports/44_Compare/"+comparison_reportname
    # base_folder_name = userid+"_"+base_name
    # compare_folder_name = userid+"_"+compare_name
    # template_path = TEMPLATE_PATH + '\\' + userid + '\\' + log_type
    template_name = 'sample'
    template_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\template\\'
    template_json = json.load(open(template_path+'\\'+template_name+'.json'))
    # base_path = "../../../WEB-INF/classes/static/html/Reports/"+base_folder_name
    # compare_path = "../../../WEB-INF/classes/static/html/Reports/"+compare_folder_name
    base_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\PattrnMing-Rabobnk_Output\\Output\\mxdev21_trade_xmls_set1'
    compare_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\PattrnMing-Rabobnk_Output\\Output\\mxdev21_trade_xmls_set2'
    base_dendo_df = pd.read_csv(base_path+'/IMP035_usage.csv')
    compare_dendo_df = pd.read_csv(compare_path+'/IMP035_usage.csv')
    cols = list(base_dendo_df.columns)
    result_csv = compare_reports_dendo(base_dendo_df,compare_dendo_df,template_json)
    final_df = pd.DataFrame(result_csv, columns = cols)
    final_df.to_csv(template_path+'/compare.csv', index=False, header=True)
    # if not os.path.isdir(temp_path):
    #     os.makedirs (temp_path)
    # final_df.to_csv(temp_path+'/compare.csv', index=False, header=True)
    print("Compare report created, Download report here")
    # ['Trade Family','Trade Group','Typology','Trade Characteristics','Value1','Value2','Count']
    # Trade Family	Trade Group	Typology	Trade Characteristics	Value1	Value2	Count

