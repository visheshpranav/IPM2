# -*- coding: utf-8 -*-
"""
Created on Fri May  7 13:06:19 2021

@author: v.a.subhash.krishna
"""

import json
import os, cgi, configparser
import pandas as pd
from murex_log_parsing import generate_dendo

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

if __name__ == '__main__':	
    print("Content-type: text/html \n")
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')
    logtype = form.getvalue('logtype')
    report_list = json.loads(form.getvalue('reportlist'))
    patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
    if not os.path.exists(patterns_path):
        patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
    patterns = json.load(open(patterns_path))
    for report_name in report_list:
        folder_name=userid+"_"+report_name
        output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
        master_df = pd.read_csv(output_path+'/murex_master.csv')
        dendo_keys = [ val for val in patterns['Dendo_list'] if val in master_df.columns]
        if 'Contract Id' not in dendo_keys:
            dendo_keys.append('Contract Id')
        dendo_keys = list(set(dendo_keys))
        generate_dendo(master_df,output_path,dendo_keys,report_name,'normal')
    