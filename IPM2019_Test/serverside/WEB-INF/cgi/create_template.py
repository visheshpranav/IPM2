# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 13:51:49 2021

@author: v.a.subhash.krishna
"""
import os, cgi, configparser
import json, copy

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
TEMPLATE_PATH = parser.get('Upload','templatepath2')

if __name__ == '__main__':
    print("Content-type: text/html \n");	
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')
    log_type = form.getvalue('log_type')
    template_name = form.getvalue('template_name')
    json_data = json.loads(form.getvalue('jsondata'))
    template_path = TEMPLATE_PATH + '\\' + userid
    if not os.path.exists(template_path):
        os.mkdir(template_path)
    template_path = template_path + '\\' + log_type
    if not os.path.exists(template_path):
        os.mkdir(template_path)
    
    
    # json_data = json.loads('[{"tradefamily": "Swaption European"},\
    #                        {" Maturity": " /trades/trade/tradeBody/swaption/stream/maturity"},\
    #                         {" Nominal": " /trades/trade/tradeBody/swaption/stream/capital/initialCapitalAmount"},\
    #                         {"tradefamily": "Xccy Swap"},{" Maturity": " /trades/trade/tradeBody/currencySwap/stream1/maturity"}]')
    final_json = {}
    previous_key = ''
    json_val = {}
    for val in json_data:
        keys = val.keys()
        if 'tradefamily' in keys:
            if previous_key:
                final_json[previous_key] = copy.deepcopy(json_val)
            final_json[val['tradefamily']] = dict()
            json_val = final_json[val['tradefamily']]
            previous_key = val['tradefamily']
        else:
            for key,value in val.items():
                json_val[key.strip()] = value.strip()
##    print(final_json)
    json.dump(final_json,open(template_path+'\\'+template_name+'.json','w'))
        
