from datetime import date, datetime, timedelta
import re,os,shutil, cgi, cgitb,pyodbc
import configparser


#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
ONL_Report = parser.get('Report','onlpathES')
start_flag = 0

def generateCSV_IMP004(matched_patterns1,userid,rep_id,Outcome,rep_name,Logic,input_dir,mode,appName,time,date_time,Imp_name):
    exh_li = []
    flag = 0
    start_flag = 0
    matched_patterns = matched_patterns1.split(",")
    if mode == "ONL":
        input_dir = input_dir+"JVM\\"
    input_dir = os.path.dirname(input_dir)+"\\"
    con = pyodbc.connect("DSN="+DSN_NAMEE)
    cur = con.cursor()
    pattern_rex = {}
    exh_li  = []
    ONL_csvarr = []
    for pattern in matched_patterns:
        query= 'SELECT REGEX from pattern_repo where PATTERN_ID = "'+pattern+'" ;'
        regex = con.execute(query).fetchone()[0]
        pattern_rex[pattern]=regex
    Gc_arr = []
    used_text_arr = []
    tenure_text_arr = []
    nursery_text_arr = []
    GC_text_arr = []
    if os.path.isdir(input_dir):
        files = os.listdir(input_dir)
##        files = [f for f in files if f.endswith(".001")]
        if files:
            for file in files:
                start_flag = start_flag+1
                time_file,ONL_csvarr = file_process(input_dir+file,rep_name,Gc_arr,pattern_rex,exh_li,used_text_arr,tenure_text_arr,nursery_text_arr,GC_text_arr,start_flag)
                if mode == "OFL":
                    Html_process(input_dir+file,rep_name,time_file,userid,rep_id,exh_li,mode,appName,time,date_time,Imp_name)
    else:
        if input_dir:
            start_flag = start_flag+1
            file = os.path.basename(input_dir)
            time_file,ONL_csvarr = file_process(input_dir,rep_name,Gc_arr,pattern_rex,exh_li,used_text_arr,tenure_text_arr,nursery_text_arr,GC_text_arr,start_flag)
            if mode == "OFL":
                Html_process(input_dir+file,rep_name,time_file,userid,rep_id,exh_li,mode,appName,time,date_time,Imp_name)
            
    if Gc_arr:
        if mode == "OFL":
            csv_filename = appName+"_"+rep_name.lower()+"_"+Imp_name+".csv"
            common_fileName = appName+"_"+rep_name.lower()+"_HeapMemory"
            dir_path = "../../../WEB-INF/classes/static/html/Reports/"+str(userid)+"_"+str(rep_id)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            output = dir_path+"/"+csv_filename
            usagefile_txt = open(csv_filename,"w")
        elif mode == "ONL":
            if not os.path.exists("../../../WEB-INF/classes/static/html/Online"):
                os.mkdir("../../../WEB-INF/classes/static/html/Online")
            csv_filename = appName+"_"+Imp_name+"_"+str(date_time)+ ".csv"
            common_fileName = appName+"_HeapMemory_ONL_"+str(date_time)
            newfileName = appName+"_HeapMemory_ONL_"+str(time)
            dir_path = "../../../WEB-INF/classes/static/html/Online"
            output = dir_path+"/"+csv_filename
            usagefile_txt = open(csv_filename, 'w') 
        usagefile_txt.write("Used Tenured(After),Free Tenured(After),Free Nursery(After),GC Completed,Exhausted,Timestamp\n")
        for i in Gc_arr:
            usagefile_txt.write(i+"\n")
        usagefile_txt.close()
        shutil.move(csv_filename, output)
        used_text = "".join(used_text_arr)
        tenure_text = "".join(tenure_text_arr)
        nursery_text = "".join(nursery_text_arr)
        GC_text = "".join(GC_text_arr)
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
        if mode == "ONL":
            newfileName = appName+"_HeapMemory_ONL_"+str(time)+ ".csv"
            newfile = ONL_Report+newfileName
            usagefile_csv = open(newfileName, 'w') 
            usagefile_csv.write("Timestamp,Used Tenured(After),Free Tenured(After),Free Nursery(After),GC Completed\n")
            for i in ONL_csvarr:
                usagefile_csv.write(i+"\n")
            usagefile_csv.close()
            shutil.move(newfileName,newfile)
    else:
        print("Please Upload The Valid Log")
        
        

