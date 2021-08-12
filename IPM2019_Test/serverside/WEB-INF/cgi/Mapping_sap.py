import threading,time, sys
import pyodbc,os,re, cgi, cgitb, openpyxl, xlrd
import configparser
from datetime import datetime
from getImperatives import fetch_imp
from generateData import getIMPCount
from getLogType import create_connection
from getLogType import process

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')
DATA_PATH = parser.get('Upload','Onlpath')
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
STAD_dir_path = parser.get('Upload','Stad_dir')
NFR_dir_path = parser.get('Upload','NFR_dir')



_sample_line = 20
imp_id_all = []
PatternIds = []

# called by each thread
class myThread (threading.Thread):
    def __init__(self, threadID, name, Pattern_id,Pattern,logLines,pattern_len,logtype_val):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.Pattern_id = Pattern_id
        self.Pattern = Pattern
        self.logLines = logLines
        self.pattern_len = pattern_len
        self.logtype_val = logtype_val
    def run(self):
        getPatternIds(self.logLines,self.Pattern_id,self.Pattern,self.pattern_len,self.threadID,self.logtype_val)

#funnction call from thread class        
def getPatternIds(logLines,Pattern_id,Pattern,pattern_len,threadID,logtype_val):
    regex = r''+Pattern+''
    man_patt = []
    for line in logLines:
        match = re.match(regex,line)
        if match:
            db1 = pyodbc.connect("DSN="+DSN_NAMEE)
            cursor = db1.cursor()
            getIds = 'select OPT_PAT_LIST from project_pattern_info where APP_NAME=(select APP_NAME from user_info where USER_ID="'+str(userid)+'")  and LOG_TYPE = "'+str(logtype_val)+'";'
            Pattern_opt = cursor.execute(getIds).fetchone()[0]
            man_patt.append(Pattern_id)
            man_patt.append(Pattern_opt)
            PatternIds.append(",".join(man_patt))
            thread_idfin = threadID
            break

#Function to fetch first 200 lines to qualify the log
def parse_log(HOME_PATH,_sample_line,test_name,userid,filename,logtype_val):
    File_path = HOME_PATH + "Cache\\" + userid + "\\" + test_name + "\\" + logtype_val +"\\"
    files = [f for f in os.listdir(File_path) if os.path.isfile(os.path.join(File_path, f))]
    logpath_file = File_path + filename
    loglines1 = []
    if filename.endswith(".zip"):
        siingle_filepath = File_path + files[0]
        fp = open(siingle_filepath,encoding='utf8', errors='ignore')
        head = fp.readlines()
#        loglines1.extend(head)
        fp.close()
        for file in files:
            fp = open(File_path + file,encoding='utf8', errors='ignore')
            head1 = fp.readlines()
            loglines1.extend(head1)
            fp.close() 
        loglines = loglines1
    elif filename.endswith(".xlsx"):
        sheet_num = 0
        wb=xlrd.open_workbook(logpath_file)
        sheet=wb.sheet_by_index(sheet_num)
        loglines = iter_rows(sheet)
        loglines = loglines
        loglines1 = loglines
    else:
        fp = open(logpath_file,encoding='utf8', errors='ignore')
        head = fp.readlines()
        fp.close()
        loglines = head
        loglines1 = head
    return loglines,logpath_file,File_path,loglines1,files

#Function to iterate excel sheet and fetch first 50 lines 
def iter_rows(sheet):
    top_50 = []
    row_i = 0
    row_count = sheet.nrows
    if row_count > 50:
        row_count = 50
    while(row_i< row_count):        
        row = sheet.row(row_i)
        rows = []
        for val in row:
            rows.append(str(val.value))
        row_line = ",".join(rows)
        top_50.append(row_line)
        row_i = row_i+1
    return top_50

#To get PatternId,Regex
def getPatternIds_all(userid,logtype_val):
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    getIds = 'select MAN_PAT_LIST from project_pattern_info where APP_NAME=(select APP_NAME from user_info where USER_ID="'+str(userid)+'") and LOG_TYPE = "'+str(logtype_val)+'";'
    Pattern = cursor.execute(getIds).fetchone()[0]
    db1.commit()
    Patterns = Pattern.split(',')
    return Patterns

