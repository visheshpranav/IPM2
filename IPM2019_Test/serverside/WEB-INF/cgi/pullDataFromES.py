import cgi, cgitb, sys
import os,re,shutil,openpyxl
import configparser
import pyodbc,datetime
from elasticsearch import Elasticsearch
import elasticsearch.helpers
from collections import Counter
from datetime import datetime
from IMP002 import process_req
from statistics import stdev

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
source_ip = parser.get('Report','ipaddress')
ONL_Report = parser.get('Report','onlpathES')
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

def usage_process(date_time, Index, appName, from_date, to_date):
    servicecalllist=[]
    es = Elasticsearch(source_ip, port=9200)  
                
    res_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["ServiceCall", "Timestamp", "message"],"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date}}}}, 
                index = Index)
    #Res_data = STAD_process(res_stad)
    counter = Counter()    
    dest_filename = "../../../html/Online/" + appName+"_usage analysis_TP_"+str(date_time)+".csv"
    filename = appName+"_usage analysis_TP_"+str(date_time)+".csv"
    for doc in res_stad:
        servicecalllist.append(doc['_source']['ServiceCall'])
    counter = Counter(servicecalllist)
    usagefile = open(filename,"w")
    usagefile.write("id,value\n")
    for key in dict(counter):
        usagefile.write(key+","+str(dict(counter)[key])+"\n")
    usagefile.close()
    shutil.move(filename, dest_filename)

def dc_process(date_time, Index, appName, from_date, to_date, impdesc, search):
    servicecalllist=[]
    param_li = []
    es = Elasticsearch(source_ip, port=9200)
    res_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["ServiceCall", "Timestamp", "UniqueParameter", "message"],"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date}}}}, 
                index = Index)
    #Res_data = STAD_process(res_stad)
    counter = Counter()
    for doc in res_stad:
        servicecalllist.append(doc['_source']['ServiceCall'])
        param_li.append(doc['_source']['ServiceCall']+","+doc['_source']['UniqueParameter'])
    uniq_service = set(servicecalllist)
    final_param = []
    for service in uniq_service:
        match_param = [f.split(",")[1] for f in param_li if service.strip() == f.split(",")[0].strip()]
##        print(service+","+str(len(list(set(match_param)))))
        if len(list(set(match_param))) > 0:
            final_param.append(service+","+str(len(list(set(match_param)))))
##        service = "CalculateFixedIncomeOrderInqRq"
            dc_drilldown(date_time, appName, from_date, to_date, service, impdesc, search)
    json_val = "["
    j = 1
    li_len = len(final_param)
    
    dest_filename = "../../../html/Online/" + appName+"_data combination_TP_"+str(date_time)+".csv"
    filename = appName+"_data combination_TP_"+str(date_time)+".csv"
    dest_jsonfilename = "../../../html/Online/" + appName+"_data combination_TP_"+str(date_time)+".json"
    jsonfilename = appName+"_data combination_TP_"+str(date_time)+".json"
    
    usagefile = open(filename,"w")
    jsonfile = open(jsonfilename,"w")
    usagefile.write("id,value\n")
    for key in final_param:
        key_arr = key.split(",")
        if li_len == j:
            json_val = json_val + "{\"axis\":\""+key_arr[0]+"\",\"value\":"+str(key_arr[1])+"}]"
        else:
            json_val = json_val + "{\"axis\":\""+key_arr[0]+"\",\"value\":"+str(key_arr[1])+"},"
        usagefile.write(key+"\n")
        j=j+1
    json_v = "["+json_val + "]"
    usagefile.close()
    jsonfile.write(json_v)
    jsonfile.close()
    shutil.move(filename, dest_filename)
    shutil.move(jsonfilename, dest_jsonfilename)

