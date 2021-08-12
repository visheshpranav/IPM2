import cgi, cgitb
import os,re,shutil,openpyxl
import configparser
import pyodbc,datetime
from elasticsearch import Elasticsearch
import elasticsearch.helpers
from collections import Counter
from datetime import datetime

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
source_ip = parser.get('Report','ipaddress')
ONL_Report = parser.get('Report','onlpathES')
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

def usage_process(date_time, Index, app_name, from_date, to_date):
    servicecalllist=[]
    es = Elasticsearch(source_ip, port=9200)  
                
    res_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["ServiceCall", "Timestamp", "message"],"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date}}}}, 
                index = Index)
    #Res_data = STAD_process(res_stad)
    counter = Counter()    
    dest_filename = "../../../html/Online/" + app_name+"_usage analysis_TP_"+str(date_time)+".csv"
    filename = app_name+"_usage analysis_TP_"+str(date_time)+".csv"
    for doc in res_stad:
        #print(doc['_source']['ServiceCall'])
        servicecalllist.append(doc['_source']['ServiceCall'])
    counter = Counter(servicecalllist)
    usagefile = open(filename,"w")
    usagefile.write("id,value\n")
    for key in dict(counter):
        print(key,dict(counter)[key])
        usagefile.write(key+","+str(dict(counter)[key])+"\n")
    usagefile.close()
    shutil.move(filename, dest_filename)

def dc_process(date_time, Index, app_name, from_date, to_date, drill_index):
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
        print(service+","+str(len(list(set(match_param)))))
        if len(list(set(match_param))) > 0:
            final_param.append(service+","+str(len(list(set(match_param)))))
##        service = "CalculateFixedIncomeOrderInqRq"
            dc_drilldown(date_time, drill_index, app_name, from_date, to_date, service)
    json_val = "["
    j = 1
    li_len = len(final_param)
    
    dest_filename = "../../../html/Online/" + app_name+"_data combination_TP_"+str(date_time)+".csv"
    filename = app_name+"_data combination_TP_"+str(date_time)+".csv"
    dest_jsonfilename = "../../../html/Online/" + app_name+"_data combination_TP_"+str(date_time)+".json"
    jsonfilename = app_name+"_data combination_TP_"+str(date_time)+".json"
    
    usagefile = open(filename,"w")
    jsonfile = open(jsonfilename,"w")
    usagefile.write("id,value\n")
    for key in final_param:
        print(key)
        key_arr = key.split(",")
        print(li_len, j)
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

def dc_drilldown(date_time, Index, app_name, from_date, to_date, service):
    es = Elasticsearch(source_ip, port=9200)
    res_data = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                #query = {"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date,"time_zone": "+05:30"}}}},
                query = {"query": {"bool": {"must": [{"match": {"serviceCall": service.strip() }}],"filter": {"range": {"TimeStamp":{"gte":from_date, "lt":to_date}}}}}},
                index = Index)
    res_head = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                #query = {"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date,"time_zone": "+05:30"}}}},
                query = {"query": {"bool": {"must": [{"match": {"serviceCall": service.strip() }}],"filter": {"range": {"TimeStamp":{"gte":from_date, "lt":to_date}}}}}},
                index = Index)
    if res_stad:
        key_head = ""
        val_arr = []
        del_list = ['path','serviceCall','type','message','host','@version','@timestamp',]
        for doc in res_stad:
##            print(doc['_source'])
            for del_key in del_list:
                try:
                    del doc['_source'][del_key]
                except KeyError:
                    pass
            keys = list(doc['_source'].keys())
##            print(keys)
            keys.remove('Status')
            keys.remove('TimeStamp')
            keys.remove('UserID')
            keys.insert(0,'Status')
            keys.insert(1,'TimeStamp')
            keys.insert(2,'UserID')
            key_head = ",".join(keys)
            values = ""
            i = 0
            for key in keys:
                if i==0:
                    values = str(doc['_source'][key])
                else:
                    values = values+","+str(doc['_source'][key])
                i = i+1
            val_arr.append(values)
        if val_arr:
            dest_filename = "../../../html/Online/" + app_name+"_data combination_TP_"+service+"_"+str(date_time)+".csv"
            filename = app_name+"_data combination_TP_"+service+"_"+str(date_time)+".csv"
            move_path = "online"
            dcdrillfile = open(filename,"w")
            dcdrillfile.write(key_head+"\n")
            for value in val_arr:
                dcdrillfile.write(value+"\n")
            dcdrillfile.close()
            shutil.move(filename, dest_filename)
        


