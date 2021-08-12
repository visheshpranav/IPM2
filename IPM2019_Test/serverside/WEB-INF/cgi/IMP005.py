import re,os,xmltodict,json
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc,shutil
import configparser
from collections import Counter
from datetime import datetime
from statistics import stdev

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
ONL_Report = parser.get('Report','onlpathES')
service_arr = []
nfvdd_arr = []
std_usage = []
final_usage = []
ONL_ALL = []
#Generate Usage Outcome
def generateCSV_IMP005(matched_patterns1,userid,rep_id,Outcome1,report_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name,log_type):
    matched_patterns = matched_patterns1.split(",")
    if ("P23" in matched_patterns) and (not "P10" in matched_patterns):
        matched_patterns.append("P10")
    Outcome = Outcome1.split(",")[0]
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    pattern_rex = {}
    flag = 0
    isReq = False
    isBody = False
    isError = False
    servicecall,response,userID,fileTime = "","","",""
    for pattern in matched_patterns:
        query= 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
        regex = con.execute(query).fetchone()[0]
        pattern_rex[pattern]=regex
    if Logic == "Customization" and (log_type == "Standard" or mode == "OFL"):
        responsetime_arr = []
        for line in loglines:
            soapreq = re.match(r''+str(pattern_rex['P5'])+'',line)
            datetimemat = re.match(r''+str(pattern_rex['P7'])+'',line)
            user = re.match(r''+str(pattern_rex['P8'])+'',line)
            soapbody = re.match(r''+str(pattern_rex['P3'])+'',line)
            soapend = re.match(r''+str(pattern_rex['P6'])+'',line)
            serv = re.match(r''+str(pattern_rex['P4'])+'',line)
            res = re.match(r''+str(pattern_rex['P23'])+'',line)
            err = re.match(r''+str(pattern_rex['P10'])+'',line)
            if soapreq:
                isReq = True
                isError = False
                isBody = False
            elif isReq and datetimemat:
                fileTime = datetimemat['value'].strip()
            elif isReq and user:
                userID = user['value'].strip()
            elif isReq and soapbody:
                isBody = True
            elif serv and isBody:
                servicecall = serv['usage'].strip()
                isBody = False
            elif res and isReq:
                response = res.group(2)
            elif err and isReq:
                isError = True
            elif isReq and soapend:
                service_arr.append(servicecall)
                cur_timestamp = fileTime[:19]
                strp_currentdate = datetime.strptime(cur_timestamp,'%Y-%m-%dT%H:%M:%S')
                currentdate = strp_currentdate.strftime("%m/%d/%y %H:%M")
                currentdate_NF = strp_currentdate.strftime("%m/%d/%y %H:%M:%S")
                currentdate_NF = str(currentdate_NF)+".000"
                if isError:
                    responsetime_arr.append(servicecall+","+str(response)+","+str(1))
                    nfvdd_arr.append(servicecall+","+userID+","+str(currentdate_NF)+","+"Fail"+","+str(response))
                    ONL_ALL.append(servicecall+","+userID+","+str(currentdate_NF)+","+"Fail"+","+str(response))
                else:
                    responsetime_arr.append(servicecall+","+str(response)+","+str(0))
                    nfvdd_arr.append(servicecall+","+userID+","+str(currentdate_NF)+","+"Pass"+","+str(response))
                    ONL_ALL.append(servicecall+","+userID+","+str(currentdate_NF)+","+"Pass"+","+str(response))
                isError = False
                isReq = False
                servicecall,response,userID,fileTime = "","","",""