def dc_drilldown(date_time, appName, from_date, to_date, service, impdesc, search):
    start_datetime = datetime.strptime(from_date,'%Y-%m-%dT%H:%M:%S')
    start_date = start_datetime.strftime("%Y-%m-%d %H:%M")       
    end_datetime = datetime.strptime(to_date,'%Y-%m-%dT%H:%M:%S')
    end_date = end_datetime.strftime("%Y-%m-%d %H:%M")
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    
    pattern_rex = {}
    matched_patterns = ['P8','P3','P9']
    for pattern in matched_patterns:
        query= 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
        regex = con.execute(query).fetchone()[0]
        pattern_rex[pattern]=regex
        
    query = 'SELECT ServiceCall, Timestamp, Status, XML_Data FROM onl_datacombination WHERE ServiceCall = "'+service+'" and App_Name = "'+appName+'" and Timestamp BETWEEN "'+start_date+'" AND "'+end_date+'";'
    response_arr = cur.execute(query).fetchall()
    main_dictParam = {}
    main_dictvalue = {}
    if response_arr:
        for servicecall, Timestamp, Status, XML_Data in response_arr:
            xml_arr = XML_Data.split("~&~")
            soap_arr = []
            flag = 0
            userkey,uservalue = "",""
            param_keys,values_arr1 = [], []
            for line in xml_arr:
                user = re.match(r''+str(pattern_rex['P8'])+'',line)
                soap_start = re.match(r''+str(pattern_rex['P3'])+'',line)
                soap_end = re.match(r''+str(pattern_rex['P9'])+'',line)
                if user:
                    userkey = user['key']
                    uservalue = user['value']
                elif soap_start:
                    param_keys,values_arr1 = [], []
                    flag = 1
                    soap_arr.append(line)
                elif soap_end and flag==1:
                    soap_arr.append(line)
                    timevalue = str(Timestamp)
                    param_keys,values_arr1 = process_req(soap_arr,servicecall)
                    param_keys.insert(0,"Status")
                    values_arr1.insert(0,("status"+":"+"Status",Status))
                    param_keys.insert(1,"Timestamp")
                    values_arr1.insert(1,("timestamp"+":"+"Timestamp",str(Timestamp)))
                    param_keys.insert(2,userkey)
                    values_arr1.insert(2,(userkey.lower()+":"+userkey,uservalue))
                    if not timevalue in main_dictParam.keys():
                        main_dictParam[timevalue] = param_keys
                        main_dictvalue[timevalue] = values_arr1
    ##                    print("~~~timecreat~~")
    ##                    print(servicecall)
    ##                    print(main_dictParam)
                    else:
                        main_dictParam[timevalue]  = main_dictParam[timevalue].extend(param_keys)
                        main_dictvalue[timevalue] = main_dictvalue[timevalue].extend(values_arr1)
    ##                    print("~~~valueadd~~")
    ##                    print(timevalue)
    ##                    print(servicecall)
    ##                    print(main_dictParam)
                    flag = 0
                    soap_arr = []
                    userkey,uservalue = "",""
                    param_keys,values_arr1 = [], []
                elif flag == 1:
                    soap_arr.append(line)
        write_ddcsv(main_dictParam,main_dictvalue,date_time,service,appName, impdesc, search)

def write_ddcsv(main_dictParam,main_dictvalue,date_time,service,appName, impdesc, search):
    param_keys = []
    values_arr = []
    keys = []
    flag = 0
    for time in main_dictParam.keys():
        param_keys.extend(main_dictParam[time])
        key = "&&".join(main_dictParam[time])
        keys.append(key)
        values_arr.append(main_dictvalue[time])
        flag = 1
    if flag == 1:
        flag = 0
        if not os.path.exists("../../../html/Online"):
            os.mkdir("../../../html/Online")
        #print(l)
        movepath = "Online"
        if not search:
            filename = appName+"_"+impdesc.lower()+"_TP_"+service+"_"+str(date_time)+".csv"
        else:
            filename = appName+"_"+impdesc.lower()+"_TP_"+service+"_"+str(search)+"_"+str(date_time)+".csv"
        usagefile = open(filename, 'w')
        seen = set()
        seen_add = seen.add
        head1 =  [x for x in param_keys if not (x in seen or seen_add(x))]
        head = ",".join(head1)
        usagefile.write(head+"\n")
        for value in values_arr:
            str_main = ""
            values = []
            for head_val in head1:
                match_val = [s[1] for s in value if ":"+head_val in s[0]]
##                print(match_val)
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

        


