# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 20:33:18 2021

@author: v.a.subhash.krishna
"""

import json
import cgi, configparser

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')


if __name__ == '__main__':	
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')
    column_name = form.getvalue('column_name')
    test_name = form.getvalue('report_name')
##    userid = "44"
##    column_name = "TIME"
##    test_name = "dmreptab"
    # logtype="DATAMART"
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    # column_name = "FREQUENCY"
    # output_path = "C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_output\\"
    unique_values_json = json.load(open(output_path+'/datamart_unique_values.json'))
    # column_name = 'SOD/EOD/INTRADAY'
    # file_path = "C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_Input\\DataMart_Sample_Data.csv"
    # column_names_file_path = "C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_Input\\Column_Details_output.csv"
    unique_values = unique_values_json[column_name]
    print(unique_values)
