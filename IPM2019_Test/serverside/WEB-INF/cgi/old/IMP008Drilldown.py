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
DSN_NAME = parser.get('DSN','DSN_NAME')
ONL_Report = parser.get('Report','onlpathES')

def generateCSV_IMP008drill(userid,rep_id,rep_name,mode,appName,time_main,date_time,Imp_name,startdate,enddate,search):
    service_arr,header_arr = generateDC(userid,rep_id,rep_name,appName,Imp_name,startdate,enddate,mode,search)
    generateUsage(service_arr,userid,rep_id,rep_name,appName,Imp_name,startdate,enddate,mode,search)
    print(set(service_arr))
    print(set(header_arr))

def generateUsage(service_arr,userid,rep_id,rep_name,appName,Imp_name,startdate,enddate,mode,search):
    if mode == "OFL":
        rep_name1 = str(userid)+"_"+str(rep_id)
        filename = appName+"_"+rep_name.lower()+"_"+Imp_name+"_"+str(search)+".csv"
        movepath = "Reports/"+rep_name1
        if not os.path.exists("../../../html/Reports/"+rep_name1):
            os.mkdir("../../../html/Reports/"+rep_name1)
        usagefile = open(filename,"w")
    usagefile.write("Service Call,Total Count,Pass Count,Fail Count,Min. Response time(ms),Max. Response time(ms),Avg. Response time(ms)\n")
    if mode == "OFL":
        response_arr = []
        filepath = "../../../html/Reports/"+rep_name1+"/"
        files = [f for f in os.listdir(filepath) if (f.endswith("_Usage.csv")) and (Imp_name in f) and (appName in f) and (rep_name.lower().strip() in f)]
        for file in files:
            fp = open(filepath+file)
            fp_lines = fp.readlines()
            fp.close()
            for line in fp_lines[1:]:
                line_arr = line.split(",")
                currentdate = datetime.strptime(line_arr[2], "%Y-%m-%d %H:%M:%S")
                currentdate = datetime.strftime(currentdate,"%m/%d/%y %H:%M")
                if(currentdate >= startdate) and (enddate >= currentdate):
                    response_arr.append(line)
        uniq_servicecall = set(service_arr)
        for service_req in uniq_servicecall:
            match_response = [int(s.split(",")[4]) for s in response_arr if service_req == s.split(",")[0]]
            match_pass = [s for s in response_arr if (service_req == s.split(",")[0]) and ("Pass" == s.split(",")[3])]
            match_fail = [s for s in response_arr if (service_req == s.split(",")[0]) and ("Fail" == s.split(",")[3])]
            match_avg = [int(s.split(",")[4]) for s in response_arr if (service_req == s.split(",")[0]) and ("Pass" == s.split(",")[3])]
            
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
    shutil.move(filename, "../../../html/"+movepath+"/"+filename)
                
    

def generateDC(userid,rep_id,report_name,appName,Imp_name,startdate,enddate,mode,search):
    service_arr = []
    header_arr = []
    data_dict = {}
    rep_name = str(userid)+"_"+str(rep_id)
    if mode == "OFL":
        filepath = "../../../html/Reports/"+rep_name+"/"
        files = [f for f in os.listdir(filepath) if (f.endswith("_DC.csv")) and (Imp_name in f) and (appName in f) and (report_name.lower().strip() in f)]
        for file in files:
            servicecall_mat = re.match(r'.*\_(.*)\_DC.csv',file)
            if servicecall_mat:
                serviceCall = servicecall_mat.group(1)
            fp = open(filepath+file)
            fp_lines = fp.readlines()
            fp.close()
            head = fp_lines[0]
            head_arr = head.split(",")
            data_arr = []
            header = []
            j = 0
            for line in fp_lines[1:]:
                match_str = re.match(r'.*[,-]{1}'+search+'[,\/]{1}.*',line)
                if match_str:
                    line_arr = line.split(",")
                    line_index = [i for i, e in enumerate(line_arr) if search in e]
                    if line_index:
                        header = []
                        for i in line_index:
                            if "-" in head_arr[i]:
                                header.append(head_arr[i].split("-")[1])
                            else:
                                header.append(head_arr[i])
                    currentdate = datetime.strptime(line_arr[1], "%Y-%m-%d %H:%M:%S")
                    currentdate = datetime.strftime(currentdate,"%m/%d/%y %H:%M")
                    if(currentdate >= startdate) and (enddate >= currentdate):
                        service_arr.append(serviceCall)
                        header_arr.extend(header)
                        if j == 0:
                            head_fin = head_arr[:3]
                            head_fin.extend([f.strip().split("-")[1] for f in head_arr[3:] if "body-" in f])
                            data_arr.append(",".join(head_fin))
                        line_fin = line_arr[:3]
                        line_fin.extend(["".join(str(f).strip().split("body-")) for f in line_arr[3:] if "body-" in f])
                        data_arr.append(",".join(line_fin))
                        j= j+1
            if data_arr:
                filename = appName+"_"+report_name.lower()+"_"+Imp_name+"_"+serviceCall+"_"+str(search)+".csv"
                movepath = "Reports/"+rep_name
                if not os.path.exists("../../../html/"+movepath):
                    os.mkdir("../../../html/"+movepath)
                usagefile = open(filename,"w")
                for val in data_arr:
                    usagefile.write(val+"\n")
                usagefile.close()
                shutil.move(filename, "../../../html/"+movepath+"/"+filename)
    return service_arr,header_arr
                        
            
            

#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    userid = form.getvalue('userid')
    rep_id = form.getvalue('rep_id')
    rep_name = form.getvalue('Txt_reportname')
    mode = form.getvalue('mode')
    appName = form.getvalue('appname')
    Imp_name = form.getvalue('Imp_name')
    start_time = form.getvalue('startdate')
    end_time = form.getvalue('enddate')
    search = form.getvalue('search')
    #matched_patterns = form.getvalue("matched_patterns")
    time = datetime.now()
    time_main = re.sub(r'[:.]','C',str(time))
    date_time = str(time).split(" ")[0]
##    userid = "5"
##    rep_id = "3"
##    rep_name = "citi_ch"
##    mode = "OFL"
##    appName = "TWA"
##    Imp_name = "search"
##    start_time = "11/17/18 23:26"
##    end_time = "11/18/18 21:53"
##    search = "AT56790"
    startdate = datetime.strptime(start_time, '%m/%d/%y %H:%M')
    startdate = datetime.strftime(startdate,"%m/%d/%y %H:%M")
    enddate = datetime.strptime(end_time, '%m/%d/%y %H:%M')
    enddate = datetime.strftime(enddate,"%m/%d/%y %H:%M")
    generateCSV_IMP008drill(userid,rep_id,rep_name,mode,appName,time_main,date_time,Imp_name,startdate,enddate,search)
