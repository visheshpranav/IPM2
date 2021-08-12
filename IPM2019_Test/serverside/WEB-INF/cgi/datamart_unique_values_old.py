# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 20:33:18 2021

@author: v.a.subhash.krishna
"""

import pandas as pd
import cgi, configparser, glob

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def generate_df(file_path):
    files = glob.glob(file_path)
    df_list = []
    for file in files:
        df_list.append(pd.read_csv(file))
    group_df = pd.concat(df_list)
    group_df = group_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    return group_df

if __name__ == '__main__':	
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')
    column_name = form.getvalue('column_name')
    test_name = form.getvalue('report_name')
##    userid = "44"
##    column_name = "TIME"
##    test_name = "nov10_12"
    logtype="DATAMART"	
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\"+str(logtype)	
    file_path = dir_path + "\\*.csv"
    column_names_file_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\DM column details\\*.csv"
    # column_name = 'REPORT_LABEL'
    # file_path = "C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_Input\\DataMart- Query_output.csv"
    # column_names_file_path = "C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_Input\\Column_Details_output.csv"
    datamart_df = generate_df(file_path)
    datamart_df['TIME'] = datamart_df['TIME'].astype('int32')
    datamart_df['TIME'] = round(datamart_df['TIME']/3600,1)
    column_details_df = generate_df(column_names_file_path)
    if column_name == 'COLUMNS':
        unique_values = list(column_details_df['COLUMNS'].unique())
    else:
        unique_values = list(datamart_df[column_name].unique())
    print(unique_values)
