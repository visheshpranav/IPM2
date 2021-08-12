import cgi, cgitb, glob
import os,re,shutil,openpyxl
import configparser
import pyodbc,datetime
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import os.path
import pandas as pd
import csv

parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
logstash_path = parser.get('Upload','LOGSTASH_SAP_PATH')
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')

def process(Stad_dir,NFR_dir,Server_dir,userid,logName,file_format,prjid):
    indx_date = ""
    data = []
    current_row = 0
    sheet_num = 0
    input_total = 0
    output_total = 0
    Log_Name = userid+"_"+logName
    es = Elasticsearch('localhost', port=9200)

    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    
    #insert STAD Data
    filename_stad = Log_Name+"_stad.csv"
    stad_ext = os.path.splitext(Stad_dir)[1][1:]
##    print(stad_ext)
    stad_flr = os.path.dirname(Stad_dir)
    stadfile = open(filename_stad,"w")
    stadfile.write("LOG_NAME,STARTED,SERVER,TYPE,TRANSACTION_OR_JOBNAME,USER,RESPONSE_TIME,TIME_IN_WPS,WAIT_TIME,CPU_TIME,DB_REQ_TIME,PROCESSING_TIME,LOAD_TIME,GENERATING_TIME,ROLL_TIME,ENQUEUE_TIME,GUI_TIME\n")

    #NFR
    filename_nfr = Log_Name+"_nfr.csv"
    nfrfile = open(filename_nfr,"w")
    nfrfile.write("LOG_NAME,TCODE,TARGET_RES_TIME\n")
    data_stad=[]
    data_nfr=[]

    
    if stad_ext == "zip":
        for stad_fl in os.listdir(stad_flr):
            print("ZIP_XLS")
            if stad_fl.split(".")[-1]=="xls":
                wb = openpyxl.load_workbook(stad_flr+"\\"+stad_fl)
                ws = wb.worksheets[sheet_num]
                data = list(iter_rows(ws))
                insert_stad(data,Log_Name,stadfile,file_format,"stad")
            elif stad_fl.split(".")[-1]=="csv":
                print("ZIP_CSV")
                print(stad_flr+"\\"+stad_fl)
                df=pd.read_csv(stad_flr+"\\"+stad_fl)
                data_nfr=[list(df.columns)] 
                for index, row in df.iterrows():
                    data_nfr.append(list(row))
                insert_stad(data_nfr,Log_Name,stadfile,file_format,"stad")
    elif stad_ext == "xlsx":
        print("XLSX")
        wb = openpyxl.load_workbook(Stad_dir)
        ws = wb.worksheets[sheet_num]
        data_stad = list(iter_rows(ws))

        #NFR
        wb = openpyxl.load_workbook(NFR_dir)
        ws = wb.worksheets[sheet_num]
        data_nfr = list(iter_rows(ws))
    elif stad_ext == "csv":
        print("CSV")
        df=pd.read_csv(Stad_dir)
        data_stad=[list(df.columns)] 
        for index, row in df.iterrows():
            data_stad.append(list(row))
        
        
        df=pd.read_csv(NFR_dir)
        data_nfr=[list(df.columns)] 
        for index, row in df.iterrows():
            data_nfr.append(list(row))

    insert_stad(data_stad,Log_Name,stadfile,file_format,"stad")
    insert_nfr(data_nfr,Log_Name,nfrfile,"nfr")
    nfrfile.close()
    stadfile.close()
    shutil.move(filename_stad, logstash_path+filename_stad)
    shutil.move(filename_nfr, logstash_path+filename_nfr)

##    #insert NFR Data
##    filename = Log_Name+"_nfr.csv"
##    print(filename)
##    nfrfile = open(filename,"w")
##    nfrfile.write("LOG_NAME,TCODE,TARGET_RES_TIME\n")
####    wb = openpyxl.load_workbook(NFR_dir)
####    ws = wb.worksheets[sheet_num]
####    data = list(iter_rows(ws))
####    insert_nfr(data,Log_Name,nfrfile,"nfr")
####    nfrfile.close()
####    shutil.move(filename, logstash_path+filename)
##
##    data=pd.read_csv(NFR_dir)
##    print("DATA2", data)
####    insert_nfr(data,Log_Name,nfrfile,"nfr")
##    nfrfile.close()
##    #shutil.move(filename, logstash_path+filename)

    

    #insert servermetrics Data
    '''if Server_dir != "":
        filename = Log_Name+"_servermetrics.csv"
        servermetricsfile = open(filename,"w")
        servermetricsfile.write("LOG_NAME,TIME,SERVER,CPU_UTIL,FREE_MEM\n")
        wb = openpyxl.load_workbook(Server_dir)
        ws = wb.worksheets[sheet_num]
        data = list(iter_rows(ws))
        insert_server(data,Log_Name,servermetricsfile,"servermetrics")
        servermetricsfile.close()
        shutil.move(filename, logstash_path+filename)
    else:
        break'''

    
