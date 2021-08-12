import re,os,xmltodict,json
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc,shutil
import configparser
from collections import Counter
from datetime import datetime
from saveRecommendations import observation

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAME = parser.get('DSN','DSN_NAME')
ONL_Report = parser.get('Report','onlpathES')

#Generate Usage Outcome
def generateCSV_IMP002(matched_patterns1,userid,rep_id,Outcome1,report_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name):
    rep_name = str(userid)+"_"+str(rep_id)
    file_timeformat = "%Y-%m-%dT%H:%M:%S"
    convert_timeformat = "%Y-%m-%d %H:%M:%S"
##    print("inside")
    matched_patterns = matched_patterns1.split(",")
    if ("P11" in matched_patterns) and (not "P10" in matched_patterns):
        matched_patterns.append("P10")
    Outcomes = Outcome1.split(",")
    con = pyodbc.connect("DSN="+DSN_NAME)
    cur = con.cursor()
    query_max= 'SELECT Max(Timestamp) from onl_datacombination;'
    dc_maxtiming = cur.execute(query_max).fetchone()[0]
    if dc_maxtiming:
        dc_maxtiming = datetime.strftime(dc_maxtiming, convert_timeformat)
    print(dc_maxtiming)
    pattern_rex = {}
    flag = 0
    req_arr = []
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
            if match1:
                req_arr.append(line)
                flag = 1
            elif match4 and flag == 1:
                flag = 0
                req_arr.append(line)
            elif match3:
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
        soap_txt =""
        isReq = False
        param_keys,values_arr1 = [], []
        soaphead_arr = []
        head_flag = 0
        timekey,userkey,errkey = "","","Status"
        timevalue,uservalue,errvalue,servicecall = "","","Pass",""
        for line in loglines:
            time = re.match(r''+str(pattern_rex['P7'])+'',line)
            user = re.match(r''+str(pattern_rex['P8'])+'',line)
            err = re.match(r''+str(pattern_rex['P10'])+'',line)
            serv = re.match(r''+str(pattern_rex['P4'])+'',line)
            end = re.match(r''+str(pattern_rex['P6'])+'',line)
            soap_start = re.match(r''+str(pattern_rex['P3'])+'',line)
            soap_end = re.match(r''+str(pattern_rex['P9'])+'',line)
            soap_headstart = re.match(r''+str(pattern_rex['P28'])+'',line)
            soap_headend = re.match(r''+str(pattern_rex['P29'])+'',line)
            if soap_headstart and head_flag == 0:
                head_flag = 1
                soaphead_arr = []
                soaphead_arr.append(line.strip()) 
            elif time and head_flag == 1:
                param_keys,values_arr1 = [], []
                timekey = time['key']
                timevalue = time['value']
                d = datetime.strptime(timevalue[:19], file_timeformat)
                timevalue = datetime.strftime(d, convert_timeformat)
                soaphead_arr.append(line.strip())
            elif user and head_flag == 1:
                userkey = user['key']
                uservalue = user['value']
                soaphead_arr.append(line.strip())
            elif soap_headend and head_flag == 1:
                soaphead_arr.append(line.strip())
                head_flag = 2
            elif err and flag == 2:
                errvalue = "Fail"
            elif end and flag == 2:
                param_keys.insert(0,errkey)
                values_arr1.insert(0,(errkey.lower()+":"+errkey,errvalue))
                param_keys.insert(1,timekey)
                values_arr1.insert(1,(timekey.lower()+":"+timekey,timevalue))
                param_keys.insert(2,userkey)
                values_arr1.insert(2,(userkey.lower()+":"+userkey,uservalue))
                if mode == "ONL":
                    if(not dc_maxtiming) or (dc_maxtiming < timevalue):
                        query= 'INSERT INTO onl_datacombination (`App_Name`, `ServiceCall`, `Timestamp`, `Status`, `XML_Data`)VALUES ("'+appName+'","'+servicecall+'","'+timevalue+'","'+errvalue+'","'+soap_txt+'");'
                        cur.execute(query)
                        con.commit()
                        print("insert")
                if not servicecall in main_dictParam.keys():
                    main_dictParam[servicecall] = {}
                    main_dictvalue[servicecall] = {}
##                    print("~~~dictcreat~~")
##                    print(servicecall)
##                    print(main_dictParam)
                if not timevalue in main_dictParam[servicecall].keys():
                    main_dictParam[servicecall][timevalue] = param_keys
                    main_dictvalue[servicecall][timevalue] = values_arr1
