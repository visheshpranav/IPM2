import re,os
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
def generateCSV_IMP006(matched_patterns1,userid,rep_id,Outcome1,report_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name):
    all_timestamps=[]
    unique_date=[]
    matched_patterns = matched_patterns1.split(",")
    Outcomes = Outcome1.split(",")
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    failure_arr,all_failure_arr,service_dict,time_file_arr = [],[],{},[]
    pattern_rex = {}
    
    if Logic == "Customization":
        for pattern in matched_patterns:
            query= 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
            regex = con.execute(query).fetchone()[0]
            pattern_rex[pattern]=regex
        failure_arr,all_failure_arr,service_dict,time_file_arr,all_timestamps,unique_date = Customize(pattern_rex,loglines)
##        print(all_timestamps)
        create_csv(failure_arr,all_failure_arr,service_dict,time_file_arr,all_timestamps,unique_date,report_name.lower().strip(),userid,rep_id,mode,appName,time_main,date_time,Imp_name,Outcomes)

def Customize(pattern_rex,loglines):
    response_arr = []
    serviceCall_arr  = []
    time_file_arr =[]
    failure_arr = []
    all_failure_arr = []
    service_dict = {}
    all_timestamps=[]
    unique_date=[]
    isReq = False
    isBody = False
    isError = False
    flag = 0
    servicecall,response,userID,fileTime,err_detail,err_decription,err_codes = "","","","","","",""
    for line in loglines:
        soapreq = re.match(r''+str(pattern_rex['P5'])+'',line)
        datetimemat = re.match(r''+str(pattern_rex['P7'])+'',line)
        user = re.match(r''+str(pattern_rex['P8'])+'',line)
        soapbody = re.match(r''+str(pattern_rex['P3'])+'',line)
        soapend = re.match(r''+str(pattern_rex['P6'])+'',line)
        serv = re.match(r''+str(pattern_rex['P4'])+'',line)
        res = re.match(r''+str(pattern_rex['P23'])+'',line)
        err = re.match(r''+str(pattern_rex['P10'])+'',line)
        err_det = re.match(r''+str(pattern_rex['P27'])+'',line)
        err_desc = re.match(r''+str(pattern_rex['P25'])+'',line)
        err_code = re.match(r''+str(pattern_rex['P26'])+'',line)
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
            flag = 1
            isError = True
        elif err_det and isReq:
            if not err_detail:
                err_detail = err_det.group(1)
            else:
                err_detail = err_detail+" / "+err_det.group(1)
        elif err_desc and isReq:
            if not err_decription:
                err_decription = err_desc.group(1)
            else:
                err_decription = err_decription+" / "+err_desc.group(1)
        elif err_code and isReq:
            if not err_codes:
                err_codes = err_code.group(1)
            else:
                if flag == 1:
                    err_codes = err_codes+" - "+err_code.group(1)
                    flag = 0
                else:
                    err_codes = err_codes+" / "+err_code.group(1)
        elif isReq and soapend:
            cur_timestamp = fileTime[:19]
            strp_currentdate = datetime.strptime(cur_timestamp,'%Y-%m-%dT%H:%M:%S')
            currentdate = strp_currentdate.strftime("%m/%d/%y %H:%M")
            currentdate_NF = strp_currentdate.strftime("%m/%d/%y %H:%M:%S")
            all_timestamps.append(str(currentdate))
            uniqueDate = (str(currentdate).split(" ")[0])
            if uniqueDate not in unique_date:
                unique_date.append(uniqueDate)
            time_file_arr.append(str(currentdate_NF)+","+str(servicecall)+","+str(response))
            if isError:
##                    print(str(currentdate_NF), str(servicecall), response, 1)
                if str(currentdate_NF).split(" ")[0].split("/")[1]+"_"+str(servicecall) in service_dict.keys():
                        service_dict[str(currentdate_NF).split(" ")[0].split("/")[1]+"_"+str(servicecall)].append(str(currentdate_NF)+","+userID+","+err_codes+","+err_decription +" - "+ err_detail)
                else:
                    service_dict[str(currentdate_NF).split(" ")[0].split("/")[1]+"_"+str(servicecall)] = []
                    service_dict[str(currentdate_NF).split(" ")[0].split("/")[1]+"_"+str(servicecall)].append(str(currentdate_NF)+","+userID+","+err_codes+","+err_decription +" - "+err_detail)
                response_arr.append(str(currentdate_NF).split(" ")[0]+"_"+str(servicecall)+","+response+","+str(1))
                serviceCall_arr.append(str(currentdate_NF).split(" ")[0]+"_"+str(servicecall))
                isError = False
            else:
