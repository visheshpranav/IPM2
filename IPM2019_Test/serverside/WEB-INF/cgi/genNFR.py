import pandas as pd
import sys
import os
import requests,json
from pandas import DataFrame
import glob,shutil
import time, re, pyodbc
from tkinter import *
import tkinter.messagebox
import zipfile
import cgi
from itertools import islice
output_string = ""
value = ""
imp_name=[]
import configparser


parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
IKEA_DATA_PATH = parser.get('Upload','ikea')
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
#logstash_path = parser.get('Upload','LOGSTASH_SAP_PATH')

COLUMN_LIST=["Started", "Server", "Step", "Typ", "Transaction or jobname", "User", "Response time (ms)", "Time in WPs (ms)", "Wait time (ms)",
             "CPU time (ms)", "DB req. time (ms)", "VMC elapsed time (ms)", "Memory used (kB)", "Transfered kBytes", "Processing time (ms)", "Load time (ms)",
             "Generating time  (ms)", "Roll (i+w) time (ms)", "Enqueue time (ms)", "GUI time (ms)"]
FINAL_COLUMN_LIST = ["Started", "Server", "Step", "Typ", "Transaction or jobname", "User", "Response time (ms)", "Time in WPs (ms)", "Wait time (ms)",
             "CPU time (ms)", "DB req.time (ms)", "VMC elapsed time (ms)", "Memory used (kB)", "Transfered kBytes", "Processing time (ms)", "Load time(ms)",
             "Generating time (ms)", "Roll (i+w) time (ms)", "Enqueue time (ms)", "GUI time (ms)"]
body_json = {
    "logtype": "SMON",
    "client_id": "101",
    "dc_id": "201",
    "app_id": "301",
    "user_id": "user01",
    "rep_name": "rep_01",
    "build_id": "1002",
    "rep_id": "3003",
    "start_date": "",
    "end_date": "",
    "file_path": "C:\\Users\\Public\\Documents\\12_Oct_2020.XLSX"}
def clean_txt_excel(file, outpath_file):
     # Using readlines() 
    file1 = open(file, 'r') 
    Lines = file1.readlines() 

    start_flag=False
    final_list = [] 
    data_list=[]
    header=False
    header_list = []
    for line in Lines:
        word_list=[]
        strip_word_list=[]
        if header:
            header_line2 = list(re.split(r'\t', line))
            header_line1 = header_list[-1]
            header_line1.reverse()
            header_line2.reverse()
            header_line2[0]=header_line2[0].strip('\n')
            # print(header_line2)
            for i in range(0, len(header_line2)):
                final_list.append(header_line1[i].strip() +' '+ header_line2[i].strip())
            final_list = list(filter(lambda a: a != ' ', final_list))
            final_list = [val.strip() for val in final_list]
            final_list.reverse()
            header=False
            if(all(x in final_list for x in COLUMN_LIST)):
                print(file.split('\\')[-1]+': all mandatory headers present')
                print("Number of columns: ",len(final_list))
            else:
                missing_fields = list(set(COLUMN_LIST)-set(final_list))
                print('Processing Error',"In "+ file.split('\\')[-1]+ ' - following mandatory Field(s) missing:\n\n'+',\n'.join(missing_fields))
                exit()
                # root=Tk()
                # tkinter.messagebox.showinfo('Processing Error',"In "+ file.split('\\')[-1]+ ' - following mandatory Field(s) missing:\n\n'+',\n'.join(missing_fields))
                # sys.exit()
                # Button(root, text="Quit", command=root.destroy).pack()
                # root.mainloop()
            
            # header_list.append()
        if 'Started' in line:
            header_line1 = list(re.split(r'\t', line))
            header_line1[-1]=header_line1[-1].strip('\n')
            # header_line1 = list(filter(lambda a: a != '', header_line1))
            # header_line1.reverse()
            # header_line1[0]=header_line1[0].strip('\n')
            # header_line1.reverse()
            # print(header_line1)
            header_list.append(header_line1)
            # print(header_list)
            header=True
        try:
            x=list(list(re.split(r'\t+', line))[1].split(":")[0])[0]
            try:
                int(x)
                start_flag=True
            except ValueError:
                start_flag=False
        except:
            start_flag=False
            
        if start_flag:
            word_list=list(re.split(r'\t+', line))
            word_list.pop(0)

            for val in word_list:
                val = val.strip()
