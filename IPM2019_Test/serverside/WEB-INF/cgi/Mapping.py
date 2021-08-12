import threading,time, sys
import pyodbc,os,re, cgi, cgitb, openpyxl, xlrd
import configparser
from datetime import datetime
from getImperatives import fetch_imp
from generateData import getIMPCount
from getLogType import create_connection

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')
##DATA_PATH = parser.get('Upload','Onlpath')
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

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
    print(getIds)
    Pattern = cursor.execute(getIds).fetchone()[0]
    print(Pattern)
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
            imp_id_all.extend(imp_ids)
            report_query = 'SELECT rep_id FROM report_info where user_id="'+userid+'" and rep_name ="'+test_name+'";'
            rep_id= cursor.execute(report_query).fetchone()[0]
            getIMPCount(str(rep_id),str(userid),loglines1,test_name,files,File_path,mode,appName,str(time),str(date_time),logtype_val)#Function call for decide flow whether SPSO|SPMO|MPSO|MPMO
            print("Rep_id - " + str(rep_id))
            #print(imp_ids)
        else:
            print("No Patterns got match")
    elif mode == "ONL":
        File_path = DATA_PATH+"Online/"
        File_path1 = DATA_PATH+"Online/WebSphere/"
        files = os.listdir(File_path1)
        head = []
        logpath_file = File_path1+files[0]
        fp = open(logpath_file,encoding='utf8', errors='ignore')
        head = fp.readlines()
        fp.close()
        imp_ids = fetch_imp("", "", "",mode,appName,logtype_val)#To get the Imperatives for Patterns
        getIMPCount("","",head,"","",File_path,mode,appName,str(time),str(date_time),logtype_val)#Function call for decide flow whether SPSO|SPMO|MPSO|MPMO
        imp_id_all.extend(imp_ids)
        
        #print(datetime.now())
    


if __name__ == "__main__":
    print("Content-type: text/html \n");
##    form = cgi.FieldStorage()
##    if sys.argv[1] == "empty":
##        userid = ""
##    else:
##        userid = sys.argv[1]
##    if sys.argv[3] == "empty":
##        report_name = ""
##    else:
##        report_name = sys.argv[3]
##    appName = sys.argv[4]
##    filename = sys.argv[5]
##    mode = sys.argv[6]
    
    #for manual execute
##    #Online
##    log_filename = "SystemOut_18.11.18_23.00.00.log"
##    userid = ""
##    test_name = ""
##    username=""
##    mode = "ONL"
##    appName = "TWA"
##    logtype_val = "Websphere"
    #Offline
    filename = "OSP-OSP_input1.csv"
    userid = "44"
    test_name = "Test24_4"
    username="murex"
    mode = "OFL"
    appName = "MUREX"
    report_name = "Test24_4"
##    #main_process(username,userid,test_name,filename,mode,appName)
    if mode == "OFL":
        logtype_arr = create_connection(appName)
        filename_arr = filename.split(',')
        print(filename_arr)
        for logtype in logtype_arr:
            print(logtype)
            logtype_val = str(logtype).split('\'')[1]
            print(logtype_val)
            filepath = DATA_PATH + "Cache\\" + userid + "\\" + report_name + "\\" + logtype_val
            print(DATA_PATH)
            for filename_val in filename_arr:
                if(logtype_val == filename_val.split('-')[0]):
                    log_filename = filename_val.split('-')[1]
            if os.path.exists(filepath):
                main_process(userid,report_name,log_filename,mode,appName,logtype_val)
                PatternIds = []
        print(imp_id_all)
    else:
        logtype_val = sys.argv[12]
        main_process(userid,report_name,filename,mode,appName,logtype_val)
        PatternIds = []
        print(imp_id_all)

    