def fa_process(date_time, Index, appName, from_date, to_date):
    servicecalllist=[]
    fail_arr=[]
    dest_filename_all = "../../../html/Online/" + appName+"_failure analysis_All_TP_"+str(date_time)+".csv"
    filename_all = appName+"_failure analysis_All_TP_"+str(date_time)+".csv"
    move_path = "online"
    failurefile_All = open(filename_all,"w")
    failurefile_All.write("Timestamp,UserId,ServiceCall,ErrorCode,ErrorDescription\n")
    es = Elasticsearch(source_ip, port=9200)
                
    res_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["ServiceCall", "Timestamp", "message","ErrorCode","ErrorDescription","UserId"],"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date}}}}, 
                index = Index)
    #Res_data = STAD_process(res_stad)
    counter = Counter()
    for doc in res_stad:
        #print(doc['_source']['ServiceCall'], doc)
        #print(doc['_source']['message'].split(",")[3])
        if not str(doc['_source']['ServiceCall']) == "-":
            fail_arr.append(appName+ "/" +str(doc['_source']['ErrorCode'].split("/")[-1])+ "/" +str(doc['_source']['ServiceCall']))
        else:
            fail_arr.append(appName+ "/" +str(doc['_source']['ErrorCode'].split("/")[-1]))
        failurefile_All.write(str(doc['_source']['Timestamp'])+","+str(doc['_source']['UserId'])+","+str(doc['_source']['ServiceCall'])+","+str(doc['_source']['ErrorCode'])+","+str(doc['_source']['ErrorDescription'])+"\n")
    failurefile_All.close()
    shutil.move(filename_all, dest_filename_all)
    dist_fail_serviceCall = set(fail_arr)
    fail_list=[]
    Err_failure=[]
    dest_filename = "../../../html/Online/" + appName+"_failure analysis_TP_"+str(date_time)+".csv"
    filename = appName+"_failure analysis_TP_"+str(date_time)+".csv"
    move_path = "online"
    failurefile = open(filename,"w")
    failurefile.write("id,value\n")
    Err_failure.append(appName+",")
    for item in dist_fail_serviceCall:
        print(item)
        fail_count = fail_arr.count(item)
        hdr_item="/".join(item.split("/")[:-1])
        print(hdr_item)
        if (hdr_item not in fail_list) and (len(item.split("/")) > 2) and (hdr_item not in dist_fail_serviceCall):
            Err_failure.append(hdr_item+",")
        fail_list.append(hdr_item)
        Err_failure.append(item+","+str(fail_count))
    #Err_failure = set(Err_failure)
    for i in Err_failure:
        failurefile.write(i+"\n")
    failurefile.close()
    shutil.move(filename, dest_filename)

def ufa_process(date_time,Index, appName, from_date, to_date,impdesc,fa_index):
    servicecall=[]
    response_arr = []
    unique_date = []
    es = Elasticsearch(source_ip, port=9200)     
    res_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["Service Call", "Timestamp", "Status","Response time(ms)"],"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date}}}}, 
                index = Index)
    #Res_data = STAD_process(res_stad)
    counter = Counter()
    text_filename = "../../../html/Online/" + appName+"_"+impdesc.lower()+"_TP_fail_response_"+str(date_time)+".txt"
    dest_filename = "../../../html/Online/" + appName+"_"+impdesc.lower()+"_TP_AllFailures_"+str(date_time)+".csv"
    filename = appName+"_"+impdesc.lower()+"_TP_Usage_"+str(search)+"_"+str(date_time)+".csv"
    usagefile = open(filename,"w")
    usagefile.write("Day,ServiceCall,Count,Status,FailureCount\n")
    for doc in res_stad:
        response_arr.append(doc['_source']['Service Call']+","+doc['_source']['Timestamp']+","+doc['_source']['Status']+","+doc['_source']['Response time(ms)'])
        servicecall.append(doc['_source']['Timestamp'].split("T")[0]+"_"+doc['_source']['Service Call'])
    uniq_servicecall = set(servicecall)
    text_file = open(text_filename, "w")    
    start_datetime = datetime.strptime(from_date,'%Y-%m-%dT%H:%M:%S')
    start_date = start_datetime.strftime("%m/%d/%y %H:%M")       
    end_datetime = datetime.strptime(to_date,'%Y-%m-%dT%H:%M:%S')
    end_date = end_datetime.strftime("%m/%d/%y %H:%M")
    text_file.write("StartDate - " + str(start_date)+"\n")
    text_file.write("EndDate - " + str(end_date)+"\n")
    text_file.write("Unique date - \n")
    for service_req1 in uniq_servicecall:
##        print(service_req1)
        failcfilename = service_req1.split("-")[2]
        service_req = service_req1.split("_")[1]
        ufa_stad = elasticsearch.helpers.scan(
            client = es,
            scroll = '2m',
            query = {"_source":["Timestamp","ServiceCall","ErrorCode","ErrorDescription","UserId"],"query":{ "bool":{ "must":[ { "match":{ "ServiceCall":service_req.strip() } }, { "range":{ "Timestamp":{ "gte":from_date, "lt":to_date }  }}]}}}, 
            index = fa_index)
        match_stad = []
        curr_serdate = service_req1.split("_")[0]