def main_process(userid,test_name,filename,mode,appName,logtype_val):   
    #PatternIds = []
    time = datetime.now()
    time = re.sub(r'[:.]','C',str(time))
    date_time = str(time).split(" ")[0]
    if mode == "OFL":
        threads = []
        test_name = test_name.strip().lower()
        Patterns = getPatternIds_all(userid,logtype_val)
        loglines,logpath_file,File_path,loglines1,files = parse_log(DATA_PATH,_sample_line,test_name, userid,filename,logtype_val)#function call to get all PatternIds,regex

        db1 = pyodbc.connect("DSN="+DSN_NAMEE)
        cursor = db1.cursor()
        
        #thread Process
        i = 0
        print(Patterns)
        for P in Patterns:
            getIds = 'select REGEX from pattern_repo where PATTERN_ID="'+str(P)+'";'
            Pattern = cursor.execute(getIds).fetchone()[0]
            db1.commit()
            thread = myThread(i, "Thread-"+str(i), P,Pattern,loglines,len(Patterns),logtype_val)
            threads.append(thread)
            thread.start()
            i = i+1
        threads[len(threads)-1].join()
    #To stop thread
    ##    for thread_val in threads:
    ##        thread_val.join()
    ##        print("completed")
    ##        print(thread_val)
    ##        print(datetime.now())
        print(PatternIds)
        if PatternIds:
            print("in")
            pattern_ids = list(set(PatternIds))
            pattern_list =[]
            pattern_str = ""
            print(pattern_ids)
            for patterns in pattern_ids:
                if not pattern_str:
                    pattern_str = patterns
                else:
                    pattern_str = pattern_str + "," + patterns
            pattern_list.append(pattern_str)
            imp_ids = fetch_imp(pattern_list, userid, test_name,mode,appName,logtype_val)#To get the Imperatives for Patterns
##            print(imp_ids)
            report_query = 'SELECT rep_id FROM report_info where user_id="'+userid+'" and rep_name ="'+test_name+'";'
            rep_id= cursor.execute(report_query).fetchone()[0]
            getIMPCount(str(rep_id),str(userid),loglines1,test_name,files,File_path,mode,appName,str(time),str(date_time),logtype_val)#Function call for decide flow whether SPSO|SPMO|MPSO|MPMO
            print("Rep_id - " + str(rep_id))
            #print(imp_ids)
        else:
            print("No Patterns got match")
    elif mode == "ONL":
        time = datetime.now()
        time = re.sub(r'[:.]','C',str(time))
        date_time = str(time).split(" ")[0]
        File_path = DATA_PATH+"Online/"
        if appName == "TWA":
            File_paths = [DATA_PATH+"Online/Standard/",DATA_PATH+"Online/Custom/"]
        elif appName == "CBOL":
            File_paths = [DATA_PATH+"Online/gmliMsg/",DATA_PATH+"Online/Messages/"]
        for File_path1 in File_paths:
            print(File_path1)
            files = os.listdir(File_path1)
            match_log = re.match(r'.*Online\/(.*?)\/',File_path1)
            if match_log:
                logtype_val = match_log.group(1)
            head = []
            for file in files:
                logpath_file = File_path1+file
                fp = open(logpath_file,encoding='utf8', errors='ignore')
                head.extend(fp.readlines())
                fp.close()
            imp_ids = fetch_imp("", "", "",mode,appName,logtype_val)#To get the Imperatives for Patterns
            getIMPCount("","",head,"","",File_path,mode,appName,str(time),str(date_time),logtype_val)#Function call for decide flow whether SPSO|SPMO|MPSO|MPMO
            imp_id_all.extend(imp_ids)
        
        #print(datetime.now())
    


if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    if sys.argv[1] == "empty":
        userid = ""
    else:
        userid = sys.argv[1]
    if sys.argv[3] == "empty":
        report_name = ""
    else:
        report_name = sys.argv[3]
    logName = sys.argv[3]
    appName = sys.argv[4]
    filename = sys.argv[5]
    mode = sys.argv[6]
    prjid = sys.argv[2]

    
    #for manual execute
