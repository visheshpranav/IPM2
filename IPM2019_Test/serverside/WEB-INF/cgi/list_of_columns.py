# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 20:10:18 2021

@author: v.a.subhash.krishna
"""
import json
import pandas as pd
import os, cgi, configparser

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def get_all_columns(value, all_columns):
    for key,values in value.items():
        all_columns.add(key)
        if isinstance(values,dict):
            all_columns = get_all_columns(values, all_columns)
        else:
            for val in values:
                all_columns.add(val)
    return all_columns

if __name__ == '__main__':	
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    userid = form.getvalue('user_id')
    test_name = form.getvalue('report_name')
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    patterns = json.load(open("C:\\LAPAM2019\\Config\\Datamart_dendo_patterns.json"))
    # patterns = json.load(open("C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_Input\\Datamart_dendo_patterns.json"))
    # output_path = "C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_output\\"
    output_df = pd.read_csv(output_path+'//Datamart_output.csv',keep_default_na = False)
    all_columns = set()
    for dm_type,value in patterns.items():
        all_columns = get_all_columns(value, all_columns)
    all_columns.remove('FREQUENCY')
    all_columns = [val for val in all_columns if val in output_df.values]
    # final_df = final_df[(datamart_output == unique_value).any(axis=1)]
    print(list(all_columns))