##        print(curr_serdate)
        for f in ufa_stad:
            if f['_source']['Timestamp'] and (curr_serdate in str(f['_source']['Timestamp'])):
                match_stad.append(f)
        if match_stad:
##            print(match_stad)
            onlfilename = "../../../html/Online/" + appName+"_"+impdesc.lower()+"_TP_"+str(failcfilename)+"_"+str(date_time)+".csv"
            failure_item_file = open(onlfilename,"w")
            failure_item_file.write("Datetime,Userid,ErrorCode,ErrorDescription\n")
            for fail_doc in match_stad:
                failure_item_file.write(fail_doc['_source']['Timestamp']+","+fail_doc['_source']['UserId']+","+fail_doc['_source']['ErrorCode']+","+fail_doc['_source']['ErrorDescription']+"\n")
            failure_item_file.close()
        uniqueDate = (str(service_req1.split("_")[0]))
        if uniqueDate not in unique_date:
            unique_date.append(uniqueDate)
        match_response = [int(s.split(",")[3]) for s in response_arr if (service_req == s.split(",")[0]) and (curr_serdate in s.split(",")[1])]
        match_pass = [s.split(",")[2] for s in response_arr if (service_req == s.split(",")[0]) and (curr_serdate in s.split(",")[1]) and ("Pass" == s.split(",")[2])]
        match_fail = [s.split(",")[2] for s in response_arr if (service_req == s.split(",")[0])  and (curr_serdate in s.split(",")[1]) and ("Fail" == s.split(",")[2])]
        match_avg = [int(s.split(",")[3]) for s in response_arr if (service_req == s.split(",")[0])  and (curr_serdate in s.split(",")[1]) and ("Pass" == s.split(",")[2])]
##        print(match_fail)
        cou_res = sum(match_response)
        if match_avg:
            min_res = min(match_avg)
            max_res = max(match_avg)
            cou_pass_avg = sum(match_avg)
            avg_pass = cou_pass_avg/len(match_avg)
        else:
            min_res = 0
            max_res = 0
            avg_pass = 0
        cou_pass = len(match_pass)
        cou_fail = len(match_fail)

        match_pass = Counter(match_pass)
        match_fail = Counter(match_fail)
        pass_fail = str(match_pass['Pass'])+"/"+str(len(match_response))
        Status = ""
        if not match_fail:
            Status = "low"
        elif(round(int(match_fail['Fail'])/len(match_response)*100, 2) > 26):
            Status = "high"
        else:
            Status = "medium"
        curr_serdate = datetime.strptime(curr_serdate,'%Y-%m-%d')
        curr_serdate = datetime.strftime(curr_serdate,'%m/%d/%y')        
        if not match_fail:
            usagefile.write(str(curr_serdate)+","+str(service_req)+","+str(len(match_response))+","+Status+","+str(int(0))+"\n")
        else:
            print(str(curr_serdate)+","+str(service_req))
            usagefile.write(str(curr_serdate)+","+str(service_req)+","+str(len(match_response))+","+Status+","+str(int(match_fail['Fail']))+"\n")
    usagefile.close()
    shutil.move(filename, dest_filename)
    for date in unique_date:
        date = datetime.strptime(date,'%Y-%m-%d')
        text_file.write(str(datetime.strftime(date, '%#m/%#d/%y')).split(" ")[0] + "\n")
        print(str(datetime.strftime(date, '%#m/%#d/%y')).split(" ")[0]) 
    text_file.close()

