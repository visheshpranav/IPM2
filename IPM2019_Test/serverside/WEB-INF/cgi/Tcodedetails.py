from elasticsearch import Elasticsearch
import pandas as pd
import cgi, cgitb
import os
import configparser, re
##es = Elasticsearch('10.83.80.124', port=9200)


parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
STAD_INDEX_NAME = parser.get('Upload','STAD_INDEX_NAME')


##if not os.path.exists(dir_path):
##    os.mkdir(dir_path)

es = Elasticsearch('localhost', port=9200) 

def Tcodedetail(Tcode,indexx,Log_Name):
    folder_Name = str(userid) + "_"+test_name
    dir_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_Name   
    search_value = ''
    if 'AIF_ZJANUS_BGR' in Tcode:
        search_value = '*ZJANUS_BGR*'
    if 'AIF_YSOIA_BCG' in Tcode:
        search_value = '*YSOIA_BCG*'
    elif 'AIF_RUN' in Tcode:
        search_value = '*RUN_*'
    elif 'AIF_PACK' in Tcode:
        search_value = '*RUN_*_PACK_*'
    elif 'USR_ATCR' in Tcode:
        search_value = '*USR_ATCR*'
    elif 'SAPMHTTP_PUBLIC' in Tcode:
        search_value = '*public*'
    elif 'SAPMHTTP_BC' in Tcode:
        search_value = '*SAPMHTTP*sap\/bc*'
    elif 'F110-2020' in Tcode:
        search_value = '*F110-2020*'
    elif 'SAP_COLLECTOR' in Tcode:
        search_value = '*SAP_COLLECTOR_*'
    elif 'RPC' in Tcode:
        search_value = '*RPC*'
    elif 'SAPMHTTP_MD_BUSINESSPARTNER_SRV' in Tcode:
        search_value = '*sap/MD_BUSINESSP*'
    elif 'SAPMHTTP_ESH_SEARCH_SRV' in Tcode:
        search_value = '*sap/ESH_SEARCH_S*'
    elif 'SAPMHTTP_CV_ATTACHMENT_SRV' in Tcode:
        search_value = '*sap/CV_ATTACHMEN*'
    elif 'ARFC' in Tcode:
        search_value = '*ARFC*'
    elif 'SAPMHTTP' in Tcode:
        search_value = '*SAPMHTTP*'
    else:
        res = es.search(index=indexx, body={"size":"10000","_source":["STARTED1","TRANSACTION_OR_JOBNAME","USER","RESPONSE_TIME","CPU_TIME","WAIT_TIME","DB_REQ_TIME","LOAD_TIME","TIME_IN_WPS","GUI_TIME","PROCESSING_TIME","ENQUEUE_TIME",
                                                       "ROLL_TIME"],"query":{"bool":{"must":[{"match":{"LOG_NAME.keyword":Log_Name}},{"match":{"TRANSACTION_OR_JOBNAME.keyword":Tcode}}]}}})
##    print(search_value)
    if search_value:
        res = es.search(index=indexx, body={"size":"10000","_source":["STARTED1","TRANSACTION_OR_JOBNAME","USER","RESPONSE_TIME","CPU_TIME","WAIT_TIME","DB_REQ_TIME","LOAD_TIME","TIME_IN_WPS","GUI_TIME","PROCESSING_TIME","ENQUEUE_TIME",
                                                       "ROLL_TIME"],"query":{"bool":{"must":[{"match":{"LOG_NAME.keyword":Log_Name}},{"wildcard":{"TRANSACTION_OR_JOBNAME.keyword":search_value}}]}}})
   
    source_list = []
    for source in res['hits']['hits']:
       source_list.append(source['_source'])
      
    print(len(source_list))
    df = pd.DataFrame(source_list)

    column_names = ["STARTED1","USER","RESPONSE_TIME","TIME_IN_WPS","CPU_TIME","WAIT_TIME","DB_REQ_TIME","LOAD_TIME","GUI_TIME","PROCESSING_TIME","ENQUEUE_TIME",
                                                 "ROLL_TIME"]

    
    df = df.reindex(columns=column_names)
    df = df.rename(columns={"STARTED1": "Starttime"})
    df['Starttime'] = [x.split('T')[1].split('.')[0] for x in df['Starttime']]
    df['LOAD_TIME'] = [round(x) for x in df['LOAD_TIME']]
    df['TIME_IN_WPS'] = [round(x) for x in df['TIME_IN_WPS']]
    df['GUI_TIME'] = [round(x) for x in df['GUI_TIME']]
    df['PROCESSING_TIME'] = [round(x) for x in df['PROCESSING_TIME']]
    df['CPU_TIME'] = [round(x) for x in df['CPU_TIME']]
    df['ENQUEUE_TIME'] = [round(x) for x in df['ENQUEUE_TIME']]
    df['DB_REQ_TIME'] = [round(x) for x in df['DB_REQ_TIME']]
    df['WAIT_TIME'] = [round(x) for x in df['WAIT_TIME']]
    df['RESPONSE_TIME'] = [round(x) for x in df['RESPONSE_TIME']]
    df['ROLL_TIME'] = [round(x) for x in df['ROLL_TIME']]
    df = df.rename(columns={"LOAD_TIME": "LOAD_TIME(ms)","TIME_IN_WPS": "TIME_IN_WPS(ms)","GUI_TIME": "GUI_TIME(ms)","PROCESSING_TIME": "PROCESSING_TIME(ms)",
                            "CPU_TIME": "CPU_TIME(ms)","ENQUEUE_TIME": "ENQUEUE_TIME(ms)","DB_REQ_TIME": "DB_REQ_TIME(ms)",
                            "WAIT_TIME": "WAIT_TIME(ms)","RESPONSE_TIME": "RESPONSE_TIME(ms)","ROLL_TIME": "ROLL_TIME(ms)"})
    
##    print(df.shape)
    Tcode = re.sub(r"[()\#/<>{}~|!?,]", "", Tcode)
    Tcode = Tcode.replace(" ", "")
    df.to_csv(dir_path+"/"+Log_Name+"_" +Tcode+ ".csv",index= False)
    
    

##    df = df.columns("logdatetime","TRANSACTION_OR_JOBNAME","LOAD_TIME","TIME_IN_WPS","GUI_TIME","PROCESSING_TIME","CPU_TIME","ENQUEUE_TIME","USER","DB_REQ_TIME",
##                                                   "WAIT_TIME","RESPONSE_TIME","ROLL_TIME")
    print("Completed")
    
   
if __name__ == "__main__":
    print("Content-type: text/html \n");    
    form = cgi.FieldStorage()
    test_name = form.getvalue('test_name').strip().lower()
    userid = form.getvalue('user_id').strip()
    Log_Name = str(userid) + "_"+test_name    
    Tcode = form.getvalue('Tcode').strip()
    prjid = form.getvalue('prjid').strip()
    print(test_name,userid,Log_Name,Tcode,prjid)
    
    
##    Tcode = "SAPMHTTP_CV_ATTACHMENT_SRV"
##    userid = "42"
##    test_name = "pf101_stad_2108"
##    Log_Name = str(userid) + "_"+test_name
    
    Tcodedetail(Tcode,STAD_INDEX_NAME,Log_Name)