##                    print("~~~timecreat~~")
##                    print(servicecall)
##                    print(main_dictParam)
                else:
                    main_dictParam[servicecall][timevalue]  = main_dictParam[servicecall][timevalue].extend(param_keys)
                    main_dictvalue[servicecall][timevalue] = main_dictvalue[servicecall][timevalue].extend(values_arr1)
##                    print("~~~valueadd~~")
##                    print(timevalue)
##                    print(servicecall)
##                    print(main_dictParam)
                flag = 0
                head_flag = 0
                soap_arr = []
                soaphead_arr = []
                soap_txt =""
                isError = "Pass"
                timekey,userkey,errkey = "","","Status"
                timevalue,uservalue,errvalue,servicecall = "","","Pass",""
            elif soap_end and flag == 1:
                soap_arr.append(line)
                soaphead_arr.append(line.strip())
                flag = 2
                #print(timevalue)
                #print(servicecall)
                param_keys,values_arr1 = process_req(soap_arr,servicecall)
                soap_txt = "~&~".join(soaphead_arr)
                soap_arr = []
                soaphead_arr = []
            elif soap_start and head_flag == 2:
                flag = 1
                soap_arr.append(line)
                soaphead_arr.append(line.strip())
                isReq = True
            elif isReq and serv:
                isReq = False
                servicecall = serv['usage'].strip()
                soap_arr.append(line)
                soaphead_arr.append(line.strip())
            elif flag == 1:
                soap_arr.append(line)
                soaphead_arr.append(line.strip())
            elif head_flag == 1:
                soaphead_arr.append(line.strip())
##        print(main_dictParam)
##        print(main_dictParam)
        write_csv(rep_name,main_dictParam,main_dictvalue,mode,appName,time_main,date_time,Imp_name,report_name)


def write_csv(rep_name,main_dictParam,main_dictvalue,mode,appName,time_main,date_time,Imp_name,report_name):
    json_data = []
    json_online = []
    json_off = []
    fail_arr = []
    for service in main_dictParam.keys():
        
        param_keys = []
        values_arr = []
        keys = []
        keys_stat = []
        flag = 0
        for time in main_dictParam[service].keys():
            if main_dictParam[service][time]:
                param_keys.extend(main_dictParam[service][time])
                key = "&&".join(main_dictParam[service][time])
                keys.append(key)
                json_online.append(str(time)+","+service+","+key+","+main_dictvalue[service][time][0][1])
                keys_stat.append(key+","+main_dictvalue[service][time][0][1])
                values_arr.append(main_dictvalue[service][time])
                flag = 1
        uniq_keys = set(keys)
        fail_sum = 0
        for key in uniq_keys:
            count_pass = len([f for f in keys_stat if key+",Pass" in f])
            count_fail = len([f for f in keys_stat if key+",Fail" in f])
            json_off.append(service+","+key+","+str(count_pass)+","+str(count_fail))
            fail_sum = fail_sum+count_fail
        fail_arr.append(service+","+str(fail_sum))
        if flag == 1:
            flag = 0
            if mode == "OFL":
                filename = appName+"_"+report_name.lower()+"_"+Imp_name+"_"+service+".csv"
                movepath = "Reports/"+rep_name
                if not os.path.exists("../../../html/"+movepath):
                    os.mkdir("../../../html/"+movepath)
                usagefile = open(filename,"w")
            elif mode == "ONL":
                if not os.path.exists("../../../html/Online"):
                    os.mkdir("../../../html/Online")
                #print(l)
                movepath = "Online"
                filename = appName+"_"+Imp_name+"_ONL_"+service+"_"+str(date_time)+".csv"
                usagefile = open(filename, 'w')
            if len(list(uniq_keys))>0: 
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
            shutil.move(filename, "../../../html/"+movepath+"/"+filename)
    observation_process(json_off,fail_arr,rep_name,mode)
    json_creation(json_online,json_off,rep_name,json_data,mode,appName,time_main,date_time,Imp_name,report_name)

