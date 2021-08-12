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
    filter_type = form.getvalue('filter_type').strip()
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    download_df = pd.read_csv(output_path+'/IMP035_usage.csv',keep_default_na = False)
    if filter_type not in download_df['Level3'].unique():
        filter_df = download_df.loc[download_df['Level2'] == filter_type]
    else:
        filter_df = download_df.loc[download_df['Level3'] == filter_type]
    trade_char_list = list(filter_df['Level4'].unique())
    if 'Events' in trade_char_list:
        trade_char_list.remove('Events')
    print(trade_char_list)
