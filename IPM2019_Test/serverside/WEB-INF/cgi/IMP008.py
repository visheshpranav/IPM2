import re,os,xmltodict,json
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc,shutil
import configparser
from collections import Counter
from datetime import datetime

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
ONL_Report = parser.get('Report','onlpathES')

#Generate Usage Outcome
def generateCSV_IMP008(matched_patterns1,userid,rep_id,Outcome1,report_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name):
    rep_name = str(userid)+"_"+str(rep_id)
##    print("inside")
    matched_patterns = matched_patterns1.split(",")
    Outcomes = Outcome1.split(",")
    main_dictParam,main_dictvalue,usage_arr = main_process(matched_patterns,loglines,Logic)
    write_Usagecsv(rep_name,usage_arr,mode,appName,time_main,date_time,Imp_name,report_name)
    write_DCcsv(rep_name,main_dictParam,main_dictvalue,mode,appName,time_main,date_time,Imp_name,report_name)

def main_process(matched_patterns,loglines,Logic):
    file_timeformat = "%Y-%m-%dT%H:%M:%S"
    convert_timeformat = "%Y-%m-%d %H:%M:%S"
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    pattern_rex = {}
    flag = 0
    req_arr = []
    usage_arr = []
    for pattern in matched_patterns:
        query= 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
        regex = con.execute(query).fetchone()[0]
        pattern_rex[pattern]=regex
    if Logic == "Customization":
        for line in loglines:
            match1 = re.match(r''+str(pattern_rex['P5'])+'',line)
            match3 = re.match(r''+str(pattern_rex['P10'])+'',line)
            match4 = re.match(r''+str(pattern_rex['P11'])+'',line)
            match2 = re.match(r''+str(pattern_rex['P6'])+'',line)
            res_match = re.match(r''+str(pattern_rex['P23'])+'',line)
            if match1:
                req_arr.append(line)
                flag = 1
            elif match4 and flag == 1:
                flag = 0
                req_arr.append(line)
            elif match3:
                req_arr.append(line)
            elif res_match:
                req_arr.append(line)
            elif match2:
                req_arr.append(line)
            elif flag == 1:
                req_arr.append(line)
        if req_arr:
            loglines = req_arr
        else:
            loglines = loglines
        flag = 0
        main_dictParam = {}
        main_dictvalue = {}
        soap_arr = []
        header_arr = []
        isReq = False
        param_keys,values_arr1,param_keysmain,values_arr1main = [], [], [], []
        timekey,userkey,errkey = "","","Status"
        timevalue,uservalue,errvalue,servicecall,response = "","","Pass","",""
        for line in loglines:
            time = re.match(r''+str(pattern_rex['P7'])+'',line)
            user = re.match(r''+str(pattern_rex['P8'])+'',line)
            err = re.match(r''+str(pattern_rex['P10'])+'',line)
            serv = re.match(r''+str(pattern_rex['P4'])+'',line)
            end = re.match(r''+str(pattern_rex['P6'])+'',line)
            soap_start = re.match(r''+str(pattern_rex['P3'])+'',line)
            soap_end = re.match(r''+str(pattern_rex['P9'])+'',line)
            res_match = re.match(r''+str(pattern_rex['P23'])+'',line)
            header_start = re.match(r''+str(pattern_rex['P28'])+'',line)
            header_end = re.match(r''+str(pattern_rex['P29'])+'',line)
            if time:
                param_keys,values_arr1 = [], []
                timekey = time['key']
                timevalue = time['value']
                d = datetime.strptime(timevalue[:19], file_timeformat)
                timevalue = datetime.strftime(d, convert_timeformat)
            elif user:
                userkey = user['key']
                uservalue = user['value']
            elif res_match and flag == 4:
                response = res_match.group(2)
            elif err and flag == 4:
                errvalue = "Fail"
            elif end and flag == 4:
                usage_arr.append(servicecall+","+uservalue+","+str(timevalue)+","+errvalue+","+str(response))
                param_keysmain.insert(0,errkey)
                values_arr1main.insert(0,(errkey.lower()+":"+errkey,errvalue))
                param_keysmain.insert(1,timekey)
                values_arr1main.insert(1,(timekey.lower()+":"+timekey,timevalue))
                param_keysmain.insert(2,userkey)
                values_arr1main.insert(2,(userkey.lower()+":"+userkey,uservalue))
                if not servicecall in main_dictParam.keys():
                    main_dictParam[servicecall] = {}
                    main_dictvalue[servicecall] = {}
                if not timevalue in main_dictParam[servicecall].keys():
                    main_dictParam[servicecall][timevalue] = param_keysmain
                    main_dictvalue[servicecall][timevalue] = values_arr1main
                else:
                    main_dictParam[servicecall][timevalue]  = main_dictParam[servicecall][timevalue].append(param_keysmain)
                    main_dictvalue[servicecall][timevalue] = main_dictvalue[servicecall][timevalue].append(values_arr1main)
                flag = 0
                soap_arr = []
                isError = "Pass"
                timekey,userkey,errkey = "","","Status"
                timevalue,uservalue,errvalue,servicecall,response = "","","Pass","",""
                param_keysmain,values_arr1main = [], []
            elif soap_end and flag == 3:
                soap_arr.append(line)
                flag = 4
                param_keys,values_arr1 = process_req(soap_arr,servicecall)
                param_keysmain.extend(param_keys)
                values_arr1main.extend(values_arr1)
                soap_arr = []
            elif header_start:
                flag = 1
                header_arr.append(line)
            elif header_end and flag == 1:
                flag = 2
                header_arr.append(line)
                param_keys,values_arr1 = process_req(header_arr,"")
                param_keysmain.extend(param_keys)
                values_arr1main.extend(values_arr1)
                header_arr = []
            elif flag == 1:
                header_arr.append(line)
            elif soap_start and flag == 2:
                flag = 3
                soap_arr.append(line)
                isReq = True
            elif isReq and serv:
                isReq = False
                servicecall = serv['usage'].strip()
                soap_arr.append(line)
            elif flag == 3:
                soap_arr.append(line)
    return main_dictParam,main_dictvalue,usage_arr
    