def json_creation(json_online,json_off,rep_name,json_data,mode,appName,time_main,date_time,Imp_name,report_name):
    j = 1
    li_len = len(json_data)
    if mode == "OFL":
        json_filename = appName+"_"+report_name.lower()+"_"+Imp_name+".json"
        csv_filename = appName+"_"+report_name.lower()+"_"+Imp_name+".csv"
        csv_obs = appName+"_"+report_name.lower()+"_"+Imp_name+"_All.csv"
        movepath = "Reports/"+rep_name
        if not os.path.exists("../../../html/"+movepath):
            os.mkdir("../../../html/"+movepath)
        f = open(json_filename, 'w')
        f_csv = open(csv_filename, 'w')
        f_csvobs = open(csv_obs, 'w')
        f_csv.write("ServiceCall,UniqueParameterCount"+"\n")
        f_csvobs.write("ServiceCall,UniqueParameter,Pass_Count,Fail_Count"+"\n")
    elif mode == "ONL":
        if not os.path.exists("../../../html/Online"):
            os.mkdir("../../../html/Online")
        movepath = "Online"
        #print(l)
        rep_name = str(time_main)
        json_filename = appName+"_"+Imp_name+"_ONL_"+str(date_time)+".json"
        newfile = ONL_Report+appName+"_"+Imp_name+"_ONL_"+str(time_main)+".json"
        csv_filename = appName+"_"+Imp_name+"_ONL_"+str(date_time)+".csv"
        csv_obs = appName+"_"+Imp_name+"_All_ONL_"+str(date_time)+".csv"
        csv_newfile = ONL_Report+appName+"_"+Imp_name+"_All_ONL_"+str(time_main)+".csv"
        csv_filename_Es = appName+"_"+Imp_name+"_AllU_ONL_"+str(time_main)+".csv"
        f = open(json_filename, 'w')
        f_csv = open(csv_filename, 'w')
        fEs_csv = open(csv_filename_Es, 'w')
        f_csvobs = open(csv_obs, 'w')
        fEs_csv.write("Timestamp,ServiceCall,UniqueParameter,Status"+"\n")
        f_csv.write("ServiceCall,UniqueParameterCount"+"\n")
        f_csvobs.write("ServiceCall,UniqueParameter,Pass_Count,Fail_Count"+"\n")
    #json &csv writing
    json_val = "["
    for i in json_data:
        sli_arr = i.split(",")
        if (not sli_arr[1] == "0") and (li_len == j):
            json_val = json_val + "{\"axis\":\""+sli_arr[0]+"\",\"value\":"+str(sli_arr[1])+"}]"
            f_csv.write(sli_arr[0]+","+str(sli_arr[1])+"\n")
        elif not sli_arr[1] == "0":
            json_val = json_val + "{\"axis\":\""+sli_arr[0]+"\",\"value\":"+str(sli_arr[1])+"},"
            f_csv.write(sli_arr[0]+","+str(sli_arr[1])+"\n")
        j = j+1
    json_v = "["+json_val + "]"
    
    if mode == "ONL":
        for val in json_online:
            fEs_csv.write(val+"\n")
        fEs_csv.close()
    for val in json_off:
        f_csvobs.write(val+"\n")
    f_csvobs.close()
    f_csv.close()
    f.write(json_v)
    f.close()
    shutil.move(json_filename, "../../../html/"+movepath+"/"+json_filename)
    shutil.move(csv_filename, "../../../html/"+movepath+"/"+csv_filename)
    shutil.move(csv_obs, "../../../html/"+movepath+"/"+csv_obs)
    if mode == "ONL":
        shutil.copy("../../../html/"+movepath+"/"+json_filename,newfile)
        shutil.move(csv_filename_Es,csv_newfile)


def process_req(soap_arr,serviceCall):
    param_keys2 = []
    param_keys1 = []
    values_arr2 = []
    xml_string = "".join(soap_arr)
    xml_dict = xmltodict.parse(xml_string)
    xml_json = json.loads(json.dumps(xml_dict))
    req_arr = list(xml_json['soapenv:Body'].keys())
    if ":" in req_arr[0]:
        req = req_arr[0].split(":")[1]
    else:
        req = req_arr[0]
    xml_json1 = xml_json['soapenv:Body'][req_arr[0]]
    param_keys = list(iterate_all(xml_json1, "key"))
##    print(param_keys)
    for key in param_keys:
        if ":" in key:
            param_keys1.append(key.split(":")[1])
        else:
            param_keys1.append(key)
    values_arr2 = list(recursive_items(xml_json1))
    for val in values_arr2:
        if ":" in val[0]:
            str_val = val[0].split(":")[1]
        else:
            str_val = val[0]
        if str_val in param_keys1:
            param_keys2.append(str_val)
##    print(values_arr2)
    return param_keys2,values_arr2
        
def recursive_items(dictionary):
    #print(dictionary)
    for key, value in dictionary.items():
        if type(value) is dict:
            yield from recursive_items(value)
        elif type(value) is list:
            for val in value:
                if type(val) == dict:
                    yield from recursive_items(val)
                if type(val) == str:
                    if not ":" in key:
                        key = ":"+key
                    yield(key,val)
                
        else:
            if not ":" in key:
                key = ":"+key
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