##                try:
##                    float(val)
##                    val=round(float(val),2)
##                except ValueError:
##                    val = val
                strip_word_list.append(val)
            data_list.append(strip_word_list)

    #print(data_list)
    df=pd.DataFrame(data_list, columns=final_list)
    if len(df.index):
        df.to_csv(outpath_file, index=False)

#insert upload details into log_info table
def insert_uploadlogentry(fileitem, username, userid, test_name):
    try:
        db1 = pyodbc.connect("DSN="+DSN_NAMEE)
        cursor = db1.cursor()
        query = """INSERT INTO REPORT_INFO (`USER_ID`, `STATUS`, `REP_NAME`, `DATE`)
                    VALUES ('%s','1','%s',now());"""
        
        cursor.execute(query %(userid,test_name))
        db1.commit()

        report_query = 'SELECT rep_id FROM report_info where user_id='+userid+' and rep_name ="'+test_name+'";'
        rep_id= cursor.execute(report_query).fetchone()[0]
        
        fn = os.path.basename(fileitem.filename)
        dir_path = "../../../WEB-INF/classes/static/html/Reports/"+userid+"_"+str(rep_id)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        json_path = IKEA_DATA_PATH + "Cache\\" + str(userid) + "\\" + test_name
        body_json['file_path'] = json_path + "\\" + fn
        res = requests.post('http://localhost:8080/SAP/Upload',data = body_json)
        if res.status_code == 200:
            res1 = requests.get('http://localhost:8080/SAP/RAE',data = body_json)
            file_name = fn.lower().split(".xlsx")[0]+".json"
            fp = open(json_path+ "\\"+file_name,'w')
            fp.write(res1.text)
            fp.close()
        shutil.move(json_path+ "\\"+file_name, dir_path+"/IMP030.json")
    except Exception as e:
        print(e)


# check given testname alerady exists in database
def is_test_existing(userid, test_name):
    query = 'select REP_NAME FROM REPORT_INFO WHERE REP_NAME = "'+test_name+'" and user_id="'+userid+'";'
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    res = cursor.execute(query).fetchall()
    if len(res) == 0:
        return True
    return False 


def merge_csv_new(excel_path,resp,outpath):
    # extension = 'csv'
    all_filenames = [i for i in glob.glob(excel_path)]

    #combine all files in the list
    merge_df = pd.concat([pd.read_csv(f, thousands='.',decimal=',', header=0, low_memory=False) for f in all_filenames],sort = True)
    #export to csv
    # print(merge_df.columns)
    merge_df_tcode = pd.DataFrame(merge_df["Transaction or jobname"].drop_duplicates().dropna())
    merge_df_tcode = merge_df_tcode.rename(columns={"Transaction or jobname": "TCODE"})    
    merge_df_tcode['Target Response Time (Seconds)'] = resp
    merge_df_tcode.to_csv(outpath+"NFR\\NFR.csv",index=False)
    merge_df = merge_df[COLUMN_LIST]
    merge_df.to_csv(outpath+"STAD\\merged_output.csv",index=False, header = FINAL_COLUMN_LIST)
    
def run_upload(fileitem,userid,test_name):
    fn = os.path.basename(fileitem.filename)
##    fn = fileitem
    folder_name = '.'.join(fn.split(".")[:-1])
    if not os.path.exists(IKEA_DATA_PATH + "Cache\\" + userid):
        os.mkdir(IKEA_DATA_PATH + "Cache\\" + userid)
    dir_path = IKEA_DATA_PATH + "Cache\\" + userid
    # if not os.path.exists(dir_path):
    #     os.mkdir(dir_path)
    # dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name + "\\" + folder_name
    # if os.path.exists(dir_path):
    #     shutil.rmtree(dir_path)
    # os.mkdir(dir_path)
    full_dir_path = dir_path + "\\"

    try:
        if fn.endswith(".zip"):
            zip_handler = zipfile.ZipFile(fileitem.file, "r")
            zip_handler.extractall(full_dir_path)
            zip_handler.close()
        else:
            if fn.endswith((".log",".txt",".xlsx",".csv",".001")):
                g = open(full_dir_path + fn, 'wb').write(fileitem.file.read())
                print(full_dir_path + test_name)
                return full_dir_path
            else:
                return "FUP 0,Please Upload The Valid File"
                exit(1)
        return full_dir_path
    except Exception as e:
        return 'FUP 0,Unexpected error:{exception}'.format(exception=e)
        exit(1)