def nfv_process(date_time,Index, appName, from_date, to_date,impdesc):
    servicecall=[]
    response_arr = []
    std_nfv = []
    custom_nfv = []
    es = Elasticsearch(source_ip, port=9200)     
    res_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["Service Call","User ID","Timestamp","Status","Response time(ms)"],"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date}}}}, 
                index = Index)
    #Res_data = STAD_process(res_stad)
    counter = Counter()    
    dest_filename = "../../../html/Online/" + appName+"_"+impdesc.lower()+"_TP_"+str(date_time)+".csv"
    dest_filename1 = "../../../html/Online/" + appName+"_"+impdesc.lower()+"_TP_All_"+str(date_time)+".csv"
    filename = appName+"_"+impdesc.lower()+"_TP_"+str(date_time)+".csv"
    filename1 = appName+"_"+impdesc.lower()+"_TP_All_"+str(date_time)+".csv"
    usagefile = open(filename,"w")
    usagefile1 = open(filename1,"w")
    usagefile.write("Service Call,Total Count,Pass Count,Fail Count,Min. Response time(ms),Max. Response time(ms),Avg. Response time(ms),Standard Deviation(ms)\n")
    usagefile1.write("Service Call,Total Count,Pass Count,Fail Count,Min. Response time(ms),Max. Response time(ms),Avg. Response time(ms),Standard Deviation(ms)\n")
    for doc in res_stad:
        response_arr.append(doc['_source']['Service Call']+","+doc['_source']['User ID']+","+doc['_source']['Status']+","+doc['_source']['Response time(ms)'])
        servicecall.append(doc['_source']['Service Call'])
    uniq_servicecall = set(servicecall)
    for service_req in uniq_servicecall:
        service_req1 = re.sub(r'[<>{}]','',service_req)
        onlfilename = "../../../html/Online/" + appName+"_"+impdesc.lower()+"_TP_"+str(service_req1)+"_"+str(date_time)+".csv"
        nfv_item_file = open(onlfilename,"w")
        match_response = [int(s.split(",")[3]) for s in response_arr if service_req == s.split(",")[0]]
        match_pass = [s for s in response_arr if (service_req == s.split(",")[0]) and ("Pass" == s.split(",")[2])]
        match_fail = [s for s in response_arr if (service_req == s.split(",")[0]) and ("Fail" == s.split(",")[2])]
        
        if match_pass or match_fail:
            nfv_item_file.write("Timestamp,Userid,Status,Response time(ms)\n")
            match_avg = [int(s.split(",")[3]) for s in response_arr if (service_req == s.split(",")[0]) and ("Pass" == s.split(",")[2])]
        else:
            nfv_item_file.write("Timestamp,Response time(ms)\n")
            match_avg = [int(s.split(",")[3]) for s in response_arr if (service_req == s.split(",")[0])]

        nfv_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source":["Timestamp", "User ID","Status","Response time(ms)"],"query":{ "bool":{ "must":[ { "match":{ "Service Call":service_req.strip() } }, { "range":{ "Timestamp":{ "gte":from_date, "lt":to_date }  }}]}}},  
                index = Index)
        for nfv_doc in nfv_stad:
            if match_pass or match_fail:
                nfv_item_file.write(nfv_doc['_source']['Timestamp']+","+nfv_doc['_source']['User ID']+","+nfv_doc['_source']['Status']+","+nfv_doc['_source']['Response time(ms)']+"\n")
            else:
                nfv_item_file.write(nfv_doc['_source']['Timestamp']+","+nfv_doc['_source']['Response time(ms)']+"\n")
        nfv_item_file.close()
        
        cou_res = sum(match_response)
        if match_avg:
            min_res = min(match_avg)
            max_res = max(match_avg)
            cou_pass_avg = sum(match_avg)
            avg_pass = cou_pass_avg/len(match_avg)
        else:
            min_res = 0
            max_res = 0
            avg_pass = 0
        if len(match_avg) > 1:
            std_dev = stdev(match_avg)
            std_dev_str = str(round(std_dev,2))
        else:
            std_dev_str = str(0)
        cou_pass = len(match_pass)
        cou_fail = len(match_fail)
        if match_pass or match_fail:
            std_nfv.append(service_req1+","+str(len(match_response))+","+str(cou_pass)+","+str(cou_fail)+","+str(round(min_res,2))+","+str(round(max_res,2))+","+str(round(avg_pass,2))+","+std_dev_str)
            #usagefile.write(service_req1+","+str(len(match_response))+","+str(cou_pass)+","+str(cou_fail)+","+str(round(min_res,2))+","+str(round(max_res,2))+","+str(round(avg_pass,2))+","+std_dev_str+"\n")
        else:
            custom_nfv.append(service_req1+","+str(len(match_response))+","+"-"+","+"-"+","+str(round(min_res,2))+","+str(round(max_res,2))+","+str(round(avg_pass,2))+","+std_dev_str)
            #usagefile.write(service_req1+","+str(len(match_response))+","+"-"+","+"-"+","+str(round(min_res,2))+","+str(round(max_res,2))+","+str(round(avg_pass,2))+","+std_dev_str+"\n")
    sorted_arr = sorted(custom_nfv,key = lambda x: float(x.split(",")[6]),reverse=True)
    fin_arr = []
    fin_arr.extend(std_nfv)
    fin_arr.extend(sorted_arr[:20])
    full_arr = []
    full_arr.extend(std_nfv)
    full_arr.extend(sorted_arr)
    for val in fin_arr:
        usagefile.write(val+"\n")
    usagefile.close()
    for val in full_arr:
        usagefile1.write(val+"\n")
    usagefile1.close()
    shutil.move(filename, dest_filename)
    shutil.move(filename1, dest_filename1)