def file_process(input_dir, logname,Gc_arr,pattern_rex,exh_li,used_text_arr,tenure_text_arr,nursery_text_arr,GC_text_arr,start_flag):

    convert_timeformat = "%a %b %d %H:%M:%S %Y"
    file_timeformat = "%b %d %H:%M:%S %Y"
    datetimeformat = "%Y-%m-%dT%H:%M:%S.%f"
    fp = open(input_dir,encoding="utf8")
    flag =0
    time_arr = []
    ONL_csvarr = []
    match_aftime,match_gc_start,match_tenured,match_nursery,match_gc,match_gc1,match_gc_end = "","","","","","",""
    match_time,match_aftime,match_gcend,match_tenure_val,match_nursery_val = "","","","",""
    #start_flag = 0
    for line in fp:
        if 'P12' in pattern_rex.keys():
            match_time = re.match(r''+str(pattern_rex['P12'])+'',line)
        if 'P13' in pattern_rex.keys():
            match_gc_start = re.match(r''+str(pattern_rex['P13'])+'',line)
        if 'P14' in pattern_rex.keys():
            match_tenured = re.match(r''+str(pattern_rex['P14'])+'',line)
        if 'P15' in pattern_rex.keys():
            match_nursery = re.match(r''+str(pattern_rex['P15'])+'',line)
        if 'P16' in pattern_rex.keys():
            match_gc = re.match(r''+str(pattern_rex['P16'])+'',line)
        if 'P17' in pattern_rex.keys():
            match_gc1 = re.match(r''+str(pattern_rex['P17'])+'',line)
        if 'P18' in pattern_rex.keys():
            match_gc_end = re.match(r''+str(pattern_rex['P18'])+'',line)
        if 'P19' in pattern_rex.keys():
            match_aftime = re.match(r''+str(pattern_rex['P19'])+'',line)
        if 'P20' in pattern_rex.keys():
            match_gcend = re.match(r''+str(pattern_rex['P20'])+'',line)
        if 'P121' in pattern_rex.keys():
            match_tenure_val = re.match(r''+str(pattern_rex['P21'])+'',line)
        if 'P22' in pattern_rex.keys():
            match_nursery_val = re.match(r''+str(pattern_rex['P22'])+'',line)
        if (match_time) and (flag==0):
            #print(line)
            timestamp = ""
            Free_Tenured = ""
            Total_Tenured = ""
            used_tenured = ""
            Free_Nursery = ""
            GC_comp = ""
            timestamp = match_time.group(1)
            d = datetime.strptime(timestamp, file_timeformat)
            timestamp = datetime.strftime(d, convert_timeformat)
            flag = 1
        elif (match_gc_start) and (flag == 1):
            flag = 2
        elif (match_tenured) and (flag ==3):
            Free_Tenured = match_tenured.group(1)
            Total_Tenured = match_tenured.group(2)
            used_tenured = int(Total_Tenured) - int(Free_Tenured)
##            used_tenured = "{:,}".format(used_tenured)
##            Free_Tenured = "{:,}".format(int(Free_Tenured))
            Gc_arr.append(str(used_tenured)+","+str(Free_Tenured)+","+str(Free_Nursery)+","+str(GC_comp)+",No,"+str(timestamp))
            ONL_csvarr.append(json_process(str(used_tenured),str(Free_Tenured),str(Free_Nursery),str(GC_comp),str(timestamp),used_text_arr,tenure_text_arr,nursery_text_arr,GC_text_arr,start_flag))
            exh_li.append("No")
            time_arr.append(str(timestamp))
            flag = 0
            timestamp = ""
            Free_Tenured = ""
            Total_Tenured = ""
            used_tenured = ""
            Free_Nursery = ""
            GC_comp = ""
            start_flag = 1
        elif (match_nursery) and (flag ==3):
            Free_Nursery = match_nursery.group(1)
