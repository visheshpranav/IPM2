# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 09:57:12 2021

@author: v.a.subhash.krishna
"""

import json
# import xml.etree.ElementTree as ET
import os, cgi, configparser
from lxml import etree

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def printDict(d,final):
    for k, v in d.items():
        if type(v) is dict:
            final = printDict(v,final)
        else:
            final.append(k)
    return final

def remove_par(path):
    pathlist1 = path.split('[')
    if len(pathlist1) > 1:
        pathlist2 = pathlist1[1].strip('0123456789]')
        if '[' in pathlist2:
            pathlist2 = remove_par(pathlist2)
        pathlist1[0] = pathlist1[0]+pathlist2
    return pathlist1[0]

if __name__ == '__main__':	
    print("Content-type: text/html \n")
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')		
    logtype = 'Sample'
    filename = form.getvalue('filename')
    headerjson = json.loads(form.getvalue('headerjson'))
##    logtype = 'Sample' 
##    userid = '44'
##    filename = "public.interfaces.import.common.dumpFileName_3508_1.xml"
##    headerjson = { "tesingg": "MxML/trades/trade/tradeBody/interestRateSwap/stream/streamTemplate/streamSchedules/calculationSchedule/scheduleGenerator/standardScheduleGenerator/defaultFrequency/periodMultiplier"}
    dir_path = DATA_PATH + "Cache\\" + str(userid) +"\\"+str(logtype)+"\\"+	str(filename)
    # dir_path = 'C:\\Users\\v.a.subhash.krishna\\Documents\\RE_223_MxmlTrades\\RE_223_MxmlTrades\\public.interfaces.import.common.dumpFileName_3508_1.xml'
    header_path_list = set()
    errors = {}
    i = 1
    XMLDoc = etree.parse(open(dir_path))
    for Node in XMLDoc.xpath('//*'):
        if not Node.getchildren() and Node.text:
            path = XMLDoc.getpath(Node).strip('/')
            path = remove_par(path)
            header_path_list.add(path)
##            print (XMLDoc.getpath(Node))
##    print(header_path_list)
    patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
    if not os.path.exists(patterns_path):
        patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
    # patterns_path = 'C:\\Users\\v.a.subhash.krishna\\Downloads\\murex_log_parsing\\patterns.json'
    patterns_json = json.load(open(patterns_path))
    keys = printDict(patterns_json,[])
    # print(keys)
    for header, header_path in headerjson.items():
        if header in keys:
            errors['ERROR '+str(i)] = header + ' column name already exists.'
            i += 1
        if header_path not in header_path_list:
            errors['ERROR '+str(i)] = 'For '+ header + ", XML path doesn't exists in the sample file."
            i += 1
    if not len(errors):
        for header, header_path in headerjson.items():
            header_path_1 = header_path.replace("MxML", ".")
            patterns_json['common_tags'][header] = header_path_1.strip('/')
        json.dump(patterns_json,open('C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json','w'))
        print('Patterns saved sucessfully.')
    else:
        print(errors)
    
    
    
    # for child in root:
    #     print({x.tag for x in root.findall(child.tag+"/*")})
    # patterns = json.load(open('C:\\LAPAM2019\\Config\\patterns.json'))