def fa_process(date_time, Index, app_name, from_date, to_date):
    servicecalllist=[]
    fail_arr=[]
    es = Elasticsearch(source_ip, port=9200)
                
    res_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["ServiceCall", "Timestamp", "message"],"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date}}}}, 
                index = Index)
    #Res_data = STAD_process(res_stad)
    counter = Counter()
    for doc in res_stad:
        #print(doc['_source']['ServiceCall'], doc)
        #print(doc['_source']['message'].split(",")[3])
        fail_arr.append(app_name+ "/" +str(doc['_source']['message'].split(",")[3])+ "/" +str(doc['_source']['ServiceCall']))
    dist_fail_serviceCall = set(fail_arr)
    print(dist_fail_serviceCall)
    fail_list=[]
    Err_failure=[]
    dest_filename = "../../../html/Online/" + app_name+"_failure analysis_TP_"+str(date_time)+".csv"
    filename = app_name+"_failure analysis_TP_"+str(date_time)+".csv"
    move_path = "online"
    failurefile = open(filename,"w")
    failurefile.write("id,value\n")
    Err_failure.append(app_name+",")
    for item in dist_fail_serviceCall:
        fail_count = fail_arr.count(item)
        hdr_item="/".join(item.split("/")[:-1])
        if hdr_item not in fail_list:
            Err_failure.append(hdr_item+",")
        fail_list.append(hdr_item)
        Err_failure.append(item+","+str(fail_count))
    
    for i in Err_failure:
        failurefile.write(i+"\n")
    failurefile.close()
    shutil.move(filename, dest_filename)

def ufa_process(date_time,Index, app_name, from_date, to_date,impdesc,fa_index):
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
    text_filename = "../../../html/Online/" + app_name+"_"+impdesc.lower()+"_TP_fail_response_"+str(date_time)+".txt"
    dest_filename = "../../../html/Online/" + app_name+"_"+impdesc.lower()+"_TP_AllFailures"+str(date_time)+".csv"
    filename = app_name+"_"+impdesc.lower()+"_TP_Usage_"+str(search)+"_"+str(date_time)+".csv"
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
    for service_req in uniq_servicecall:
        onlfilename = "../../../html/Online/" + app_name+"_"+impdesc.lower()+"_TP_"+str(service_req.split("_")[1])+"_"+str(date_time)+".csv"
        failure_item_file = open(onlfilename,"w")
        failure_item_file.write("Datetime,Userid,ErrorCode,ErrorDescription\n")
        ufa_stad = elasticsearch.helpers.scan(
            client = es,
            scroll = '2m',
            query = {"_source":["Timestamp","ServiceCall","ErrorCode","ErrorDescription","UserId"],"query":{ "bool":{ "must":[ { "match":{ "ServiceCall":service_req.strip() } }, { "range":{ "Timestamp":{ "gte":from_date, "lt":to_date }  }}]}}}, 
            index = fa_index)
        for fail_doc in ufa_stad:
            failure_item_file.write(fail_doc['_source']['Timestamp']+","+fail_doc['_source']['UserId']+","+fail_doc['_source']['ErrorCode']+","+fail_doc['_source']['ErrorDescription']+"\n")
        failure_item_file.close()
        uniqueDate = (str(service_req.split("_")[0]))
        if uniqueDate not in unique_date:
            unique_date.append(uniqueDate)
        match_response = [int(s.split(",")[3]) for s in response_arr if service_req.split("_")[1] == s.split(",")[0]]
        match_pass = [s.split(",")[2] for s in response_arr if (service_req.split("_")[1] == s.split(",")[0]) and ("Pass" == s.split(",")[2])]
        match_fail = [s.split(",")[2] for s in response_arr if (service_req.split("_")[1] == s.split(",")[0]) and ("Fail" == s.split(",")[2])]
        match_avg = [int(s.split(",")[3]) for s in response_arr if (service_req.split("_")[1] == s.split(",")[0]) and ("Pass" == s.split(",")[2])]
        
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
        pass_fail = str(match_pass['Pass'])+"/"+str(len(match_response))
        Status = ""
        if(str(match_pass['1']) == "Fail"):
            Status = "low"
        elif(round(int(match_pass['1'])/len(match_response)*100, 2) > 26):
            Status = "high"
        else:
            Status = "medium"
            
        usagefile.write(str(service_req.split("_")[1])+","+str(service_req.split("_")[0])+","+str(len(match_response))+","+Status+","+str(int(match_pass['Pass']))+"\n")
    usagefile.close()
    shutil.move(filename, dest_filename)
    for date in unique_date:
        date = datetime.strptime(date,'%Y-%m-%d')
        text_file.write(str(datetime.strftime(date, '%#m/%#d/%y')).split(" ")[0] + "\n")
        print(str(datetime.strftime(date, '%#m/%#d/%y')).split(" ")[0]) 
    text_file.close()

