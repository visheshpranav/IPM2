

import os, cgi, configparser
import json, copy

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
TEMPLATE_PATH = parser.get('Upload','templatepath2')

if __name__ == '__main__':	
    print("Content-type: text/html \n")
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')		
    logtype = form.getvalue('logtype')
    temname = form.getvalue('temname') + ".json"
    # userid = "44"	
    # logtype = "TradeInsertion"
    # temname = "TRD_tesgfh"+ ".json"
    final_list = []
    template_path = TEMPLATE_PATH + str(userid) + '\\' + logtype + '\\' + temname
    template_json = json.load(open(template_path))
    if logtype == 'TradeInsertion':
        for typo,value in template_json.items():
            for key,val in value.items():
                each_val = [typo,key,val]
                final_list.append(each_val)
        print(final_list)
    else:
        print("data not avaible")
