# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 10:03:21 2021

@author: v.a.subhash.krishna
"""

import pandas as pd
import numpy as np
import json
import cgi, configparser

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def col_positions(root,column_name,pos,pos_list):
    for key, value in root.items():
        if key == column_name:
            pos_list.add(pos)
        elif isinstance(value,dict):
            pos_list = col_positions(value,column_name,pos+1,pos_list)
        else:
            for val in value:
                if val == column_name:
                    pos_list.add(pos+1)
    return pos_list

def filter_json(output_json,column_name,unique_value,flag):
    if 'value' in output_json.keys():
        if output_json['name'] != column_name or output_json['value'] != unique_value:
            # print(output_json['name'],output_json['value'])
            if 'children' in output_json.keys():
                remove_var = []
                for i in range(len(output_json['children'])):
                    flag = 0
                    output_json['children'][i],flag = filter_json(output_json['children'][i],column_name,unique_value,flag)
                    if not flag:
                        remove_var.append(output_json['children'][i])
                
                for i in remove_var:
                    str_i = str(i)
                    check_value = "'value': '"+unique_value+"'"
                    if column_name in str_i and check_value in str_i:
                        continue
                    output_json['children'].remove(i)
        else:
            flag = 1
            
    else:
        remove_var = []
        for i in range(len(output_json['children'])):
            flag = 0
            output_json['children'][i],flag = filter_json(output_json['children'][i],column_name,unique_value,flag)
            if not flag:
                remove_var.append(output_json['children'][i])
        for i in remove_var:
            str_i = str(i)
            check_value = "'value': '"+unique_value+"'"
            if column_name in str_i and check_value in str_i:
                continue
            output_json['children'].remove(i)
    return output_json,flag

if __name__ == '__main__':	
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')
    column_name = form.getvalue('column_name')
    test_name = form.getvalue('report_name')
    unique_value = form.getvalue('unique_value')
##    userid = "44"
##    column_name = "COLUMNS"
##    test_name = "testdmrepotab"
##    unique_value = "DT_NDXIFF0"
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    # column_name = 'FREQUENCY'
    # unique_value = '8'
    # output_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_output'
    # patterns = json.load(open("C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_Input\\Datamart_dendo_patterns.json"))
    # output_json = json.load(open(output_path+'//datamart_output_100k.json'))
    # datamart_output = pd.read_csv(output_path + '/Datamart_output_100k.csv')
    if column_name != 'SOD/EOD/INTRADAY':
        check_list = [column_name,unique_value]
        column_name_1 = column_name
    else:
        check_list = [unique_value]
        column_name_1 = unique_value
    output_json = json.load(open(output_path+'//datamart_output.json'))
    datamart_output = pd.read_csv(output_path + '/Datamart_output.csv')
    flag = 0
    output_json, flag = filter_json(output_json,column_name_1,unique_value,flag)
    final_df = datamart_output[np.equal.outer(datamart_output.to_numpy(copy=False),
                                              check_list).any(axis=1).all(axis=1)]
    # final_df = datamart_output[datamart_output == column_name]
    # final_df = final_df[(datamart_output == unique_value).any(axis=1)]
    # final_df = datamart_output[np.equal.outer(datamart_output.to_numpy(copy=False),
    #                                           [column_name,unique_value]).any(axis=1).all(axis=1)]
    # print(final_df)
    column_name = column_name.replace('/','_')
    final_df.to_csv(output_path+'\\'+column_name+'_'+unique_value+'.csv', index=False, header=True)
    json.dump(output_json,open(output_path+'\\'+column_name+'_'+unique_value+'.json','w'))
    
    
