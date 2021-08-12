# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 13:16:20 2021

@author: v.a.subhash.krishna
"""

import json
# import xml.etree.ElementTree as ET
import os, cgi, configparser

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

if __name__ == '__main__':	
    print("Content-type: text/html \n")
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')
    logtype = form.getvalue('logtype')
    json_data = json.loads(form.getvalue('jsondata'))
    # typology = form.getvalue('typology')
##    userid= '44'
##    logtype = 'TradeInsertion'
##    json_data = json.loads('[{ "tradefamily": "IPIS_OUT"},{" IPS_out1": " /trades/trade/tradeBody/simpleCashFlows/plInstrument",   "change_type": "DO"}, {" IPS_out2": " /trades/trade/tradeBody/simpleCashFlows/plInstrumentFamily","change_type": "DO"}]')
    # dir_path = DATA_PATH + "Cache\\" + str(userid) +"\\"+str(logtype)+"\\"+	str(filename)
    # userid = '42'
    # dir_path = 'C:\\Users\\v.a.subhash.krishna\\Documents\\RE_223_MxmlTrades\\RE_223_MxmlTrades\\public.interfaces.import.common.dumpFileName_3508_1.xml'
    
    patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
    if not os.path.exists(patterns_path):
        patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
    if logtype == 'TradeInsertion':
        patterns_json = json.load(open(patterns_path))
        for val in json_data:
            keys = list(val.keys())
            if 'tradefamily' not in keys:
                keys.remove('change_type')
                for key in keys:
##                    print(key.strip())
##                    print(val['change_type'])
                    if val['change_type'] == 'both':
                        if key.strip() not in patterns_json['Dendo_list']:
                            patterns_json['Dendo_list'].append(key.strip())
                    else:
                        if key.strip() in patterns_json['Dendo_list']:
                            patterns_json['Dendo_list'].remove(key.strip())
        json.dump(patterns_json, open('C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json','w'))
    print('Patterns saved sucessfully.')
    