def write_Usagecsv(rep_name,usage_arr,mode,appName,time_main,date_time,Imp_name,report_name):
    if mode == "OFL":
            filename = appName+"_"+report_name.lower()+"_"+Imp_name+"_Usage.csv"
            movepath = "Reports/"+rep_name
            if not os.path.exists("../../../WEB-INF/classes/static/html/"+movepath):
                os.mkdir("../../../WEB-INF/classes/static/html/"+movepath)
            usagefile = open(filename,"w")
    elif mode == "ONL":
        if not os.path.exists("../../../WEB-INF/classes/static/html/Online"):
            os.mkdir("../../../WEB-INF/classes/static/html/Online")
        #print(l)
        rep_name = str(time_main)
        movepath = "Online"
        filename = appName+"_"+Imp_name+"_ONL_Usage_"+str(date_time)+".csv"
        newfile_local = appName+"_"+Imp_name+"_ONL_Usage_"+str(time_main)+".csv"
        newfile = ONL_Report+appName+"_"+Imp_name+"_ONL_Usage_"+str(time_main)+".csv"
        usagefile = open(filename, 'w')
        usagefile_local = open(newfile_local, 'w')
    usagefile.write("Service Call,User ID,Timestamp,Status,Response time(ms)\n")
    if mode == "ONL":
            usagefile_local.write("Service Call,User ID,Timestamp,Status,Response time(ms)\n")
    for i in usage_arr:
        usagefile.write(i+"\n")
        if mode == "ONL":
            usagefile_local.write(i+"\n")
    usagefile.close()
    if mode == "ONL":
        usagefile_local.close()
    shutil.move(filename, "../../../WEB-INF/classes/static/html/"+movepath+"/"+filename)
    if mode == "ONL":
        shutil.move(newfile_local,newfile)
        

def write_DCcsv(rep_name,main_dictParam,main_dictvalue,mode,appName,time_main,date_time,Imp_name,report_name):
    json_data = []
    for service in main_dictParam.keys():
        if mode == "OFL":
            filename = appName+"_"+report_name.lower()+"_"+Imp_name+"_"+service+"_DC.csv"
            movepath = "Reports/"+rep_name
            if not os.path.exists("../../../WEB-INF/classes/static/html/"+movepath):
                os.mkdir("../../../WEB-INF/classes/static/html/"+movepath)
            usagefile = open(filename,"w")
        elif mode == "ONL":
            if not os.path.exists("../../../WEB-INF/classes/static/html/Online"):
                os.mkdir("../../../WEB-INF/classes/static/html/Online")
            #print(l)
            rep_name = str(time_main)
            movepath = "Online"
            filename = appName+"_"+Imp_name+"_ONL_"+service+"_"+str(date_time)+".csv"
            usagefile = open(filename, 'w')
        param_keys = []
        values_arr = []
        keys = []
        for time in main_dictParam[service].keys():
            if main_dictParam[service][time]:
                param_keys.extend(main_dictParam[service][time])
                key = "&&".join(main_dictParam[service][time])
                keys.append(key)
                values_arr.append(main_dictvalue[service][time])
        uniq_keys = set(keys)
        json_data.append(service+","+str(len(list(uniq_keys))))
        seen = set()
        seen_add = seen.add
        head1 =  [x for x in param_keys if not (x in seen or seen_add(x))]
        head = ",".join(head1)
        usagefile.write(head+"\n")
        key_pair = []
        for value in values_arr:
            str_main = ""
            values = []
            for head_val in head1:
                match_val = [s[1] for s in value if ":"+head_val in s[0]]
                if match_val:
                    if None in match_val:
                        match_val = ['None' if v is None else v for v in match_val]
                    str_val = "/".join(match_val)
                else:
                    str_val = "NA"
                values.append(str_val)
            value_str = ",".join(values)
            usagefile.write(value_str+"\n")
        usagefile.close()
        shutil.move(filename, "../../../WEB-INF/classes/static/html/"+movepath+"/"+filename)

