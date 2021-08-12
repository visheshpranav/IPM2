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
DSN_NAME = parser.get('DSN','DSN_NAME')
ONL_Report = parser.get('Report','onlpathES')
allfail_arr = []
fail_arr = []

#Generate Usage Outcome
def generateCSV_IMP003(matched_patterns1,userid,rep_id,Outcome1,report_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name,logtype):                    
    matched_patterns = matched_patterns1.split(",")
    Outcomes = Outcome1.split(",")
    con = pyodbc.connect("DSN="+DSN_NAME)
    cur = con.cursor()
    
    pattern_rex = {}
    if Logic == "None":
        noneLogic(matched_patterns,loglines,Outcomes,userid,rep_id,report_name,mode,appName,time_main,date_time,Imp_name)
    elif Logic == "Customization":
        for pattern in matched_patterns:
            query= 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
            regex = con.execute(query).fetchone()[0]
            pattern_rex[pattern]=regex
        if logtype == "Standard":
            Customize_standard(pattern_rex,loglines,report_name.lower().strip(),userid,rep_id,mode,appName,time_main,date_time,Imp_name,Outcomes)
        elif logtype == "Custom":
            Customize_custom(pattern_rex,loglines,report_name.lower().strip(),userid,rep_id,mode,appName,time_main,date_time,Imp_name,Outcomes)
    
def noneLogic(matched_patterns,loglines,Outcomes,userid,rep_id,report_name,mode,appName,time_main,date_time,Imp_name):
    usage = []
    l = []
    l_page = []
    l_page1 = []
    con = pyodbc.connect("DSN="+DSN_NAME)
    cur = con.cursor()
    for pattern in matched_patterns:
        query = 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
        regex = con.execute(query).fetchone()[0]
        pattern = r''+str(regex)+''
        for line in loglines:
            match = re.match(pattern,line)
            if match:
                temp = match['usage']
                status = match['failure'].strip()
                m = re.match(r'\/(.*?)\/.*',temp)
                if not status == "200":
                    if m:
                        val = status + temp
                        l_page1.append(val)
    l_page = set(l_page1)
    st_val="httpStatus"
    l.append(st_val)
    for item in l_page:
        st_val="httpStatus"
        #pass_count = l_fin.count(item)
        fail_count = l_page1.count(item)
        #print(fail_count)
        if fail_count != 0:
            #print(item)
            item_arr = item.split("/")
            st_val_i=1
            for item_val in item_arr:
                if(len(item_arr) == st_val_i):
                    st_val = st_val + "/"+ item_val + "," + str(fail_count)
                else:
                    st_val = st_val + "/"+ item_val
                st_val_i = st_val_i+1
                if st_val not in l:
                    l.append(st_val)

    create_outcome(l,Outcomes,userid,rep_id,report_name,mode,appName,time_main,date_time,Imp_name)
    
def create_outcome(l,Outcomes,userid,rep_id,report_name,mode,appName,time_main,date_time,Imp_name):
    l.sort()
    l = set(l)
    for Outcome in Outcomes:
        if Outcome == "csv":
            if mode == "OFL":
                if not os.path.exists("../../../html/Reports/"+str(userid)+"_"+str(rep_id)):
                    os.mkdir("../../../html/Reports/"+str(userid)+"_"+str(rep_id))
                filename = appName+"_"+report_name.lower()+"_"+Imp_name+"."+Outcome
                move_path = "Reports/"+str(userid)+"_"+str(rep_id)
                failurefile = open(filename,"w")
            #print(l)
            elif mode == "ONL":
                if not os.path.exists("../../../html/Online"):
                    os.mkdir("../../../html/Online")
                filename = appName+"_"+Imp_name+"_ONL_"+str(date_time)+"."+Outcome
                newfile = ONL_Report+appName+"_"+Imp_name+"_ONL_"+str(time_main)+"."+Outcome
                move_path = "Online"
                failurefile = open(filename,"w")
            failurefile.write("id,value\n")
            for i in l:
                failurefile.write(i+"\n")
            failurefile.close()
            shutil.move(filename, "../../../html/"+move_path+"/"+filename)
            if mode == "ONL":
                shutil.copy("../../../html/Online/"+filename,newfile)

