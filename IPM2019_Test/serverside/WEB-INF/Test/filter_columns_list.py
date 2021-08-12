# -*- coding: utf-8 -*-
"""
Created on Thu May 27 02:12:15 2021

@author: v.a.subhash.krishna
"""

import pandas as pd
import cgi, configparser

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')


if __name__ == '__main__':	
    print("Content-type: text/html \n");
    # print(datetime.now())	
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id').strip()
    test_name = form.getvalue('report_name').strip()
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    download_df = pd.read_csv(output_path+'/IMP035_usage.csv',keep_default_na = False)
    na_df = download_df.loc[download_df['Level3']=='NA']
    filter_list = list(download_df['Level3'].unique())
    if 'NA' in filter_list:
        filter_list.extend(list(na_df['Level2'].unique()))
        filter_list.remove('NA')
    print(filter_list)