def search_UAprocess(date_time,Index, appName, from_date, to_date,impdesc,search,uniq_service):
    servicecall=[]
    response_arr = []
    es = Elasticsearch(source_ip, port=9200)     
    res_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["Service Call", "Timestamp", "User ID","Status","Response time(ms)"],"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date}}}}, 
                index = Index)
    #Res_data = STAD_process(res_stad)
    counter = Counter()    
    dest_filename = "../../../html/Online/" + appName+"_"+impdesc.lower()+"_TP_Usage_"+str(search)+"_"+str(date_time)+".csv"
    filename = appName+"_"+impdesc.lower()+"_TP_Usage_"+str(search)+"_"+str(date_time)+".csv"
    usagefile = open(filename,"w")
    usagefile.write("Service Call,Total Count,Pass Count,Fail Count,Min. Response time(ms),Max. Response time(ms),Avg. Response time(ms)\n")
    for doc in res_stad:
        response_arr.append(doc['_source']['Service Call']+","+doc['_source']['User ID']+","+doc['_source']['Status']+","+doc['_source']['Response time(ms)'])
##        servicecall.append(doc['_source']['Service Call'])
##    uniq_servicecall = set(servicecall)
    for service_req in uniq_service:
        match_response = [int(s.split(",")[3]) for s in response_arr if service_req == s.split(",")[0]]
        match_pass = [s for s in response_arr if (service_req == s.split(",")[0]) and ("Pass" == s.split(",")[2])]
        match_fail = [s for s in response_arr if (service_req == s.split(",")[0]) and ("Fail" == s.split(",")[2])]
        match_avg = [int(s.split(",")[3]) for s in response_arr if (service_req == s.split(",")[0]) and ("Pass" == s.split(",")[2])]
        
        cou_res = sum(match_response)
        if match_avg:
            min_res = min(match_avg)
            max_res = max(match_avg)
            cou_pass_avg = sum(match_avg)
            avg_pass = cou_pass_avg/len(match_avg)
        else:
            min_res = 0
            max_res = 0
            avg_pass = 0
        cou_pass = len(match_pass)
        cou_fail = len(match_fail)
        usagefile.write(service_req+","+str(len(match_response))+","+str(cou_pass)+","+str(cou_fail)+","+str(round(min_res,2))+","+str(round(max_res,2))+","+str(round(avg_pass,2))+"\n")
    usagefile.close()
    shutil.move(filename, dest_filename)

