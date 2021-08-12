import re,os
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
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
ONL_Report = parser.get('Report','onlpathES')
ONL_USAGE = []
ONL_REPO_DATA = []

#Generate Usage Outcome
def generateCSV_IMP001(matched_patterns1,userid,rep_id,Outcome1,rep_name,loglines,Logic,mode,appName,time,date_time,Imp_name):
    matched_patterns = matched_patterns1.split(",")
    Outcomes = Outcome1.split(",")
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    usage = []
    file_timeformat = "%Y-%m-%dT%H:%M:%S"
    convert_timeformat = "%Y-%m-%d %H:%M:%S"
    timevalue = ""
    if len(matched_patterns) == 1:
        pattern = matched_patterns[0]
        query = 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
        regex = con.execute(query).fetchone()[0]
        pattern = r''+str(regex)+''
        for line in loglines:
            match = re.match(pattern,line)
            if match:
                usage.append(match['usage'])
    else:
        if Logic == "THEN":
            regexs= []
            timestamp = ""
            for pattern in matched_patterns:
                query = 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
                regex = con.execute(query).fetchone()[0]
                regexs.append(regex)
            reg_count = len(regexs)
            pat_cou = 0
            for line in loglines:
                regex = regexs[pat_cou]
                pattern = r''+str(regex)+''
                match = re.match(pattern,line)
                if pat_cou == (reg_count-1):
                    if match:
                        if (mode == "ONL") and (appName == "TWA"):
                            ONL_REPO_DATA.append(timevalue+","+match['usage'])
                        usage.append(match['usage'])
                        ONL_USAGE.append(match['usage'])
                        pat_cou = 0
                    else:
                        pat_cou = 0
                elif match:
                    if (mode == "ONL") and (pat_cou == 0) and (appName == "TWA"):
                        timevalue = match['value']
                        d = datetime.strptime(timevalue[:19], file_timeformat)
                        timevalue = datetime.strftime(d, convert_timeformat)
                    pat_cou = pat_cou+1
        elif Logic == "AND":
            regexs= {}
            for pattern in matched_patterns:
                query = 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
                regex = con.execute(query).fetchone()[0]
                regexs[pattern] = regex
            reg_count = len(regexs.keys())
            for line in loglines:
                pat_cou = 0
                timestamp = ""
                str_val = ""
                for patt in regexs.keys():
                    regex = regexs[patt]
                    pattern = r''+str(regex)+''
                    match = re.match(pattern,line)
                    if match:
                        pat_cou = pat_cou+1
                        if pat_cou == 1:
                            str_val = match.group(1)
                        else:
                            str_val1 = match.group(1) 
                            if (str_val1.endswith("Rs") or str_val1.endswith("Response")):
                                str_val1 = re.sub(r'Rs|Response','',str_val1)
                            usage.append(str_val1)
                            ONL_USAGE.append(str_val1)
                            str_val = str_val+","+str_val1
                if pat_cou == reg_count:
                    ONL_REPO_DATA.append(str_val)
            
            
    for Outcome in Outcomes:
        if Outcome == "csv":
            if mode == "OFL":
                if not os.path.exists("../../../WEB-INF/classes/static/html/Reports/"+str(userid)+"_"+str(rep_id)):
                    os.mkdir("../../../WEB-INF/classes/static/html/Reports/"+str(userid)+"_"+str(rep_id))
                #print(l)
                usage = Counter(usage)
                filename = appName+"_"+rep_name.lower()+"_"+Imp_name+"."+Outcome
                usagefile = open(filename,"w")
                usagefile.write("id,value\n")
                for i in usage:
                    usagefile.write(i+","+str(usage[i])+"\n")
                usagefile.close()
                shutil.move(filename, "../../../WEB-INF/classes/static/html/Reports/"+str(userid)+"_"+str(rep_id)+"/"+filename)
            if mode == "ONL":
                if not os.path.exists("../../../html/Online/"):
                    os.mkdir("../../../html/Online")
                #print(l)
                usage = ONL_USAGE
                usage = Counter(usage)
                filename =appName+"_"+Imp_name+"_ONL_"+str(date_time)+"."+Outcome
                file = appName+"_"+Imp_name+"_ONL_"+str(time)+"."+Outcome
                usagefile = open(filename,"w")
                usagefile.write("id,value\n")
                for i in usage:
                    usagefile.write(i+","+str(usage[i])+"\n")
                usagefile.close()
                if appName == "TWA":
                    usagefile = open(file,"w")
                    usagefile.write("Timestamp,ServiceCall\n")
                    for i in ONL_REPO_DATA:
                        usagefile.write(i+"\n")
                    usagefile.close()
                shutil.move(filename, "../../../html/Online/"+filename)
                shutil.move(file,ONL_Report+file)
    #observations
    txt_data = "Top 3 service calls as per usage:"
    observe_data = usage.most_common(3)
    data_cou = [f[1] for f in usage.most_common()]
    data_len = sum(data_cou)
    i = 1
    for service in observe_data:
        service_req = service[0]
        avg = service[1]/data_len
        percent = avg * 100
        txt_data = txt_data+"\n   "+str(i)+". "+service_req+" - "+str(round(percent))+"%"
        i = i+1
    print(txt_data)
    if mode == "OFL":
        observation(txt_data,rep_id,userid,"IMP001")
        

        
#Function to qualify the log
def parse_log(logpath_file):
    if logpath_file.endswith(".xlsx"):
        sheet_num = 0
        wb=xlrd.open_workbook(logpath_file)
        sheet=wb.sheet_by_index(sheet_num)
        loglines = iter_rows(sheet)
    else:
        fp = open(logpath_file,encoding='utf8', errors='ignore')
        loglines = fp.readlines()
    return loglines        

#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    #matched_patterns = form.getvalue("matched_patterns")
    time = datetime.now()
    time_main = re.sub(r'[:.]','C',str(time))
    date_time = str(time).split(" ")[0]
##    matched_patterns = "P3,P4"
##    userid = "9"
##    rep_id = "714"
##    rep_name = "t7"
##    Outcome = "csv"
##    Logic = "THEN"
##    logpath_file = "C:\\LAPAM2019\\DataLake\\Logs\\Cache\\9\\t7\\WebSphere\\SystemOut.log"
##    mode = "OFL"
##    appName = "TWA"
##    Imp_name = "usageanalysis"
    matched_patterns = "P1"
    userid = "33"
    rep_id = "1519"
    rep_name = "wwwwww"
    Outcome = "csv"
    Logic = "None"
    logpath_file = "C:\\LAPAM2019\\DataLake\\Cache\\33\\wwwwww\\Apache\\apa_sample.txt"
    mode = "OFL"
    appName = "P002"
    Imp_name = "usageanalysis"
    loglines = parse_log(logpath_file)
    generateCSV_IMP001(matched_patterns,userid,rep_id,Outcome,rep_name,loglines,Logic,mode,appName,time_main,date_time,Imp_name)
##    matched_patterns1,userid,rep_id,Outcome1,rep_name,loglines,Logic,mode,appName,time,date_time,I

    
