# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 09:57:12 2021

@author: v.a.subhash.krishna
"""

import json
import xml.etree.ElementTree as ET
import os, cgi, configparser
# from lxml import etree

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def printDict(d,typology):
    final = []
    final.extend(list(d['common_tags'].keys()))
    if typology != 'Common Tags':
        final.extend(list(d[typology].keys()))
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
    typology = form.getvalue('typology')
    # typology = typology.replace(' ','_')
    pattern_type = form.getvalue('patterntype')
    headerjson = json.loads(form.getvalue('headerjson'))
    
##    userid = '44'
##    filename = "public.interfaces.import.common.dumpFileName_3508_1.xml"
    # typology = 'Common Tags'
    # pattern_type = 'Both'
    # headerjson = { "tesingg": "MxML/trades/trade/tradeBody/interestRateSwap/*/streamTemplate/streamSchedules/calculationSchedule/scheduleGenerator/standardScheduleGenerator/defaultFrequency/periodMultiplier"}
    dir_path = DATA_PATH + "Cache\\" + str(userid) +"\\"+str(logtype)+"\\"+	str(filename)
    # dir_path = 'C:\\Users\\v.a.subhash.krishna\\Documents\\RE_223_MxmlTrades\\RE_223_MxmlTrades\\public.interfaces.import.common.dumpFileName_3508_1.xml'
    # header_path_list = set()
    errors = {}
    i = 1
    # XMLDoc = etree.parse(open(dir_path))
    tree = ET.parse(dir_path)
    root = tree.getroot()
    # for Node in XMLDoc.xpath('//*'):
    #     if not Node.getchildren() and Node.text:
    #         path = XMLDoc.getpath(Node).strip('/')
    #         path = remove_par(path)
    #         header_path_list.add(path)
            # print (XMLDoc.getpath(Node))
    # print(header_path_list)
    patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
    if not os.path.exists(patterns_path):
        patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
    # patterns_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\44_patterns_updated.json'
    patterns_json = json.load(open(patterns_path))
    keys = printDict(patterns_json,typology)
    # print(keys)
    for header, header_path in headerjson.items():
        header_path = header_path.replace('MxML','.')
        header_path = header_path.replace('*','*/')
        obj_list = root.findall(header_path)
        # print(obj_list)
        if header in keys:
            errors['ERROR '+str(i)] = header + ' column name already exists.'
            i += 1
         # and header_path not in header_path_list
        if not len(obj_list):
            errors['ERROR '+str(i)] = 'For '+ header + ", XML path doesn't exists in the sample file."
            i += 1
    if not len(errors):
        if typology == 'Common Tags':
            typology = 'common_tags'
        for header, header_path in headerjson.items():
            if pattern_type == 'Both':
                if header not in patterns_json['Dendo_list']:
                    patterns_json['Dendo_list'].append(header)
            header_path_1 = header_path.replace("MxML", ".")
            patterns_json[typology][header] = header_path_1.strip('/')
        json.dump(patterns_json,open('C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json','w'))
        print('Patterns saved sucessfully.')
    else:
        print(errors)
    
    
    
    # for child in root:
    #     print({x.tag for x in root.findall(child.tag+"/*")})
    # patterns = json.load(open('C:\\LAPAM2019\\Config\\patterns.json'))