def insert_stad(data,Log_Name,stadfile,file_format,tab_name):
    indx_date = ""
    T_data = []
    global startdateval
    j = 0
    for i in data:
##        print("@@@@@@@@@@",i)
        if None in i:
            i = ['' if v is None else v for v in i]
        #i = [str(s) for s in i ]
##        print("@@@@@@@@@@",i)
        if "Analysed time:" in i:
            print("col Analysed time")
            #date_obj = datetime.datetime.strptime(date_string, date_format)
            for date_field in i:
                match = re.match(r'\d\d\d\d\-\d\d-\d\d *',date_field)
                match1 = re.match(r'\d\d\.\d\d.\d\d\d\d *',date_field)
                if match or match1:
                    startdatearr = date_field.split(" ")
                    startdateval = startdatearr[0]
                    if match1:
                        startdateval = datetime.strptime(startdateval, "%d.%m.%Y").strftime("%Y-%m-%d")
                    #print("val " + str(startdateval))
                    break
        if "Response time (ms)" in i:#Get the index from list i
            print("*********col Response time**************")
            indx_date = i.index("Started")
            print("rs - " + str(indx_date))
            indx_Tcode = i.index("Transaction or jobname")
            print("rs - " + str(indx_Tcode))
            indx_response = i.index("Response time (ms)")
            indx_Wait = i.index("Wait time (ms)")
            indx_CPU = i.index("CPU time (ms)")
            indx_DB = i.index("DB req.time (ms)")
            indx_processing = i.index("Processing time (ms)")
            indx_Load = i.index("Load time(ms)")
            indx_Roll = i.index("Roll (i+w) time (ms)")
            indx_Enqueue = i.index("Enqueue time (ms)")
            indx_GUI = i.index("GUI time (ms)")
            indx_user = i.index("User")
            indx_Typ = i.index("Typ")
            indx_timewps = i.index("Time in WPs (ms)")
            indx_generating = i.index("Generating time (ms)")
            indx_Server = i.index("Server")
        elif "Started" in i:
            print("***********col Starteddddd*****************")
            indx_date = i.index("Started")
            indx_Tcode = i.index("Transaction or jobname")
            indx_response = i.index("Response")
            indx_Wait = i.index("Wait time")
            indx_CPU = i.index("CPU time")
            indx_DB = i.index("DB req.")
            indx_processing = i.index("Processing")
            indx_Load = i.index("Load time")
            indx_Roll = i.index("Roll (i+w)")
            indx_Enqueue = i.index("Enqueue")
            indx_GUI = i.index("GUI time")
            indx_user = i.index("User")
            indx_Typ = i.index("Typ")
            indx_timewps = i.index("Time in")
            indx_generating = i.index("Generating")
            indx_Server = i.index("Server")

##                column_names = ['Started','Server','Step','Typ','Transaction or jobname','User','Response time (ms)',
##                    'Time in  WPs (ms)','Wait time (ms)','CPU time (ms)','DB req.time (ms)',
##                    'VMC elapsed time (ms)','Memory used (kB)','Transfered kBytes','Processing time (ms)',
##                    'Load time  (ms)','Generating time  (ms)','Roll (i+w) time (ms)','Enqueue time (ms)','GUI time  (ms)']

        if indx_date is not None and indx_date != '':
            match = re.match(r'\d\d\:\d\d:\d\d',str(i[int(indx_date)]))
            if match:
                if file_format == "German":
                    i[indx_response] = str(i[indx_response]).replace('.','')
                    i[indx_response] = str(i[indx_response]).replace(',','.')
                    i[indx_response] = float(i[indx_response].strip())
                    i[indx_timewps] = str(i[indx_timewps]).replace('.','')
                    i[indx_timewps] = str(i[indx_timewps]).replace(',','.')
                    i[indx_timewps] = float(i[indx_timewps].strip())
                    i[indx_Wait] = str(i[indx_Wait]).replace('.','')
                    i[indx_Wait] = str(i[indx_Wait]).replace(',','.')
                    i[indx_Wait] = float(i[indx_Wait].strip())
                    i[indx_CPU] = str(i[indx_CPU]).replace('.','')
                    i[indx_CPU] = str(i[indx_CPU]).replace(',','.')
                    i[indx_CPU] = float(i[indx_CPU].strip())
                    i[indx_DB] = str(i[indx_DB]).replace('.','')
                    i[indx_DB] = str(i[indx_DB]).replace(',','.')
                    i[indx_DB] = float(i[indx_DB].strip())
                    i[indx_processing] = str(i[indx_processing]).replace('.','')
                    i[indx_processing] = str(i[indx_processing]).replace(',','.')
                    i[indx_processing] = float(i[indx_processing].strip())
                    i[indx_Load] = str(i[indx_Load]).replace('.','')
                    i[indx_Load] = str(i[indx_Load]).replace(',','.')
                    i[indx_Load] = float(i[indx_Load].strip())
                    i[indx_generating] = str(i[indx_generating]).replace('.','')
                    i[indx_generating] = str(i[indx_generating]).replace(',','.')
                    i[indx_generating] = float(i[indx_generating].strip())
                    i[indx_Roll] = str(i[indx_Roll]).replace('.','')
                    i[indx_Roll] = str(i[indx_Roll]).replace(',','.')
                    i[indx_Roll] = float(i[indx_Roll].strip())
                    i[indx_Enqueue] = str(i[indx_Enqueue]).replace('.','')
                    i[indx_Enqueue] = str(i[indx_Enqueue]).replace(',','.')
                    i[indx_Enqueue] = float(i[indx_Enqueue].strip())
                    i[indx_GUI] = str(i[indx_GUI]).replace('.','')
                    i[indx_GUI] = str(i[indx_GUI]).replace(',','.')
                    i[indx_GUI] = float(i[indx_GUI].strip())
                stadfile.write(str(Log_Name)+","+str(i[indx_date])+","+str(i[indx_Server])+","+str(i[indx_Typ])+","+str(i[indx_Tcode])+","+str(i[indx_user])+","+str(i[indx_response])
                                       +","+str(i[indx_timewps])+","+str(i[indx_Wait])+","+str(i[indx_CPU])+","+str(i[indx_DB])+","+str(i[indx_processing])+","+str(i[indx_Load])
                                       +","+str(i[indx_generating])+","+str(i[indx_Roll])+","+str(i[indx_Enqueue])+","+str(i[indx_GUI])+"\n")
            