##                    print(str(currentdate_NF), str(servicecall), response, 0)
                response_arr.append(str(currentdate_NF).split(" ")[0]+"_"+str(servicecall)+","+response+","+str(0))
                serviceCall_arr.append(str(currentdate_NF).split(" ")[0]+"_"+str(servicecall))
            isError = False
            isReq = False
            flag = 0
            servicecall,response,userID,fileTime,err_detail,err_decription,err_codes = "","","","","","",""
    response_fin = []
    uniq_serviceCall = set(serviceCall_arr)
##    print(uniq_serviceCall)
    for service_req in uniq_serviceCall:
        match_response = [int(s.split(",")[1]) for s in response_arr if service_req == s.split(",")[0]]
        match_pass = [s.split(",")[2] for s in response_arr if service_req == s.split(",")[0]]
##        print(match_response)
        min_res = min(match_response)
        max_res = max(match_response)
        cou_res = sum(match_response)
        avg_res = cou_res/len(match_response)
        match_pass = Counter(match_pass)
        pass_fail = str(match_pass['1'])+"/"+str(len(match_response))
        Status = ""
        if(str(match_pass['1']) == "0"):
            Status = "low"
        elif(round(int(match_pass['1'])/len(match_response)*100, 2) > 26):
            Status = "high"
        else:
            Status = "medium"
        #print(Status)
        response_fin.append(service_req+","+str(len(match_response))+","+str(match_pass['0'])+","+str(match_pass['1'])+","+str(min_res)+","+str(max_res)+","+str(round(avg_res,2)))
        failure_arr.append(service_req+","+str(len(match_response))+","+str(match_pass['0'])+","+str(match_pass['1'])+","+str(min_res)+","+str(max_res)+","+str(round(avg_res,2))+"\n")
##        print(service_req.split("_")[0]+","+service_req.split("_")[1]+","+str(len(match_response))+","+Status+","+str(int(match_pass['1']))+"\n")
        all_failure_arr.append(service_req.split("_")[0]+","+service_req.split("_")[1]+","+str(len(match_response))+","+Status+","+str(int(match_pass['1']))+"\n")
    return failure_arr,all_failure_arr,service_dict,time_file_arr,all_timestamps,unique_date
    

