# -*- coding: utf-8 -*-
"""
Created on Tue May 18 23:03:26 2021

@author: v.a.subhash.krishna
"""

import pandas as pd
import json
import os, cgi, configparser

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def generate_filter_df(master_df, filter_type, col_list, filter_outpath, filename):
    filter_list = []
    if 'tradeType' in master_df.columns:
        filter_col = 'tradeType'
    else:
        filter_col = 'Typology'
    if filter_type != 'All':
        master_df = master_df.loc[master_df[filter_col] == filter_type]
    groupby_list = ['Category','tradeFamily','tradeGroup', filter_col]
    groupby_list.extend(col_list)
    # print(groupby_list)
    groupby_df = master_df.groupby(groupby_list)
    for df in groupby_df:
        if '' not in df[0]:
            dum_list = list(df[0][0:4])
            i = 4
            for col in col_list:
                dum_list.extend([col,df[0][i]])
                i += 1
            dum_list.append(len(df[1]))
            filter_list.append(dum_list)
            # print(dum_list)
    col_name = ['Category','tradeFamily','tradeGroup', filter_col]
    for col in col_list:
        col_name.extend([col,col+' Value'])
    col_name.append('Count')
    filter_df = pd.DataFrame(filter_list,columns=col_name)
    dendo_col_name = ['Category']
    for i in range(1,len(col_name)-1):
        dendo_col_name.append('Level'+str(i))
    dendo_col_name.append('Count')
    dendo_filter_df = pd.DataFrame(filter_list,columns=dendo_col_name)
    dendo_filter_df.to_csv(filter_outpath+'\\'+filename+'.csv', index=False, header=True)
    filter_df.to_csv(filter_outpath+'\\TradeEvents_'+filter_type+'_Rearrange.csv', index=False, header=True)
    master_df.drop(columns='Category',inplace = True)
    filter_df.drop(columns='Category',inplace = True)
    with pd.ExcelWriter(filter_outpath+'/TradeEvents_'+filter_type+'_Rearrange.xlsx') as writer:
        filter_df.to_excel(writer, sheet_name='Count', index=False, header=True)
        master_df.to_excel(writer, sheet_name='Master', index=False, header=True)



if __name__ == '__main__':	
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    userid = form.getvalue('user_id')
    test_name = form.getvalue('report_name')
    # # logtype = form.getvalue('logtype').split("\n")[0].strip()
    filter_type = form.getvalue('filter_type')
    filename = form.getvalue('filename')
    col_list = json.loads(form.getvalue('col_list'))
    dat = form.getvalue("dateTime")
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    # filename = 'Trade_Rearrange_Usage_2021-5-1910-9-31'
    # filter_type = 'NA'
    # dat = '2021-5-1912-49-31'
    # col_list = ['Trade Status','Typology']
    # output_path = "C:\\Users\\v.a.subhash.krishna\\Downloads\\five_output"
    filter_outpath = output_path + '\\' + filter_type + '_' + dat
    if not os.path.exists(filter_outpath):	
        os.mkdir(filter_outpath)
    master_df = pd.read_csv(output_path+'\\murex_master.csv', keep_default_na = False)
    generate_filter_df(master_df, filter_type, col_list, filter_outpath, filename)
    