def store_json(fileitem,userid,test_name):
    try:
        fn = os.path.basename(fileitem.filename)
        if fn:
            if not os.path.exists(IKEA_DATA_PATH + "Cache\\" + userid):
                os.mkdir(IKEA_DATA_PATH + "Cache\\" + userid)
            dir_path = IKEA_DATA_PATH + "Cache\\" + userid
            if not os.path.exists(dir_path + "\\" + test_name):
                os.mkdir(dir_path+ "\\" + test_name)
            dir_path = IKEA_DATA_PATH + "Cache\\" + userid + "\\" + test_name
            
            if fn.endswith((".XLSX",".xlsx")):
                g = open(dir_path + "\\"+ fn, 'wb').write(fileitem.file.read())
    except Exeption as e:
        print("Json File - " + str(e))

if __name__=='__main__':
    start = time.process_time()
    form = cgi.FieldStorage()
    fileitems = form['Dlg_filename']
    json_fileitems = form['Dlg_jsonfilename']
    resp = form.getvalue("NFR")    
    username = form.getvalue('username')
    userid = form.getvalue('userid').strip()
    test_name = form.getvalue('Txt_reportname')
##    userid = "42"
##    test_name = "QH1_SO_1310"
##    resp = "2"
##    file_path = IKEA_DATA_PATH + "Cache\\" + userid + '\\'
##    print ("Content-type: text/html \n")
##    if True:
    if is_test_existing(userid, test_name):
        if type(fileitems) == list:
            for fileitem in fileitems:
                file_path = run_upload(fileitem,userid,test_name)
        else:
            file_path = run_upload(fileitems,userid,test_name)
        if json_fileitems.filename:
            print(os.path.basename(json_fileitems.filename))
            store_json(json_fileitems,userid,test_name)
        insert_uploadlogentry(json_fileitems,username, userid, test_name) 
        # path = "C:\\Muthu\\Working\\Clients\\IPM_Projects\\Ikea\\July\\QH101_2407_0000_2400\\"
        txt_path = file_path+"*.txt"
        files = glob.glob(txt_path)

        print("Number of files in the input folder:",str(len(files)))
        outpath = file_path+"\\modified\\"
        start = time.process_time()
        if os.path.exists(outpath):
            shutil.rmtree(outpath)
        
        os.mkdir(outpath)
        for file in files:
            #print(file)
            file_name = file.split('\\')[-1]
            excel_file_name = file_name.split(".txt")[0]+".csv"
            clean_txt_excel(file, outpath+excel_file_name)
            os.remove(file)
        
        print("Clean Code Time Taken (seconds) :: ", time.process_time() - start)
        excel_path = file_path+"\\modified\\*.csv"
        dir_path = file_path + test_name
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        if not os.path.exists(dir_path+'\\STAD'):
            os.mkdir(dir_path+'\\STAD')
        if not os.path.exists(dir_path+'\\NFR'):
            os.mkdir(dir_path+'\\NFR')
        final_outpath = dir_path + '\\'
        # merged_file_path = file_path+"\\Output\\"
        # if not os.path.exists(merged_file_path):
        #     os.mkdir(merged_file_path)
        #resp=input("Kindly provide the Response Time:" )
        start = time.process_time()
        merge_csv_new(excel_path,resp,final_outpath)
        if os.path.exists(outpath):
            shutil.rmtree(outpath)
        ##    Log_Name = userid+"_"+logName
        ##    filename_stad = Log_Name+"_stad.csv"
        ##    filename_nfr = Log_Name+"_nfr.csv"
        ##    shutil.move(filename_stad, logstash_path+filename_stad)
        ##    shutil.move(filename_nfr, logstash_path+filename_nfr)
        print("New Merged CSV Time Taken (seconds) :: ", time.process_time() - start)
    else:
        print("TAP 0, Report name already exists")
    