##            Free_Nursery = "{:,}".format(int(Free_Nursery))
        elif (match_gc or match_gc1) and (flag ==2):
            if match_gc:
                GC_comp = int(float(match_gc.group(1)))
            if match_gc1:
                GC_comp = int(float(match_gc1.group(1)))
        elif (match_gc_end) and (flag ==2):
            flag = 3
        if match_aftime:
            timestamp = ""
            Free_Tenured = ""
            Total_Tenured = ""
            used_tenured = ""
            Free_Nursery = ""
            timestamp = match_aftime.group(1)
            d = datetime.strptime(timestamp, datetimeformat)
            timestamp = datetime.strftime(d, convert_timeformat)
        if match_gcend:
            GC_comp = match_gcend.group(1)
            if timestamp == "":
                timestamp = match_gcend.group(2)
                d = datetime.strptime(timestamp, datetimeformat)
                timestamp = datetime.strftime(d, convert_timeformat)
            flag = 4
        elif match_nursery_val and (flag==4):
            Free_Nursery = match_nursery_val.group(1)
        elif match_tenure_val and (flag==4):
            Free_Tenured = match_tenure_val.group(1)
            Total_Tenured = match_tenure_val.group(2)
            used_tenured = int(Total_Tenured) - int(Free_Tenured)            
            Gc_arr.append(str(used_tenured)+","+str(Free_Tenured)+","+str(Free_Nursery)+","+str(GC_comp)+",No,"+str(timestamp))
            ONL_csvarr.extend(json_process(str(used_tenured),str(Free_Tenured),str(Free_Nursery),str(GC_comp),str(timestamp),used_text_arr,tenure_text_arr,nursery_text_arr,GC_text_arr,start_flag))
            exh_li.append("No")
            time_arr.append(str(timestamp))
            flag = 0
            timestamp = ""
            Free_Tenured = ""
            Total_Tenured = ""
            used_tenured = ""
            Free_Nursery = ""
            GC_comp = ""
            start_flag = 1
    sort_time = sorted(time_arr, key=lambda x: datetime.strptime(x, convert_timeformat))
##    print(sort_time)
    start = sort_time[0]
    d = datetime.strptime(start, convert_timeformat)
    start = datetime.strftime(d, '%Y-%m-%d %H:%M:%S')
    end = sort_time[len(sort_time)-1]
    d = datetime.strptime(end, convert_timeformat)
    end = datetime.strftime(d, '%Y-%m-%d %H:%M:%S')
    timing = start+" to "+end
    return timing,ONL_csvarr

def json_process(used_tenured,Free_Tenured,Free_Nursery,GC_comp,timestamp,used_text_arr,tenure_text_arr,nursery_text_arr,GC_text_arr,start_flag):
    ONL_csvtxt = ""
    defs={'KB':1024, 'MB':1024**2, 'GB':1024**3, 'TB':1024**4}
    tenure = "GB"
    nursery = "MB"
    behavior_timeformat = "%Y-%m-%d %H:%M:%S"
    convert_timeformat = "%a %b %d %H:%M:%S %Y"
    UtenureA = re.sub(r',','',used_tenured)
    UtenureA = '{:0.2} {}'.format(int(UtenureA)/defs[tenure],tenure)
    UtenureA = UtenureA.split(" ")[0]
    ftenureA = re.sub(r',','',Free_Tenured)
    ftenureA = '{:0.2} {}'.format(int(ftenureA)/defs[tenure],tenure)
    ftenureA = ftenureA.split(" ")[0]
    fnurseryA = re.sub(r',','',Free_Nursery)
    fnurseryA = '{:0.2} {}'.format(int(fnurseryA)/defs[nursery],nursery)
    fnurseryA = fnurseryA.split(" ")[0]
    GC_comp = re.sub(r',','',GC_comp)
    Gc_comp  = int(GC_comp)
    d = datetime.strptime(timestamp, convert_timeformat)
    timestamp = datetime.strftime(d, behavior_timeformat)
    if start_flag == 0:
        start_flag = 1
        used_text_arr.append("{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(UtenureA)+"}")
        tenure_text_arr.append("{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(ftenureA)+"}")
        nursery_text_arr.append("{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(fnurseryA)+"}")
        GC_text_arr.append("{\"DateTime\":\""+str(timestamp)+"\",\"GC\":"+str(Gc_comp)+"}")
        ONL_csvtxt = str(timestamp)+","+str(UtenureA)+","+str(ftenureA)+","+str(fnurseryA)+","+str(Gc_comp)
    else:
        used_text_arr.append(",{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(UtenureA)+"}")
        tenure_text_arr.append( ",{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(ftenureA)+"}")
        nursery_text_arr.append(",{\"DateTime\":\""+str(timestamp)+"\",\"After\":"+str(fnurseryA)+"}")
        GC_text_arr.append(",{\"DateTime\":\""+str(timestamp)+"\",\"GC\":"+str(Gc_comp)+"}")
        ONL_csvtxt = str(timestamp)+","+str(UtenureA)+","+str(ftenureA)+","+str(fnurseryA)+","+str(Gc_comp)
    return ONL_csvtxt



