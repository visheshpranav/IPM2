# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 10:19:59 2021

@author: v.a.subhash.krishna
"""

import json
import os, cgi

if __name__ == '__main__':	
    print("Content-type: text/html \n")
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')		
    logtype = form.getvalue('logtype')
    typology = form.getvalue('typology')
    try:
        view_pattern = form.getvalue('view_pattern')
    except:
        view_pattern = ''
 #   userid = "44"	
 #   logtype = "Trade Char"
 #   typology = "Common Tags"
##    typology = typology.replace(' ','_')
    if logtype == 'TradeInsertion':
        final_list = []
        patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
        if not os.path.exists(patterns_path):
            patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
        # patterns_path = 'C:\\Users\\v.a.subhash.krishna\\Downloads\\murex_log_parsing\\patterns.json'
        patterns_json = json.load(open(patterns_path))
        if typology == 'Common Tags':
            typology = 'common_tags'
        typo_tags = patterns_json[typology]
        for key,value in patterns_json[typology].items():
            if view_pattern:
                if key in patterns_json['Dendo_list']:
                    final_list.append([key,value,'Both'])
                else:
                    final_list.append([key,value,'Download'])
            else:
                final_list.append([key,value])
        print(final_list)