def nfv_process(date_time,Index, app_name, from_date, to_date,impdesc):
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
    dest_filename = "../../../html/Online/" + app_name+"_"+impdesc.lower()+"_TP_"+str(date_time)+".csv"
    filename = app_name+"_"+impdesc.lower()+"_TP_"+str(date_time)+".csv"
    usagefile = open(filename,"w")
    usagefile.write("Service Call,Total Count,Pass Count,Fail Count,Min. Response time(ms),Max. Response time(ms),Avg. Response time(ms)\n")
    for doc in res_stad:
        response_arr.append(doc['_source']['Service Call']+","+doc['_source']['User ID']+","+doc['_source']['Status']+","+doc['_source']['Response time(ms)'])
        servicecall.append(doc['_source']['Service Call'])
    uniq_servicecall = set(servicecall)
    for service_req in uniq_servicecall:
        onlfilename = "../../../html/Online/" + app_name+"_"+impdesc.lower()+"_TP_"+str(service_req)+"_"+str(date_time)+".csv"
        nfv_item_file = open(onlfilename,"w")
        nfv_item_file.write("Timestamp,Userid,Status,Response time(ms)\n")
        nfv_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source":["Timestamp", "User ID","Status","Response time(ms)"],"query":{ "bool":{ "must":[ { "match":{ "Service Call":service_req.strip() } }, { "range":{ "Timestamp":{ "gte":from_date, "lt":to_date }  }}]}}},  
                index = Index)
        for nfv_doc in nfv_stad:
            nfv_item_file.write(nfv_doc['_source']['Timestamp']+","+nfv_doc['_source']['User ID']+","+nfv_doc['_source']['Status']+","+nfv_doc['_source']['Response time(ms)']+"\n")
        nfv_item_file.close()
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

def search_UAprocess(date_time,Index, app_name, from_date, to_date,impdesc,search,uniq_service):
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
    dest_filename = "../../../html/Online/" + app_name+"_"+impdesc.lower()+"_TP_Usage_"+str(search)+"_"+str(date_time)+".csv"
    filename = app_name+"_"+impdesc.lower()+"_TP_Usage_"+str(search)+"_"+str(date_time)+".csv"
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

def search_DCprocess(date_time,Index, app_name, from_date, to_date,impdesc, search):
    header_arr = []
    uniq_service = []
    main_dict = {}
    es = Elasticsearch(source_ip, port=9200)
    res_stad = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                #query = {"query": {"range" : {"Timestamp":{"gte":from_date, "lt":to_date,"time_zone": "+05:30"}}}},
                query = {"query": {"range": {"TimeStamp":{"gte":from_date, "lt":to_date}}}},
                index = Index)
    if res_stad:
        head_arr = []
        service_req = ""
        val_arr = []
        service_arr = []
        for doc in res_stad:
            for (key,value) in doc['_source'].items():
                if ('serviceCall' in doc['_source'].keys()) and (re.match(r'.*[-]{1}'+search+'[\/]{1}.*',value)):
                    if not key == "message":
                        header_arr.append(key)
            if header_arr:
                del_list = ['path','serviceCall','type','message','host','@version','@timestamp',]
                for del_key in del_list:
                    try:
                        if del_key == "serviceCall":
                            service_req = doc['_source'][del_key]
                        del doc['_source'][del_key]
                    except KeyError:
                        pass
                keys = list(doc['_source'].keys())