def Html_process(input_dir,Log_Name,fileName,userid,rep_id,exh_li,mode,appName,time,date_time,Imp_name):
    if mode == "OFL":
        fileName2 = re.sub(r':','C',fileName)
        fileName2 = appName+"_"+Log_Name.lower()+"_"+Imp_name+"_"+fileName2
        file_name = str(userid)+"_"+str(rep_id)
        dir_path = "../../../WEB-INF/classes/static/html/Reports/"+file_name
    elif mode == "ONL":
        fileName1 = re.sub(r':','C',fileName)
        fileName2 = appName+"_"+Imp_name+"_ONL_"+str(date_time)+"_"+fileName1
        file_name = str(fileName)
        dir_path = "../../../WEB-INF/classes/static/html/Online"
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    output = dir_path+"/"+fileName2+".html"
    out_path = dir_path+"/"
    os.system("java -Xmx1000m -jar jar/ga458.jar -I \""+input_dir+"\"; "+"\""+output+"\"")
    for file in os.listdir(out_path):
        if file.endswith('.png'):
            os.remove(out_path+file)
    process_html(output,exh_li,file_name,fileName,mode,appName,time,date_time,Imp_name,Log_Name,userid,rep_id)



# Function to create gauge_out.txt
def process_html(input_dir,exh_li,folder_name,fileName,mode,appName,time,date_time,Imp_name,rep_name,userid,rep_id):
    file_timeformat = "%a %b %d %H:%M:%S %Y"
    convert_timeformat = "%d-%b-%Y %H:%M"
    savefile_timeformat = "%d_%b_%Y_%H_%M"
    defs={'KB':1024, 'MB':1024**2, 'GB':1024**3, 'TB':1024**4}
    tenure = "GB"
    avgten_end = "MB"
    totmem = 0
    totmem1 = 0
    oof = 0
    large_all = 0
    overallGC = 0
    longGC = 0
    maxall = 0
    avg_ten = 0
    fp = open(input_dir,encoding="utf8")
    for line in fp:
        match_totmem = re.match(r'.*vm argument \: \-Xmx(.*?)m.*',line)
        match_totmem1 = re.match(r'.*\<BR\>maxHeapSize \: (.*?) bytes\<BR\>.*',line)
        match_avgten = re.match(r'.*Average Tenured Area usage\<\/B\>\<\/span\> \: (.*?) bytes \<\/li\>.*',line)
        match_overall = re.match(r'.*Overall Garbage Collection overhead\<\/B\>\<\/span\> : (.*?)%\<\/li\>.*',line)
        match_longGc = re.match(r'.*Longest Garbage Collections\<\/B\>\<\/span\>\<BR\>(.*?) ms \(.*',line)
        match_maxall= re.match(r'.*Maximum Allocation Request\<\/B\>\<\/span\> \: (.*?) bytes \(.*',line)
        match_oof= re.match(r'.*Java heap exhaustion\<\/B\>\<\/span\> \: (.*?)\<\/li\>.*',line)
        match_start = re.match(r'.*First Garbage Collection\<\/B\>\<\/span\> : (.*?)\<\/li\>\<li\>.*',line)
        match_ends = re.match(r'.*Last Garbage Collection\<\/B\>\<\/span\> : (.*?)\<\/li\>\<li\>.*',line)
        if match_totmem:
            totmem = match_totmem.group(1)
        if match_oof:
            oof = match_oof.group(1)
        if match_avgten:
            avg_ten = match_avgten.group(1)
            avg_ten = re.sub(r',','',avg_ten)
            avg_ten = '{:0.2} {}'.format(int(avg_ten)/defs[avgten_end],avgten_end)
            avg_ten = avg_ten.split(" ")[0]
        if match_overall:
            overallGC = match_overall.group(1)
        if match_longGc:
            longGC_ms = match_longGc.group(1)
            longGC_ms = re.sub(r',','',longGC_ms)
            longGC = round(int(longGC_ms)/1000)
        if match_maxall:
            maxall = match_maxall.group(1)
            maxall = re.sub(r',','',maxall)
            maxall = '{:0.2} {}'.format(int(maxall)/defs[avgten_end],avgten_end)
            maxall_arr = maxall.split(" ")
            maxall = str(round(float(maxall_arr[0])))+" "+maxall_arr[1]
        match_exh = [s for s in exh_li if "Yes" in s]
        if len(match_exh)>1:
            large_all = 1
        if totmem != 0:
            totmem = round((float(avg_ten)/round(int(totmem)))*100)
        elif match_totmem1:
            totmem1 = match_totmem1.group(1)
            totmem1 = re.sub(r',','',totmem1)
            totmem1 = '{:0.2} {}'.format(int(totmem1)/defs[avgten_end],avgten_end)
            totmem1 = totmem1.split(" ")[0]
            totmem = round((float(avg_ten)/round(float(totmem1)))*100)

        if match_start:
            start = datetime.strptime(match_start.group(1), file_timeformat)
            savefile_st = datetime.strftime(start, savefile_timeformat)
            start = datetime.strftime(start, convert_timeformat)
        if match_ends:
            ends = datetime.strptime(match_ends.group(1), file_timeformat)
            ends = datetime.strftime(ends, convert_timeformat)