##    #Online
##    userid = "41"
##    report_name = "test_g7"
##    logName = "test_g7"
##    appName = "Workshop"
##    filename = "STAD-ST03.xlsx"
##    prjid = "693"
    #Offline
##    filename = "ST03_1.xlsx"
##    userid = "41"
##    report_name = "pr5"
##    Stad_dir = "C:\\LAPAM2019\\DataLake\\Cache\\41\\pr5\\STAD\\ST03_1.xlsx"
##    NFR_dir = "C:\\LAPAM2019\\DataLake\\Cache\\41\\pr5\\NFR\\NFR.xlsx"
##    prjid = "730"
##    mode = "OFL"
##    file_format="German"
##    Server_dir = " "
    
    #main_process(username,userid,test_name,filename,mode,appName)
    log_filename = "ST03.xlsx"
    Stad_dir = STAD_dir_path + userid + "\\"+report_name +"\\STAD\\"
    NFR_dir = STAD_dir_path + userid + "\\"+report_name +"\\NFR\\NFR.xlsx"
    
    if mode == "OFL":
        report_name = report_name.lower()
        logtype_arr = create_connection(appName)
        filename_arr = filename.split(',')
        print(filename_arr)
        rep_id =""
        db1 = pyodbc.connect("DSN="+DSN_NAMEE)
        cursor = db1.cursor()
        for logtype in logtype_arr:
            logtype_val = str(logtype).split('\'')[1]
            print(logtype_val)
            filepath = DATA_PATH + "Cache\\" + userid + "\\" + report_name + "\\" + logtype_val
            
##            for filename_val in filename_arr:
##                if(logtype_val == filename_val.split('_')[0]):
##                    log_filename = filename_val.split('_')[1]
##                    print(filename_val)
            if os.path.exists(filepath):                
                # Check for SAP logs                
                for filename_val in filename_arr:
                    if "STAD" in filename_val and logtype_val in filename_val.split('-')[0]:
                        Stad_dir = STAD_dir_path + userid + "\\"+report_name +"\\STAD\\" + filename_val.split('-')[1]
                        log_filename = filename_val.split('-')[1]                        
                        main_process(userid,report_name,log_filename,mode,appName,logtype_val)
                        #get Imperative list
                        report_query = 'SELECT rep_id FROM report_info where user_id='+userid+' and rep_name ="'+report_name+'";'
                        rep_id= cursor.execute(report_query).fetchone()[0]
                        process(Stad_dir,NFR_dir,Server_dir,userid,report_name,file_format,rep_id)
                    elif "NFR" in filename_val and logtype_val in filename_val.split('-')[0]:
                        NFR_dir = STAD_dir_path + userid + "\\"+report_name +"\\NFR\\" + filename_val.split('-')[1]
                        log_filename = filename_val.split('-')[1]                
                        main_process(userid,report_name,log_filename,mode,appName,logtype_val)
                        #get Imperative list
                        report_query = 'SELECT rep_id FROM report_info where user_id='+userid+' and rep_name ="'+report_name+'";'
                        rep_id= cursor.execute(report_query).fetchone()[0]

                        process(Stad_dir,NFR_dir,Server_dir,userid,report_name,file_format,rep_id)
                
            
                PatternIds = []
                

        
##        print("REP_ID - " + str(rep_id))
        db2 = pyodbc.connect("DSN="+DSN_NAMEE)
        cursor = db2.cursor()
        query = 'select concat(IMP_ID ,"-" , IMP_DESCRIPTION) from imperative_info where IMP_ID in (select imp_id from report_imperatives_patterns where Rep_id = '+str(rep_id)+' and user_id='+str(userid)+');'
        cursor.execute(query)
        res = cursor.fetchall()
        imp_id_all = [f[0] for f in res]
        print(imp_id_all)
    else:
        logtype_val = "Standard"
        main_process(userid,report_name,filename,mode,appName,logtype_val)
        PatternIds = []
        print(set(imp_id_all))

        

    