def Customize_standard(pattern_rex,loglines,report_name,userid,rep_id,mode,appName,time_main,date_time,Imp_name,Outcomes):
    
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
                err_detail = err_detail+" & "+err_det.group(1)
        elif err_desc and isReq:
            if not err_decription:
                err_decription = err_desc.group(1)
            else:
                err_decription = err_decription+" & "+err_desc.group(1)
        elif err_code and isReq:
            if flag == 1:
                err_codes = err_code.group(1)
                flag = 0
        elif isReq and soapend:
            cur_timestamp = fileTime[:19]
            strp_currentdate = datetime.strptime(cur_timestamp,'%Y-%m-%dT%H:%M:%S')
            currentdate = strp_currentdate.strftime("%m/%d/%y %H:%M")
            currentdate_NF = strp_currentdate.strftime("%m/%d/%y %H:%M:%S")
            if isError:
                if mode == "ONL":
                    fail_arr.append(appName+ "/" +str(err_codes)+ "/" +str(servicecall))
                else:
                    fail_arr.append(report_name+ "/" +str(err_codes)+ "/" +str(servicecall))
                allfail_arr.append(str(currentdate_NF)+","+userID+","+str(servicecall)+","+str(err_codes)+","+str(err_decription)+" - "+str(err_detail))
            isError = False
            isReq = False
            flag = 0
            servicecall,response,userID,fileTime,err_detail,err_decription,err_code = "","","","","","",""
    if mode == "OFL":
        if not os.path.exists("../../../html/Reports/"+str(userid)+"_"+str(rep_id)):
            os.mkdir("../../../html/Reports/"+str(userid)+"_"+str(rep_id))
        filename = appName+"_"+report_name.lower()+"_"+Imp_name+"_All"+".csv"
        move_path = "Reports/"+str(userid)+"_"+str(rep_id)
        failurefile = open(filename,"w")
    #print(l)
    elif mode == "ONL":
        if not os.path.exists("../../../html/Online"):
            os.mkdir("../../../html/Online")
        filename = appName+"_"+Imp_name.lower()+"_All_ONL_"+str(date_time)+".csv"
        newfile = ONL_Report+appName+"_"+Imp_name+"_All"+"_ONL_"+str(time_main)+".csv"
        print(date_time)
        move_path = "Online"
        failurefile = open(filename,"w")
    failurefile.write("Timestamp,UserId,ServiceCall,ErrorCode,ErrorDescription\n")
    for i in allfail_arr:
        failurefile.write(i+"\n")
    failurefile.close()
    shutil.move(filename, "../../../html/"+move_path+"/"+filename)
    if mode == "ONL":
        shutil.copy("../../../html/Online/"+filename,newfile)

    Err_failure = []
    if mode == "ONL":
        Err_failure.append(appName+",")
    else:
        Err_failure.append(report_name+",")
    dist_fail_serviceCall = set(fail_arr)
    fail_list=[]
    for item in dist_fail_serviceCall:
        fail_count = fail_arr.count(item)
        hdr_item="/".join(item.split("/")[:-1])
        if hdr_item not in fail_list:
            Err_failure.append(hdr_item+",")
        fail_list.append(hdr_item)
        Err_failure.append(item+","+str(fail_count))
    create_outcome(Err_failure,Outcomes,userid,rep_id,report_name,mode,appName,time_main,date_time,Imp_name)


def Customize_custom(pattern_rex,loglines,report_name,userid,rep_id,mode,appName,time_main,date_time,Imp_name,Outcomes):
    codes = []
    details = []
    code,detail = "",""
    isStart = False
    timestamp = ""
    for line in loglines:
        start_mat = re.match(r''+str(pattern_rex['P36'])+'',line)
        code_mat = re.match(r''+str(pattern_rex['P37'])+'',line.strip())
        detail_mat = re.match(r''+str(pattern_rex['P38'])+'',line.strip())
        end_mat = re.match(r''+str(pattern_rex['P31'])+'',line.strip())
        if start_mat:
            isStart = True
            codes = []
            details = []
            code,detail = "",""
            fileTime = start_mat.group(1)
            cur_timestamp = fileTime[:19]
            strp_currentdate = datetime.strptime(cur_timestamp,'%Y-%m-%d %H:%M:%S')
            currentdate = strp_currentdate.strftime("%m/%d/%y %H:%M")
            currentdate_NF = strp_currentdate.strftime("%m/%d/%y %H:%M:%S")
        elif code_mat and isStart:
            codes.append(code_mat.group(1))
        elif detail_mat and isStart:
            details.append(detail_mat.group(1))
        elif end_mat and isStart and codes:
            isStart = False
            code = "/".join(codes)
            detail = "/".join(details)
            allfail_arr.append(str(currentdate_NF)+",-,-,"+str(code)+","+str(detail))
            fail_arr.append(appName+ "/" +str(codes[-1]))
            codes = []
            details = []
            code,detail = "",""
            
    if not os.path.exists("../../../html/Online"):
        os.mkdir("../../../html/Online")
    filename = appName+"_"+Imp_name.lower()+"_All_ONL_"+str(date_time)+".csv"
    newfile = ONL_Report+appName+"_"+Imp_name+"_All"+"_ONL_"+str(time_main)+".csv"
    print(date_time)
    move_path = "Online"
    failurefile = open(filename,"w")
    failurefile.write("Timestamp,UserId,ServiceCall,ErrorCode,ErrorDescription\n")
    for i in allfail_arr:
        failurefile.write(i+"\n")
    failurefile.close()
    shutil.move(filename, "../../../html/"+move_path+"/"+filename)
    if mode == "ONL":
        shutil.copy("../../../html/Online/"+filename,newfile)

    Err_failure = []
    Err_failure.append(appName+",")
    dist_fail_serviceCall = set(fail_arr)
    fail_list=[]
    for item in dist_fail_serviceCall:
        fail_count = fail_arr.count(item)
        hdr_item="/".join(item.split("/")[:-1])
        if hdr_item not in fail_list:
            Err_failure.append(hdr_item+",")
        fail_list.append(hdr_item)
        Err_failure.append(item+","+str(fail_count))
    create_outcome(Err_failure,Outcomes,userid,rep_id,report_name,mode,appName,time_main,date_time,Imp_name)
            
    
    
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
    time_main = re.sub(r'[:\.]','C',str(time))
    date_time = str(time).split(" ")[0]
    matched_patterns = "P36,P37,P38,P31"
    userid = ""
    rep_id = ""
    rep_name = ""
    Outcome = "csv"
    Logic = "Customization"
    logpath_file = "C:\\LAPAM2019\\DataLake\\Online\\Custom\\CitiPlanner_RA_SG.log.6"
    mode = "ONL"
    appName = "TWA"
    Imp_name = "Failure Analysis"
    logtype = "Custom"
    loglines = parse_log(logpath_file)
    generateCSV_IMP003(matched_patterns,userid,rep_id,Outcome,rep_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name,logtype)
    