##        print(str(totmem)+"|"+str(oof)+"|"+str(overallGC)+"|"+str(longGC)+"|"+str(maxall))
##        print("\nLARGERST ALLOCATION : "+maxall+"="+str(large_all))
    fp.close()
    if mode == "OFL":
        fileName = re.sub(r':','C',fileName)
        fileName = appName+"_"+rep_name.lower()+"_"+Imp_name+"_"+fileName
        file_name = str(userid)+"_"+str(rep_id)
        folder_name = "../../../WEB-INF/classes/static/html/Reports/"+file_name
    elif mode == "ONL":
        fileName1 = re.sub(r':','C',fileName)
        fileName = appName+"_"+Imp_name+"_"+fileName1+"_ONL_"+str(date_time)
        newfileName = ONL_Report+appName+"_"+Imp_name+"_ONL_"+fileName1+"_"+str(time)+".csv"
        folder_name = "../../../WEB-INF/classes/static/html/Online"
    txt_filename =fileName+".txt"
    usagefile_txt = open(txt_filename,"w")
    usagefile_txt.write("TOTAL MEMORY=")
    usagefile_txt.write(str(totmem))
    usagefile_txt.write("\nOUT OF MEMORY : "+oof+"=")
    usagefile_txt.write(str(oof))
    usagefile_txt.write("\nGC Overhead : "+str(overallGC)+" %=")
    usagefile_txt.write(str(overallGC))
    usagefile_txt.write("\nGC Time : "+str(longGC_ms)+" ms=")
    usagefile_txt.write(str(longGC))
    usagefile_txt.write("\nLargest Allocation : "+maxall+"=")
    usagefile_txt.write(str(large_all))
    usagefile_txt.write("\nLog Timing=")
    usagefile_txt.write(start +" to "+ends)
    usagefile_txt.close()
    shutil.move(txt_filename, folder_name+"/"+txt_filename)

    #csv creation for online
    if mode == "ONL":
        csv_filename =fileName+".csv"
        usagefile_csv = open(csv_filename,"w")
        usagefile_csv.write("TOTAL MEMORY,OUT OF MEMORY,GC Overhead,GC Time,Largest Allocation,Log_StartTime,Log_EndTime\n")
        usagefile_csv.write(str(totmem)+","+str(oof)+"&&"+str(oof)+","+str(overallGC)+" %&&"+str(overallGC)+","+str(longGC_ms)+" ms&&"+str(longGC)+","+str(maxall)+"&&"+str(large_all)+","+str(start)+","+str(ends)+"\n")
        usagefile_csv.close()
        shutil.move(csv_filename, newfileName)

            
#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage
    time = datetime.now()
    time = re.sub(r'[:.]','C',str(time))
    date_time = str(time).split(" ")[0]
    matched_patterns = "P12,P13,P14,P15,P16,P17,P18,P19,P20,P21,P22"
    userid = ""
    rep_id = ""
    rep_name = ""
    Outcome = "json,txt"
    Logic = "Customization"
    input_dir = "C:\\LAPAM2019\\DataLake\\Online\\"
    mode = "ONL"
    appName = "TWA"
    Imp_name = "memory analysis"
    generateCSV_IMP004(matched_patterns,userid,rep_id,Outcome,rep_name,Logic,input_dir,mode,appName,time,date_time,Imp_name)
    