#observation
def observation_process(observe_data,failcount_arr,rep_name,mode):
    userid,rep_id = rep_name.split("_")
    txt_data = "Top 2 service calls as per failure count:"
    fail_valarr = [int(f.split(",")[1]) for f in failcount_arr]
    sort_values = sorted(fail_valarr,reverse=True)
    max_values = sort_values[:2]
    max_service = []
    for val in max_values:
        max_service.extend([f for f in failcount_arr if str(val)== f.split(",")[-1]])
    i = 1
    for val in max_service:
##        print(val)
        service,fail_sum = val.split(",")
        pass_arr = [int(f.split(",")[2]) for f in observe_data if service == f.split(",")[0]]
        fail_arr = [int(f.split(",")[3]) for f in observe_data if service == f.split(",")[0]]
        partial_fail = []
        partial_pass = []
        for f in observe_data:
            val_arr = f.split(",")
            if (not int(val_arr[3]) == 0 and not int(f.split(",")[2]) == 0) and service == f.split(",")[0]:
                partial_fail.append(int(val_arr[3]))
                partial_pass.append(int(val_arr[2]))
        txt_data = txt_data+"\n   "+str(i)+". "+service
        if 0 in pass_arr:
            pass_ind = [i for i,e in enumerate(pass_arr) if e == 0]
            fail_data = [fail_arr[i] for i in pass_ind]
            #txt_data = txt_data+"\n      * "+str(pass_arr.count(0))+"/"+str(len(pass_arr))+" DataCombination Failed Completely"
            txt_data = txt_data+"\n      * "+str(sum(fail_data))+"/"+str(sum(fail_data))+" service call requests failed for "+str(pass_arr.count(0))+" data combination resulting in (Full failure)"
        if 0 in fail_arr:
            fail_ind = [i for i,e in enumerate(fail_arr) if e == 0]
            pass_data = [pass_arr[i] for i in fail_ind]
            #txt_data = txt_data+"\n      * "+str(fail_arr.count(0))+"/"+str(len(fail_arr))+" data combination resulting in (Full failure)"
            txt_data = txt_data+"\n      * "+str(sum(pass_data))+"/"+str(sum(pass_data))+" service call requests passed for "+str(fail_arr.count(0))+" data combination resulting in (Full pass)"
        if partial_fail:
            partial_cou = sum(partial_pass)+sum(partial_fail)
##            partial_avg = sum(partial_fail)/sum(fail_arr)
            partial_avg = sum(partial_fail)/partial_cou
            partial_percent = partial_avg * 100
            #txt_data = txt_data+"\n      * "+str(len(partial_fail))+"/"+str(len(fail_arr))+" attributes to "+str(round(partial_percent))+"% of failure"
            txt_data = txt_data+"\n      * "+str(sum(partial_fail))+"/"+str(partial_cou)+" service call requests failed for "+str(len(partial_fail))+" data combination resulting "+str(round(partial_percent))+"% failure (partial failure)"
        i = i+1
##    print(txt_data)
    if mode == "OFL":
        txt_data = txt_data+"\nNote : For a service call, combination of fields with data is considered as a unique data combination with missing fields shown as NA.\nPlease download the data combination file for more details."
        print(txt_data)
        observation(txt_data,rep_id,userid,"IMP002")
            

        
#Function to qualify the log
def parse_log(logpath_file):
    if logpath_file.endswith(".xlsx"):
        sheet_num = 0
        wb=xlrd.open_workbook(logpath_file)
        sheet=wb.sheet_by_index(sheet_num)
        loglines = iter_rows(sheet)
    else:
        loglines = []
        files = os.listdir(logpath_file)
        for file in files:
            fp = open(logpath_file+file,encoding='utf8', errors='ignore')
            loglines.extend(fp)
    return loglines        

#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    #matched_patterns = form.getvalue("matched_patterns")
    time = datetime.now()
    time_main = re.sub(r'[:.]','C',str(time))
    date_time = str(time).split(" ")[0]
    matched_patterns = "P5,P6,P7,P8,P3,P9,P3,P4,P6,P11,P28,P29"
    userid = ""
    rep_id = ""
    rep_name = ""
    Outcome = "json,csv"
    Logic = "Customization"
    logpath_file = "C:\\LAPAM2019\\DataLake\\Online\\WebSphere\\"
##    logpath_file = "C:\\LAPAM2019\\DataLake\\Online\\SystemOut.log"
    mode = "ONL"
    appName = "TWA"
    Imp_name = "data combination"
    loglines = parse_log(logpath_file)
    generateCSV_IMP002(matched_patterns,userid,rep_id,Outcome,rep_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name)
    
