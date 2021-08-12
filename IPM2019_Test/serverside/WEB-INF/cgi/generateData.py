import threading
import pyodbc,os,re
import configparser
from IMP001 import generateCSV_IMP001
from IMP003 import generateCSV_IMP003
from IMP002 import generateCSV_IMP002
from IMP004 import generateCSV_IMP004
from IMP005 import generateCSV_IMP005
from IMP006 import generateCSV_IMP006
from IMP008 import generateCSV_IMP008
#fetch the upload path,DSN_NAMEE from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

# called by each thread
class myThread (threading.Thread):
    def __init__(self, threadID, name, IMP_Count, reportid, userid,loglines,test_name,files,File_path,mode,appName,time,date_time,logtype_val):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.IMP_Count = IMP_Count
        self.reportid = reportid
        self.userid = userid
        self.loglines = loglines
        self.test_name = test_name
        self.files = files
        self.File_path = File_path
        self.mode = mode
        self.appName = appName
        self.time = time
        self.date_time = date_time
        self.logtype_val = logtype_val
    def run(self):
        decideFlow(self.name,self.IMP_Count,self.userid,self.reportid,self.loglines,self.test_name,self.files,self.File_path,self.mode,self.appName,self.time,self.date_time,self.logtype_val)

def decideFlow(Thread_name,IMPCount,userid,reportid,loglines,rep_name,files,File_path,mode,appName,time,date_time,logtype_val):
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    if Thread_name == "SP" and IMPCount>0:
        if mode == "OFL":
            query = 'select IMP_ID,PAT_LIST,OUTPUT,LOGIC from report_imperatives_patterns where USER_ID="'+userid+'" and REP_ID ="'+reportid+'" and LOG_TYPE ="'+logtype_val+'" and LOGIC != "None";'
        elif mode == "ONL":
            query = 'select IMP_ID,PAT_LIST,OUTPUT,LOGIC from online_imperative_info where App_Name="'+appName+'" and LOG_TYPE="'+logtype_val+'";'
        sp_arr = cursor.execute(query).fetchall()
        for sp in sp_arr:
            query1 = 'select IMP_DESCRIPTION from imperative_info where IMP_ID="'+sp[0]+'";'
            Imp_name = cursor.execute(query1).fetchone()[0].lower()
            if len(sp[1].split(",")) == 1:
                print(sp[0])
                OC_Count = len(sp[2].split(","))
                if OC_Count == 1:
                    print("SPSO")
                    if sp[0] == "IMP001":
                        generateCSV_IMP001(sp[1],userid,reportid,sp[2],rep_name,loglines,"None",mode,appName,time,date_time,Imp_name)#Function call for IMP001
                    elif sp[0] == "IMP003":
                        generateCSV_IMP003(sp[1],userid,reportid,sp[2],rep_name,loglines,"None",mode,appName,time,date_time,Imp_name,logtype_val)#Function call for IMP001
                else:
                    print("SPMO")
    elif Thread_name == "MP" and IMPCount>0:
        if mode == "OFL":
            query = 'select IMP_ID,PAT_LIST,OUTPUT,LOGIC from report_imperatives_patterns where USER_ID="'+userid+'" and REP_ID ="'+reportid+'" and LOG_TYPE ="'+logtype_val+'" and LOGIC != "None";'
        elif mode == "ONL":
            query = 'select IMP_ID,PAT_LIST,OUTPUT,LOGIC from online_imperative_info where App_Name="'+appName+'"and LOG_TYPE="'+logtype_val+'";'
        mp_arr = cursor.execute(query).fetchall()
        for mp in mp_arr:
            query1 = 'select IMP_DESCRIPTION from imperative_info where IMP_ID="'+mp[0]+'";'
            Imp_name = cursor.execute(query1).fetchone()[0].lower()
            if len(mp[1].split(",")) > 1:
                print(mp[0])
                OC_Count = len(mp[2].split(","))
                Logic = mp[3]
                if OC_Count == 1:
                    print("MPSO")
                    if Logic == "AND" and mp[0] == "IMP001":
                        generateCSV_IMP001(mp[1],userid,reportid,mp[2],rep_name,loglines,Logic,mode,appName,time,date_time,Imp_name)
                        print("MPSOA")
                    elif Logic == "OR": 
                        print("MPSOO")
                    elif Logic == "THEN" and mp[0] == "IMP001":
                        print("MPSOT")
                        generateCSV_IMP001(mp[1],userid,reportid,mp[2],rep_name,loglines,Logic,mode,appName,time,date_time,Imp_name)
                    elif Logic == "Customization"  and mp[0] == "IMP003":
                        print(Imp_name)
                        generateCSV_IMP003(mp[1],userid,reportid,mp[2],rep_name,loglines,Logic,mode,appName,time,date_time,Imp_name,logtype_val)
                    elif Logic == "Customization"  and mp[0] == "IMP005":
                        generateCSV_IMP005(mp[1],userid,reportid,mp[2],rep_name,loglines,Logic,mode,appName,time,date_time,Imp_name,logtype_val)
                    elif Logic == "Customization"  and mp[0] == "IMP008":
                        generateCSV_IMP008(mp[1],userid,reportid,mp[2],rep_name,loglines,Logic,mode,appName,time,date_time,Imp_name)
                else:
                    print("MPMO")
                    if Logic == "AND": 
                        print("MPMOA")
                    elif Logic == "OR": 
                        print("MPMOO")
                    elif Logic == "Customization"  and mp[0] == "IMP002":
                        generateCSV_IMP002(mp[1],userid,reportid,mp[2],rep_name,loglines,Logic,mode,appName,time,date_time,Imp_name)
                    elif Logic == "Customization"  and mp[0] == "IMP004":
                        generateCSV_IMP004(mp[1],userid,reportid,mp[2],rep_name,Logic,File_path,mode,appName,time,date_time,Imp_name)
                    elif Logic == "Customization"  and mp[0] == "IMP006":
                        generateCSV_IMP006(mp[1],userid,reportid,mp[2],rep_name,loglines,Logic,mode,appName,time,date_time,Imp_name)
            
        