##              print(keys)
                values = ""
                header = ""
                i = 0
                values1 =str(doc['_source']['Status'])+","+ str(doc['_source']['TimeStamp'])+","+str(doc['_source']['UserID'])
                header = "Status,TimeStamp,UserID"
                keys.remove('Status')
                keys.remove('TimeStamp')
                keys.remove('UserID')
                key_head = ",".join(keys)
                service_arr.append(service_req)
                for key in keys:
                    key_ar = key.split("-")
                    if key_ar[0] == "body":
                        if "body-" in doc['_source'][key]:
                            val_ES = re.sub("body-","",str(doc['_source'][key]))
                            values1 = values1+","+str(val_ES)
                            header = header+","+key.split("-")[1]
                    i = i+1
                if service_req in main_dict.keys():
                    main_dict[service_req]['values'].append(values1)
                else:
                    main_dict[service_req] = {}
                    main_dict[service_req]['head'] = header
                    main_dict[service_req]['values'] = []
                    main_dict[service_req]['values'].append(values1)
        uniq_service = set(service_arr)
        for ser_req in uniq_service:
            data_arr = main_dict[ser_req]['values']
            head = main_dict[ser_req]['head']
            if data_arr and head:
                dest_filename = "../../../html/Online/" + app_name+"_"+impdesc.lower()+"_TP_"+ser_req+"_"+str(search)+"_"+str(date_time)+".csv"
                filename = app_name+"_"+impdesc.lower()+"TP_"+ser_req+"_"+str(search)+"_"+str(date_time)+".csv"
                move_path = "online"
                dcdrillfile = open(filename,"w")
                dcdrillfile.write(head+"\n")
                for value in data_arr:
                    dcdrillfile.write(value+"\n")
                dcdrillfile.close()
                shutil.move(filename, dest_filename)
    return header_arr,uniq_service
        
def hmprocess(date_time,Index, app_name, from_date, to_date,impdesc):
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
            common_fileName = app_name+"_"+impdesc.lower()+"_HeapMemory_TP_"+str(date_time)
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
    query = 'SELECT Imp_Id from Online_Imperative_Info where App_Name = "'+appName+'";'
    response_arr = cursor.execute(query).fetchall()
##                matched_pat_list = response_arr[0].split(',')
    imp_ids_desc = []
    imp_ids = []
    for impid in response_arr:
        query1 = 'SELECT IMP_DESCRIPTION from imperative_info where IMP_ID = "'+impid[0]+'";'
        imp_name = cursor.execute(query1).fetchone()[0]
        imp_ids.append(str(impid[0]))
        imp_ids_desc.append(str(impid[0])+"-"+imp_name)
    return imp_ids,imp_ids_desc

    
# main function
if __name__ == "__main__":
       print("Content-type: text/html \n");
       form = cgi.FieldStorage()
##       app_name = form.getvalue('app_name')
##       from_date = form.getvalue('from_date')
##       to_date = form.getvalue('to_date')
##       search = form.getvalue('search')
       time = datetime.now()
       print(time)
       time_main = re.sub(r'[:.]','-',str(time))
       date_time = str(time).split(" ")[0]
       app_name="TWA"
       from_date = "2019-03-11T11:40:00"
       to_date = "2019-03-14T11:42:00"
       search = "CITI"
    
       #Stad Log
       imp_ids,imp_ids_desc = getImperatives(app_name)
       for impid_des in imp_ids_desc:
            impid,impdesc = impid_des.split("-")
            if not search:
                if impid == "IMP001":
                    ua_index = "ua"
                    usage_process(date_time, ua_index, app_name, from_date, to_date)
                elif impid == "IMP002":
                    dc_index = "dcall"
                    drill_index = "dc"
                    dc_process(date_time, dc_index, app_name, from_date, to_date, drill_index)
                elif impid == "IMP003":
                    fa_index = "faall"
                    fa_process(date_time,fa_index, app_name, from_date, to_date)
                if impid == "IMP004":
                    hm_index = "hm"
                    hmprocess(date_time,hm_index, app_name, from_date, to_date, impdesc)
                elif impid == "IMP005":
                    nfv_index = "sua"
                    nfv_process(date_time,nfv_index, app_name, from_date, to_date,impdesc)
                elif impid == "IMP006":
                    ufa_index = "sua"
                    ufa_process(date_time,ufa_index, app_name, from_date, to_date, impdesc, fa_index)
            elif impid == "IMP008" and search:
                print("hi")
                sua_index = "sua"
                sdc_index = "sdc"
                header_arr,uniq_service = search_DCprocess(date_time,sdc_index, app_name, from_date, to_date,impdesc,search)
                if uniq_service:
                    search_UAprocess(date_time,sua_index, app_name, from_date, to_date,impdesc,search,uniq_service)
                    print(uniq_service)
       print(datetime.now())
       print("succesfully Inserted")