def search_DCprocess(date_time,appName, from_date, to_date,impdesc,search):
    start_datetime = datetime.strptime(from_date,'%Y-%m-%dT%H:%M:%S')
    start_date = start_datetime.strftime("%Y-%m-%d %H:%M")       
    end_datetime = datetime.strptime(to_date,'%Y-%m-%dT%H:%M:%S')
    end_date = end_datetime.strftime("%Y-%m-%d %H:%M")
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    
    pattern_rex = {}
    matched_patterns = ['P8','P3','P9','P28','P29']
    for pattern in matched_patterns:
        query= 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
        regex = con.execute(query).fetchone()[0]
        pattern_rex[pattern]=regex
    query_servicecall = 'SELECT ServiceCall FROM onl_datacombination WHERE App_Name = "'+appName+'" and Timestamp BETWEEN "'+start_date+'" AND "'+end_date+'";'
    service_arr = cur.execute(query_servicecall).fetchall()
    service_arr = [f[0] for f in service_arr]
    uniq_service = set(service_arr)
    search_sCall = []
    head_arr = []
    for service in uniq_service:
        query = 'SELECT ServiceCall, Timestamp, Status, XML_Data FROM onl_datacombination WHERE ServiceCall = "'+service+'" and App_Name = "'+appName+'" and Timestamp BETWEEN "'+start_date+'" AND "'+end_date+'";'
        response_arr = cur.execute(query).fetchall()
        main_dictParam = {}
        main_dictvalue = {}
        if response_arr:
            for servicecall, Timestamp, Status, XML_Data in response_arr:
                xml_arr = XML_Data.split("~&~")
                soap_arr = []
                flag = 0
                head_flag = 0
                userkey,uservalue = "",""
                isheader = False
                param_keys,values_arr1 = [], []
                for line in xml_arr:
                    user = re.match(r''+str(pattern_rex['P8'])+'',line)
                    soap_start = re.match(r''+str(pattern_rex['P3'])+'',line)
                    soap_end = re.match(r''+str(pattern_rex['P9'])+'',line)
                    head_start = re.match(r''+str(pattern_rex['P28'])+'',line)
                    head_end = re.match(r''+str(pattern_rex['P29'])+'',line)
                    if head_start:
                        head_flag = 1
                    elif user and head_flag == 1:
                        userkey = user['key']
                        uservalue = user['value']
                        if search.strip() == uservalue.strip():
                            isheader = True
                            head_arr.append(userkey)
                    elif head_end and head_flag == 1:
                        head_flag = 2
                    elif soap_start and head_flag == 2:
                        param_keys,values_arr1 = [], []
                        flag = 1
                        soap_arr.append(line)
                    elif soap_end and (flag == 1) and isheader:
                        search_sCall.append(service)
                        soap_arr.append(line)
                        timevalue = str(Timestamp)
                        param_keys,values_arr1 = process_req(soap_arr,servicecall)
                        param_keys.insert(0,"Status")
                        values_arr1.insert(0,("status"+":"+"Status",Status))
                        param_keys.insert(1,"Timestamp")
                        values_arr1.insert(1,("timestamp"+":"+"Timestamp",str(Timestamp)))
                        param_keys.insert(2,userkey)
                        values_arr1.insert(2,(userkey.lower()+":"+userkey,uservalue))
                        if not timevalue in main_dictParam.keys():
                            main_dictParam[timevalue] = param_keys
                            main_dictvalue[timevalue] = values_arr1
        ##                    print("~~~timecreat~~")
        ##                    print(servicecall)
        ##                    print(main_dictParam)
                        else:
                            main_dictParam[timevalue]  = main_dictParam[timevalue].extend(param_keys)
                            main_dictvalue[timevalue] = main_dictvalue[timevalue].extend(values_arr1)
        ##                    print("~~~valueadd~~")
        ##                    print(timevalue)
        ##                    print(servicecall)
        ##                    print(main_dictParam)
                        flag = 0
                        soap_arr = []
                        head_flag = 0
                        userkey,uservalue = "",""
                        param_keys,values_arr1 = [], []
                    elif flag == 1:
                        soap_arr.append(line)
                        if ">"+search.strip()+"</" in line:
                            isheader = True
                            head_txt = line.split("</")[1].split(">")[0]
                            if ":" in head_txt:
                                head_txt = head_txt.split(":")[1]
                            head_arr.append(head_txt)
                    elif head_flag == 1 :
                        if ">"+search.strip()+"</" in line:
                            isheader = True
                            head_txt = line.split("</")[1].split(">")[0]
                            if ":" in head_txt:
                                head_txt = head_txt.split(":")[1]
                            head_arr.append(head_txt)
            if head_arr:
                write_ddcsv(main_dictParam,main_dictvalue,date_time,service,appName,impdesc,search)
    return set(head_arr),set(search_sCall)
        