#To get the IMP_count for SP and MP
def getIMPCount(reportid,userid,loglines,test_name,files,File_path,mode,appName,time,date_time,logtype_val):
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    if mode == "OFL":
        SP_query = 'select count(IMP_ID) from report_imperatives_patterns where USER_ID="'+userid+'" and REP_ID ="'+reportid+'" and LOG_TYPE ="'+logtype_val+'" and LOGIC = "None";'
        MP_query = 'select count(IMP_ID) from report_imperatives_patterns where USER_ID="'+userid+'" and REP_ID ="'+reportid+'" and LOG_TYPE ="'+logtype_val+'" and LOGIC != "None";'
    elif mode == "ONL":
        SP_query = 'select count(IMP_ID) from online_imperative_info where App_Name="'+appName+'" and LOG_TYPE="'+logtype_val+'";'
        MP_query = 'select count(IMP_ID) from online_imperative_info where App_Name="'+appName+'" and LOG_TYPE="'+logtype_val+'";'
    SPIMP_Count = cursor.execute(SP_query).fetchone()[0]
    MPIMP_Count = cursor.execute(MP_query).fetchone()[0]
    SP_thread = myThread(1, "SP", SPIMP_Count,reportid,userid,loglines,test_name,files,File_path,mode,appName,time,date_time,logtype_val)
    MP_thread = myThread(1, "MP", MPIMP_Count,reportid,userid,loglines,test_name,files,File_path,mode,appName,time,date_time,logtype_val)
    SP_thread.start()
    SP_thread.join()
    MP_thread.start()
    MP_thread.join()
    


if __name__ == "__main__":
    print("Content-type: text/html \n");
    userid = "1"
    reportid = "33"
    getIMPCount(reportid,userid)
