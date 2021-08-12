# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 10:28:14 2021

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
##    typology = typology.replace(' ','_')
    header = form.getvalue('header')
    if logtype == 'Trade Char':
        final_list = []
        patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
        if not os.path.exists(patterns_path):
            patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
        # patterns_path = 'C:\\Users\\v.a.subhash.krishna\\Downloads\\murex_log_parsing\\patterns.json'
        patterns_json = json.load(open(patterns_path))
        if typology == 'Common Tags':
            typology = 'common_tags'
        patterns_json[typology].pop(header)
        if header in patterns_json['Dendo_list']:
            patterns_json['Dendo_list'].remove(header)
        for key,value in patterns_json[typology].items():
            final_list.append([key,value])
        json.dump(patterns_json,open('C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json','w'))
        print(final_list)