def hmprocess(date_time,Index, appName, from_date, to_date,impdesc):
    es_timestamp = "%Y-%m-%dT%H:%M:%S.%fZ" 
    convert_timestamp = "%Y-%m-%d %H:%M:%S"
    es = Elasticsearch(source_ip, port=9200)
    res_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                #query = {"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date,"time_zone": "+05:30"}}}},
                query = {"query": {"range": {"Timestamp":{"gte":from_date, "lt":to_date}}}},
                index = Index)
    start_flag = 0
    if res_stad:
        used_text = ""
        tenure_text = ""
        nursery_text = ""
        GC_text = ""
        for doc in res_stad:
            if start_flag == 0:
                start_flag = 1
                d = datetime.strptime(str(doc['_source']['Timestamp']), es_timestamp)
                timestamp = datetime.strftime(d, convert_timestamp)
                used_text = "{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(doc['_source']['Used Tenured(After)'])+"}"
                tenure_text = "{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(doc['_source']['Free Tenured(After)'])+"}"
                nursery_text = "{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(doc['_source']['Free Nursery(After)'])+"}"
                GC_text = "{\"DateTime\":\""+str(timestamp)+"\",\"GC\":"+str(doc['_source']['GC Completed'])+"}"
            else:
                d = datetime.strptime(str(doc['_source']['Timestamp']), es_timestamp)
                timestamp = datetime.strftime(d, convert_timestamp)
                used_text = used_text+",{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(doc['_source']['Used Tenured(After)'])+"}"
                tenure_text =  tenure_text+",{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(doc['_source']['Free Tenured(After)'])+"}"
                nursery_text = nursery_text+",{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(doc['_source']['Free Nursery(After)'])+"}"
                GC_text = GC_text+",{\"DateTime\":\""+str(timestamp)+"\",\"GC\":"+str(doc['_source']['GC Completed'])+"}"
        if GC_text:
            if not os.path.exists("../../../html/Online"):
                os.mkdir("../../../html/Online")
            common_fileName = appName+"_"+impdesc.lower()+"_HeapMemory_TP_"+str(date_time)
            dir_path = "../../../html/Online"
            txt_filename = common_fileName + ".txt"
            usagefile_txt = open(txt_filename,"w")
            usagefile_txt.write("Used Tenured(After)=")
            usagefile_txt.write(used_text)
            usagefile_txt.write("\nFree Tenured(After)=")
            usagefile_txt.write(tenure_text)
            usagefile_txt.write("\nFree Nursery(After)=")
            usagefile_txt.write(nursery_text)
            usagefile_txt.write("\nGC Completed=")
            usagefile_txt.write(GC_text)
            usagefile_txt.close()
            shutil.move(txt_filename, dir_path+"/"+txt_filename)


def getImperatives(appName):
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    query = 'SELECT Imp_Id from Online_Imperative_Info where App_NAME = "'+appName+'";'
    response_arr = cursor.execute(query).fetchall()
##                matched_pat_list = response_arr[0].split(',')
    imp_ids_desc = []
    imp_ids = []
    response_arr = [f[0] for f in response_arr]
    response_arr= set(response_arr)
    for impid in response_arr:
        query1 = 'SELECT IMP_DESCRIPTION from imperative_info where IMP_ID = "'+impid+'";'
        imp_name = cursor.execute(query1).fetchone()[0]
        imp_ids.append(str(impid))
        imp_ids_desc.append(str(impid)+"-"+imp_name)
    return imp_ids,imp_ids_desc

    
# main function
if __name__ == "__main__":
       print("Content-type: text/html \n");
       form = cgi.FieldStorage()
       appName = sys.argv[4]
       from_date = sys.argv[10]
       to_date = sys.argv[11]
       search = sys.argv[12]
       time = datetime.now()
       print(time)
       time_main = re.sub(r'[:.]','-',str(time))
       date_time = str(time).split(" ")[0]
##       appName = "TWA"
##       from_date = "2019-01-15T00:00:00"
##       to_date = "2019-05-07T19:59:59"
##       search = ""
       if sys.argv[12] == "empty":
           search = ""
       else:
           search = sys.argv[12]
       #Stad Log
       imp_ids,imp_ids_desc = getImperatives(appName)
       for impid_des in imp_ids_desc:
            print(impid_des)
            impid,impdesc = impid_des.split("-")
            if not search:
                if impid == "IMP001":
                    ua_index = "ua"
                    usage_process(date_time, ua_index, appName, from_date, to_date)
                elif impid == "IMP002":
                    dc_index = "dcall"
                    dc_process(date_time, dc_index, appName, from_date, to_date, impdesc, search)
                elif impid == "IMP003":
                    fa_index = "faall"
                    fa_process(date_time,fa_index, appName, from_date, to_date)
                if impid == "IMP004":
                    hm_index = "hm"
                    hmprocess(date_time,hm_index, appName, from_date, to_date, impdesc)
                elif impid == "IMP005":
                    nfv_index = "nfv"
                    nfv_process(date_time,nfv_index, appName, from_date, to_date,impdesc)
                elif impid == "IMP006":
                    fa_index = "faall"
                    ufa_index = "sua"
                    ufa_process(date_time,ufa_index, appName, from_date, to_date, impdesc, fa_index)
            elif impid == "IMP008" and search:
                sua_index = "sua"
                header_arr,uniq_service = search_DCprocess(date_time,appName, from_date, to_date,impdesc,search)
##                print(uniq_service)
                print(header_arr)
                if uniq_service and header_arr:
                    search_UAprocess(date_time,sua_index, appName, from_date, to_date,impdesc,search,uniq_service)
                    print(uniq_service)
                
       print(datetime.now())
       print("succesfully Inserted")