def create_csv(failure_arr,all_failure_arr,service_dict,time_file_arr,all_timestamps,unique_date,report_name,userid,rep_id,mode,appName,time_main,date_time,Imp_name,Outcomes):   
    if mode == "OFL":
        ofl_repname = str(userid)+"_"+str(rep_id)
        ofl_filename = appName+"_"+report_name+"_"+Imp_name
        filename = ofl_filename+"_All.csv"
        all_filename = ofl_filename+"_AllFailures.csv"
        time = ofl_filename+"_timedetails.csv"
        text_filename = ofl_filename+"_fail_response.txt"
        for service in service_dict.keys():
            failure_item_file = open(ofl_filename+"_"+service+".csv","w")
            failure_item_file.write("Datetime,Userid,ErrorCode,ErrorDescription\n")
            for i in service_dict[service]:
                failure_item_file.write(i+"\n")
            failure_item_file.close()
    elif mode == "ONL":
        onl_repname = appName+"_"+Imp_name
        onl_filename = ONL_Report+appName+"_"+Imp_name
        filename = onl_repname+"_ONL_All"+"_"+str(date_time)+".csv"
        all_filename = onl_repname+"_ONL_AllFailures""_"+str(date_time)+".csv"
        time = onl_repname+"_ONL_timedetails_"+str(date_time)+".csv"
        text_filename = onl_repname+"_ONL_fail_response_"+str(date_time)+".txt"
        for service in service_dict.keys():
            failure_item_file = open(onl_repname+"_ONL_"+service+"_"+str(date_time)+".csv","w")
            failure_item_file.write("Datetime,Userid,ErrorCode,ErrorDescription\n")
            for i in service_dict[service]:
                failure_item_file.write(i+"\n")
            failure_item_file.close()
                
        
    failure_file = open(filename,"w")
    failure_file.write("Service Call,Total Count,Pass Count,Fail Count,Min. Response time(ms),Max. Response time(ms),Avg. Response time(ms)\n")
    for i in failure_arr:
        failure_file.write(i)
    failure_file.close()
    
    all_failure_file = open(all_filename,"w")
    all_failure_file.write("Day,ServiceCall,Count,Status,FailureCount\n")
    for i in all_failure_arr:
        all_failure_file.write(i)
    all_failure_file.close()
    
    time_file = open(time,"w")
    time_file.write("Datetime,ServiceCall,Responsetime(ms)\n")
    for i in time_file_arr:
        time_file.write(i+"\n")
    time_file.close()
    
    EndDate = max(all_timestamps)   
    StartDate = min(all_timestamps)
    text_file = open(text_filename, "w")
    text_file.write("StartDate - " + str(StartDate)+"\n")
    text_file.write("EndDate - " + str(EndDate)+"\n")
    text_file.write("Unique date - \n")
    for date in unique_date:
        date = datetime.strptime(date,'%m/%d/%y')
        text_file.write(str(datetime.strftime(date, '%#m/%#d/%y')).split(" ")[0] + "\n")
        print(str(datetime.strftime(date, '%#m/%#d/%y')).split(" ")[0]) 
    text_file.close()
    
    sourcefiles = [f for f in os.listdir('.') if os.path.isfile(f)]
    sourcepath = os.path.dirname(os.path.realpath(__file__))
    if mode == "OFL":
        ofl_repname = str(userid)+"_"+str(rep_id)
        destinationpath = "../../../WEB-INF/classes/static/html/Reports/"+ofl_repname+"/"
        if not os.path.exists(destinationpath):
            os.mkdir(destinationpath)
        for files in sourcefiles:
            if files.endswith('.csv'):
                shutil.move(files, os.path.join(destinationpath,files))
            if files.endswith('.txt'):
                shutil.move(files, os.path.join(destinationpath,files))
    elif mode == "ONL":
        destinationpath = "../../../WEB-INF/classes/static/html/Online/"
        if not os.path.exists(destinationpath):
            os.mkdir(destinationpath)
        for files in sourcefiles:
            if files.endswith('.csv'):
                files1 = re.sub(date_time,time_main,files)
                shutil.move(files, os.path.join(destinationpath,files))                
                shutil.copy(os.path.join(destinationpath,files), os.path.join(ONL_Report,files1))
            if files.endswith('.txt'):
                files1 = re.sub(date_time,time_main,files)
                shutil.move(files, os.path.join(destinationpath,files))                
                shutil.copy(os.path.join(destinationpath,files), os.path.join(ONL_Report,files1))

#Function to qualify the log
def parse_log(logpath_file):
    if logpath_file.endswith(".xlsx"):
        sheet_num = 0
        wb=xlrd.open_workbook(logpath_file)
        sheet=wb.sheet_by_index(sheet_num)
        loglines = iter_rows(sheet)
    else:
        fp = open(logpath_file,encoding='utf8', errors='ignore')
        head = fp.readlines()
        fp.close()
        loglines = head
    return loglines 

#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    #matched_patterns = form.getvalue("matched_patterns")
    time = datetime.now()
    time_main = re.sub(r'[:.]','C',str(time))
    date_time = str(time).split(" ")[0]
    matched_patterns = "P3,P4,P5,P6,P7,P8,P9,P10,P23,P27,P25,P26"
    userid = "9"
    rep_id = "750"
    rep_name = "a14"
    Outcome = "csv"
    Logic = "Customization"
    logpath_file = "C:\\LAPAM2019\\DataLake\\Logs\\Cache\\9\\a14\\WebSphere\\SystemOut.log"
    mode = "OFL"
    appName = "TWA"
    Imp_name = "usage vs failure analysis"
    loglines = parse_log(logpath_file)
    generateCSV_IMP006(matched_patterns,userid,rep_id,Outcome,rep_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name)