def process_req(soap_arr,serviceCall):
    param_keys2 = []
    param_keys1 = []
    values_arr2 = []
    xml_string = "".join(soap_arr)
    xml_dict = xmltodict.parse(xml_string)
    xml_json = json.loads(json.dumps(xml_dict))
    if serviceCall:
        req_arr = list(xml_json['soapenv:Body'].keys())
        if ":" in req_arr[0]:
            req = req_arr[0].split(":")[1]
        else:
            req = req_arr[0]
        xml_json1 = xml_json['soapenv:Body'][req_arr[0]]
    else:
        req_arr = list(xml_json['soapenv:Header'].keys())
        if ":" in req_arr[0]:
            req = req_arr[0].split(":")[1]
        else:
            req = req_arr[0]
        xml_json1 = xml_json['soapenv:Header'][req_arr[0]]
    param_keys = list(iterate_all(xml_json1, "key"))
    for key in param_keys:
        if serviceCall:
            if ":" in key:
                param_keys1.append("body-"+key.split(":")[1])
            else:
                param_keys1.append(key)
        else:
            if ":" in key:
                param_keys1.append("header-"+key.split(":")[1])
            else:
                param_keys1.append(key)
    values_arr2 = list(recursive_items(xml_json1,serviceCall))
    for val in values_arr2:
        if ":" in val[0]:
            str_val = val[0].split(":")[1]
        else:
            str_val = val[0]
        if str_val in param_keys1:
            param_keys2.append(str_val)
##    print(param_keys2)
##    print(values_arr2)
    return param_keys2,values_arr2
        
def recursive_items(dictionary,serviceCall):
    #print(dictionary)
    for key, value in dictionary.items():
        if type(value) is dict:
            yield from recursive_items(value,serviceCall)
        elif type(value) is list:
            for val in value:
                if type(val) == dict:
                    yield from recursive_items(val,serviceCall)
                if type(val) == str:
                    if not ":" in key:
                        key = ":"+key
                    if serviceCall:
                        key = key.split(":")[0]+":body-"+key.split(":")[1]
                        val = "body-"+str(val)
                    else:
                        key = key.split(":")[0]+":header-"+key.split(":")[1]
                        val = "header-"+str(val)
                    yield(key,val)
                
        else:
            if not ":" in key:
                key = ":"+key
            if serviceCall:
                key = key.split(":")[0]+":body-"+key.split(":")[1]
                value = "body-"+str(value)
            else:
                key = key.split(":")[0]+":header-"+key.split(":")[1]
                value = "header-"+str(value)
            yield (key, value)
            

def iterate_all(iterable, returned="key"):
    
    """Returns an iterator that returns all keys or values
       of a (nested) iterable.
       
       Arguments:
           - iterable: <list> or <dictionary>
           - returned: <string> "key" or "value"
           
       Returns:
           - <iterator>
    """
  
    if isinstance(iterable, dict):
        for key, value in iterable.items():
            if returned == "key":
                yield key
            elif returned == "value":
                if not (isinstance(value, dict) or isinstance(value, list)):
                    yield value
            else:
                raise ValueError("'returned' keyword only accepts 'key' or 'value'.")
            for ret in iterate_all(value, returned=returned):
                yield ret
    elif isinstance(iterable, list):
        for el in iterable:
            for ret in iterate_all(el, returned=returned):
                yield ret                
    
#Function to qualify the log
def parse_log(logpath_file):
    if logpath_file.endswith(".xlsx"):
        sheet_num = 0
        wb=xlrd.open_workbook(logpath_file)
        sheet=wb.sheet_by_index(sheet_num)
        loglines = iter_rows(sheet)
    else:
        fp = open(logpath_file,encoding='utf8', errors='ignore')
        loglines = fp
    return loglines        

#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    #matched_patterns = form.getvalue("matched_patterns")
    time = datetime.now()
    time_main = re.sub(r'[:.]','C',str(time))
    date_time = str(time).split(" ")[0]
    matched_patterns = "P3,P4,P5,P6,P7,P8,P9,P10,P11,P23,P28,P29"
    userid = ""
    rep_id = ""
    rep_name = ""
    Outcome = "csv"
    Logic = "Customization"
    logpath_file = "C:\\LAPAM2019\\DataLake\\Online\\WebSphere\\SystemOut.log"
    mode = "ONL"
    appName = "TWA"
    Imp_name = "search"
    loglines = parse_log(logpath_file)
    generateCSV_IMP008(matched_patterns,userid,rep_id,Outcome,rep_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name)
    
