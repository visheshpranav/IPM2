# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 10:03:21 2021

@author: v.a.subhash.krishna
"""

import pandas as pd
import numpy as np
import cgi, configparser, glob

#fetch the upload path from config	
# parser = configparser.ConfigParser() 	
# parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
# DATA_PATH = parser.get('Upload','Oflpath')

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
    column_name = column_name.replace('/','_')
    test_name = form.getvalue('report_name')
    unique_value = form.getvalue('unique_value')
##    userid = "44"
##    column_name = "COLUMNS"
##    test_name = "testdmrepotab"
##    unique_value = "DT_NDXIFF0"
    column_name = column_name.replace('/','_')
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    # column_name = 'PROCESSING SCRIPTS'
    # unique_value = 'BD_ALL_PS'
    # output_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_output'
    datamart_output = pd.read_csv(output_path + '/Datamart_output.csv')
    final_df = datamart_output[(datamart_output == unique_value).any(axis=1)]
    # final_df = datamart_output[np.equal.outer(datamart_output.to_numpy(copy=False),
    #                                           [column_name,unique_value]).any(axis=1).all(axis=1)]
    print(final_df)
    final_df.to_csv(output_path+'\\'+column_name+'_'+unique_value+'.csv', index=False, header=True)
    
