# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 10:10:22 2021

@author: v.a.subhash.krishna
"""

import json
import os, cgi

if __name__ == '__main__':	
    print("Content-type: text/html \n")
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')		
    logtype = form.getvalue('logtype')
##    userid = "44"		
##    logtype = "TradeInsertion"
    if logtype == 'TradeInsertion':
        typology = []
        patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
        if not os.path.exists(patterns_path):
            patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
        # patterns_path = 'C:\\Users\\v.a.subhash.krishna\\Downloads\\murex_log_parsing\\patterns.json'
        patterns_json = json.load(open(patterns_path))
        typology = list(patterns_json.keys())
        index = typology.index('common_tags')
        typology[index] = 'Common Tags'
        typology.remove('internalId')
        typology.remove('Contract Id')
        typology.remove('Dendo_list')
        typology.remove('lastContractEventReference')
##        typology.remove('events')
##        typology = [val.replace('_',' ') for val in typology]
        print(typology)