def insert_nfr(data,Log_Name,nfrfile,tab_name):
    indx_date = ""
    T_data = []
    j = 0
    for i in data:
        if 'None' in i:
            i = ['' if v is None else v for v in i]
        i = [str(s) for s in i ]
        if "TCODE" in i:
            indx_Tcode = i.index("TCODE")
            indx_response = i.index("Target Response Time (Seconds)")
        else:
            Tcode_val = i[indx_Tcode].strip()
            if Tcode_val:
                nfrfile.write(str(Log_Name)+","+str(Tcode_val)+","+str(i[indx_response])+"\n")

def insert_server(data,Log_Name,servermetricsfile,tab_name):
    indx_date = ""
    server_val = "0"
    T_data = []
    j = 0
    for i in data:
        if None in i:
            i = ['' if v is None else v for v in i]
        i = [str(s) for s in i ]
        if "Time" in i:
            indx_date = i.index("Time")
            indx_cpu = i.index("CPU Idle")
            indx_freemem = i.index("Free Mem.")
        if "Server" in i:
            indx_Server = i.index("Server")
            server_val = i[indx_Server]
        if indx_date:
            match = re.match(r'\d\d\:\d\d:\d\d',i[int(indx_date)])
            if match:
                servermetricsfile.write(str(Log_Name)+","+str(i[indx_date])+","+str(server_val)+","+str(i[indx_cpu])+","+str(i[indx_freemem])+"\n")

    
def iter_rows(ws):
    for row in ws.iter_rows():
        yield [cell.value for cell in row]

# main function
if __name__ == "__main__":
       print("Content-type: text/html \n");
       form = cgi.FieldStorage()
       userid = form.getvalue('userid').strip()
       prjid = form.getvalue('prjid').strip()
       test_name = form.getvalue('Txt_testname')
       Stad_dir = parser.get('Upload','Stad_dir')+userid+"\\"+test_name+"\\STAD\\"+form.getvalue('Stad_dir')
       NFR_dir = parser.get('Upload','NFR_dir')+userid+"\\"+test_name+"\\NFR\\"+form.getvalue('NFR_dir')
       Server_dir = ""
       file_format = form.getvalue('file_format').strip()
       print(userid, prjid, test_name,Stad_dir, NFR_dir, Server_dir)
##       userid = "42"
##       prjid = "992"
##       test_name = "QH1_SO_1610"
##       file_format=""
##       Stad_dir="C:\\LAPAM2019\\DataLake\\Cache\\42\\QH1_SO_1610\\STAD\\merged_output.csv"
##       NFR_dir="C:\\LAPAM2019\\DataLake\\Cache\\42\\QH1_SO_1610\\NFR\\NFR.csv"
##       Server_dir=""

##       userid = "41"
##       prjid = "803"
##       test_name = "rep1"
##       file_format="German"
##       Stad_dir="C:\\LAPAM2019\\DataLake\\Cache\\41\\rep1\\STAD\\ST03.xlsx"
##       NFR_dir="C:\\LAPAM2019\\DataLake\\Cache\\41\\rep1\\NFR\\NFR.xlsx"
##       Server_dir=""
       logName = test_name.strip().lower()
       process(Stad_dir,NFR_dir,Server_dir,userid,logName,file_format,prjid)
##       print(startdateval)