##        print(responsetime_arr)
    elif Logic == "Customization" and log_type == "Custom":
        responsetime_arr = []
        datetimeFormat = '%Y-%m-%d %H:%M:%S,%f'
        parent = ""
        parent_time = ""
        start_method = []
        end_method = []
        main_meth = []
        parentReq = ""
        match_f = False
        for line in loglines:
            match_parent = re.match(r''+str(pattern_rex['P32'])+'',line)
            parent_end = re.match(r''+str(pattern_rex['P33'])+'',line)
            child_match = re.match(r''+str(pattern_rex['P34'])+'',line)
            child_end = re.match(r''+str(pattern_rex['P35'])+'',line)
            if match_parent:
                strp_currentdate = datetime.strptime(match_parent.group(1), '%Y-%m-%d %H:%M:%S,%f')
                currentdate = datetime.strftime(strp_currentdate,"%m/%d/%y %H:%M:%S")
                parent = match_parent.group(2)
                parentReq = match_parent.group(2)+"Request"
                parent_time = currentdate
            if parent_end:
                strp_currentdate = datetime.strptime(parent_end.group(1), '%Y-%m-%d %H:%M:%S,%f')
                currentdate = strp_currentdate.strftime("%m/%d/%y %H:%M:%S")
                diff = datetime.strptime(parent_end.group(1), datetimeFormat)\
                                - datetime.strptime(parent_time, datetimeFormat)
                milli = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
                responsetime_arr.append(parentReq+","+str(int(milli))+","+str(0))
                parent_time = re.sub(r',','.',parent_time)
                nfvdd_arr.append(parentReq+","+parent_time+","+str(int(milli)))
                ONL_ALL.append(parentReq+","+"-"+","+str(parent_time)+","+"-"+","+str(int(milli)))
                service_arr.append(parentReq)
            if child_match:
                strp_currentdate = datetime.strptime(child_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
                currentdate = strp_currentdate.strftime("%m/%d/%y %H:%M:%S")
                child_start = child_match.group(1)+"$&$"+child_match.group(2)
                start_method1 = start_method
                j = 0
                for i in start_method1:
                    i_arr = i.split("$&$")
                    if child_match.group(2) == i_arr[1]:
                        start_method.pop(j)
                    j = j+1
                start_method.append(child_start)
            if child_end:
                strp_currentdate = datetime.strptime(child_end.group(1), '%Y-%m-%d %H:%M:%S,%f')
                currentdate = strp_currentdate.strftime("%m/%d/%y %H:%M:%S")
                j = 0
                flag = 0
                start_method1 = start_method
                for i in start_method1:
                    i_arr = i.split("$&$")
                    if child_end.group(2) == i_arr[1]:
                        diff = datetime.strptime(child_end.group(1), datetimeFormat)\
                                - datetime.strptime(i_arr[0], datetimeFormat)
                        milli = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
                        responsetime_arr.append(i_arr[1]+","+str(int(milli))+","+str(0))
                        main_t,millisec = child_end.group(1).split(",")
                        strp_currentdate = datetime.strptime(i_arr[0], '%Y-%m-%d %H:%M:%S,%f')
                        currentdate = strp_currentdate.strftime("%m/%d/%y %H:%M:%S")
                        currentdate = re.sub(r',','.',currentdate)
                        currentdate = currentdate + "."+millisec
                        nfvdd_arr.append(i_arr[1]+","+currentdate+","+str(int(milli)))
                        ONL_ALL.append(i_arr[1]+","+"-"+","+currentdate+","+"-"+","+str(int(milli)))
                        service_arr.append(i_arr[1])
                        start_method.pop(j)
                    j = j+1
    writecsv(service_arr,responsetime_arr,nfvdd_arr,userid,rep_id,Outcome,report_name,mode,appName,time_main,date_time,Imp_name,log_type,ONL_ALL)         
            
                    
def writecsv(service_arr,responsetime_arr,nfvdd_arr,userid,rep_id,Outcome,report_name,mode,appName,time_main,date_time,Imp_name,log_type,ONL_ALL):
    
    uniq_serviceCall = set(service_arr)
    #print(uniq_serviceCall)
##    print(responsetime_arr)
    for service_req in uniq_serviceCall:
        print(service_req)
        rep_name = str(userid)+"_"+str(rep_id)
        service_req1 = re.sub(r'[<>{}]','',service_req)
        match_response = [int(s.split(",")[1]) for s in responsetime_arr if service_req == s.split(",")[0]]
        match_pass = [s.split(",")[2] for s in responsetime_arr if service_req == s.split(",")[0]]
        match_nfvdd = [s for s in nfvdd_arr if service_req == s.split(",")[0]]
        match_avg = [int(s.split(",")[1]) for s in responsetime_arr if (service_req == s.split(",")[0]) and (s.split(",")[2] == "0")]
        #print(service_req)
        match_pass = Counter(match_pass)
##        print(match_response)
        if len(match_response) > 0:
            if mode == "OFL":
                filename_service = appName+"_"+report_name.lower()+"_"+Imp_name+"_"+service_req1+"."+Outcome
                movepath = "Reports/"+rep_name
                usagefile_service = open(filename_service,"w")
            elif mode == "ONL":
                onl_filename_service = appName+"_"+Imp_name+"_ONL_"+service_req1+"_"+str(date_time)+"."+Outcome
                #newfilename_service = ONL_Report+appName+"_"+Imp_name+"_ONL_"+service_req1+"_"+str(time_main)+"."+Outcome
                movepath = "Online"
                usagefile_service = open(onl_filename_service,"w")
            if service_req.endswith("Rq") or not log_type == "Custom" :
                usagefile_service.write("Service Call,User Id,Timestamp,Status,Response time(ms)\n")
            else:
                usagefile_service.write("Service Call,Timestamp,Response time(ms)\n")
            cou_res = sum(match_response)       
            avg_res = cou_res/len(match_response)
            if match_avg:
                min_res = min(match_avg)
                max_res = max(match_avg)
                cou_pass_avg = sum(match_avg)
                avg_pass = cou_pass_avg/len(match_avg)
            else:
                avg_pass = 0
                min_res = 0
                max_res = 0
            if len(match_avg) > 1:
                std_dev = stdev(match_avg)
                std_dev_str = str(round(std_dev,2))
            else:
                std_dev_str = str(0)
            if service_req.endswith("Rq") or not log_type == "Custom":
                #usagefile.write(service_req1+","+str(len(match_response))+","+str("-")+","+str("-")+","+str(min_res)+","+str(max_res)+","+str(round(avg_pass,2))+"\n")
                pass_fail = str(match_pass['1'])+"/"+str(len(match_response))
                Status = ""
                if(str(match_pass['1']) == "0"):
                    Status = "low"
                elif(round(int(match_pass['1'])/len(match_response)*100, 2) > 28):
                    Status = "high"
                else:
                    Status = "medium"
                std_usage.append(service_req1+","+str(len(match_response))+","+str(match_pass['0'])+","+str(match_pass['1'])+","+str(min_res)+","+str(max_res)+","+str(round(avg_pass,2))+","+std_dev_str)
                final_usage.append(service_req1+","+str(len(match_response))+","+str(match_pass['0'])+","+str(match_pass['1'])+","+str(min_res)+","+str(max_res)+","+str(round(avg_pass,2))+","+std_dev_str)
            else:
                final_usage.append(service_req1+","+str(len(match_response))+","+str("-")+","+str("-")+","+str(min_res)+","+str(max_res)+","+str(round(avg_pass,2))+","+std_dev_str)
                
            for i in match_nfvdd:
                usagefile_service.write(i+"\n")
            usagefile_service.close()
            
            if mode == "ONL":
                shutil.move(onl_filename_service, "../../../html/"+movepath+"/"+onl_filename_service)
                #shutil.copy("../../../html/"+movepath+"/"+onl_filename_service,newfilename_service)
            else:
                shutil.move(filename_service, "../../../WEB-INF/classes/static/html/"+movepath+"/"+filename_service)
    if mode == "OFL":
        sortedfin_arr = sorted(final_usage, key = lambda x: float(x.split(",")[6]),reverse=True)
        rep_name = str(userid)+"_"+str(rep_id)
        filename = appName+"_"+report_name.lower()+"_"+Imp_name+"."+Outcome
        movepath = "Reports/"+rep_name
        if not os.path.exists("../../../WEB-INF/classes/static/html/Reports/"+rep_name):
            os.mkdir("../../../WEB-INF/classes/static/html/Reports/"+rep_name)
        usagefile = open(filename,"w")
        usagefile.write("Service Call,Total Count,Pass Count,Fail Count,Min. Response time(ms),Max. Response time(ms),Avg. Response time(ms),Standard Deviation(ms)\n")
        for i in sortedfin_arr:
            usagefile.write(i+"\n")
        usagefile.close()
        shutil.move(filename, "../../../WEB-INF/classes/static/html/"+movepath+"/"+filename)
    elif mode == "ONL":
        sortedfin_arr = sorted(final_usage, key = lambda x: float(x.split(",")[6]),reverse=True)
        onl_filename = appName+"_"+Imp_name+"_ONL_"+str(date_time)+"."+Outcome
        onl_fullfile = appName+"_"+Imp_name+"_ONL_All_"+str(date_time)+"."+Outcome
        newfilename = ONL_Report+appName+"_"+Imp_name+"_ONL_All_"+str(time_main)+"."+Outcome
        movepath = "Online"
        usagefile = open(newfilename,"w")
        usagefile.write("Service Call,User ID,Timestamp,Status,Response time(ms)\n")
        for i in ONL_ALL:
            usagefile.write(i+"\n")
        usagefile.close()
        usagefile = open(onl_filename,"w")
        usagefile.write("Service Call,Total Count,Pass Count,Fail Count,Min. Response time(ms),Max. Response time(ms),Avg. Response time(ms),Standard Deviation(ms)\n")
        usage = []
        usage.extend(std_usage)
        usage.extend(sortedfin_arr[:20])
        for i in usage:
            usagefile.write(i+"\n")
        usagefile.close()
        shutil.move(onl_filename, "../../../html/"+movepath+"/"+onl_filename)
        usagefile = open(onl_fullfile,"w")
        usagefile.write("Service Call,Total Count,Pass Count,Fail Count,Min. Response time(ms),Max. Response time(ms),Avg. Response time(ms),Standard Deviation(ms)\n")
        usage = []
        usage.extend(std_usage)
        usage.extend(sortedfin_arr)
        for i in usage:
            usagefile.write(i+"\n")
        usagefile.close()
        shutil.move(onl_fullfile, "../../../html/"+movepath+"/"+onl_fullfile)
        



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
    matched_patterns = "P5,P7,P8,P3,P4,P23,P6"
    userid = "9"
    rep_id = "736"
    rep_name = "a1"
    Outcome = "csv"
    Logic = "Customization"
    logpath_file = "C:\\LAPAM2019\\DataLake\\Logs\\Cache\\9\\a1\\WebSphere\\SystemOut.log"
    mode = "OFL"
    appName = "TWA"
    Imp_name = "Non Functional View"
    log_type = "Standard"
    loglines = parse_log(logpath_file)
    generateCSV_IMP005(matched_patterns,userid,rep_id,Outcome,rep_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name,log_type)
    
