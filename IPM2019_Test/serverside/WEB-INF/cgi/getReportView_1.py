import os,openpyxl,re,pyodbc,shutil,math
import cgi, cgitb
from pprint import pprint
from collections import Counter
import configparser
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import datetime
from itertools import groupby
from operator import itemgetter
import pandas as pd

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM\\Config\\configfile.config")
##STAD_INDEX_NAME = parser.get('Upload','STAD_INDEX_NAME')
STAD_INDEX_NAME = "sap_stad"
TCODE_WS_PATH = parser.get('Upload','tcodetoworkstream')

def process(test_name,prjid,userid):
    #Log_Name = str(userid) + "_"+str(prjid)+"_"+test_name
    Log_Name = str(userid) +"_"+test_name
    es = Elasticsearch('localhost', port=9200)
    dir_path = "../../../WEB-INF/classes/static/html/Reports/"+Log_Name
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    csvtcode_data = []
    groupby_tcode_dict = {}
    tcode_users = {}
    tcode_workstream = pd.read_csv(TCODE_WS_PATH)
    #fetch distinct tcode value from stad 
    res=es.search(index=STAD_INDEX_NAME,body={ "size": 0,"query": {"bool": {"must": [{"match":{"LOG_NAME.keyword":Log_Name}}]}},"aggs": {"uniqtcode" : {"terms": {"field" : "TRANSACTION_OR_JOBNAME.keyword", "exclude" : ["SAPMHTTP.*","RFC"] ,"size": 10000},"aggs": {"avg_res": {"avg": {"field": "RESPONSE_TIME"}},"max_res": {"max": {"field": "RESPONSE_TIME"}},"tran_type":{"terms":{"field":"TYPE.keyword","size":10000}},"user_count": {"terms": {"field": "USER.keyword", "size": 10000},"aggs": {"max_user_res": {"max": {"field": "RESPONSE_TIME"}},"fail_count": {"filter": {"script": {"script": "doc['RESPONSE_TIME'].value > 2000"}}}}}}}}},request_timeout=60)
##    print(res)
    agg_val=res['aggregations']['uniqtcode']['buckets']
    data=""
    for doc in agg_val:
        max_user_dict={}
        impacted_user_count=set()
        Failed_tran_count=0
        transaction_type='Job'

        if doc['tran_type']['buckets'][0]['key'] == 'TA':
            #print(doc['key'],tcode_workstream['Tcode'].values)
            if doc['key'] in tcode_workstream['Tcode'].values:
                transaction_type = 'Standard'
            else:
                transaction_type = 'Custom'
                
        for get_details in doc['user_count']['buckets']:
            max_user_dict[get_details['key']] = get_details['doc_count']
            if get_details['fail_count']['doc_count'] != 0:
                impacted_user_count.add(get_details['key'])
                Failed_tran_count = Failed_tran_count + get_details['fail_count']['doc_count']
        maximum_user = max(max_user_dict, key=max_user_dict.get)
        search_value = ''
        if doc['key'].startswith('<') and doc['key'].endswith('>'):
            continue
        if 'ZJANUS_BGR_' in doc['key']:
            search_value = 'AIF_ZJANUS_BGR'
        elif 'RUN_' in doc['key']:
            if '_PACK_' in doc['key']:
                search_value = 'AIF_PACK'
            else:
                search_value = 'AIF_RUN'
        elif 'USR_ATCR_' in doc['key']:
            search_value = 'USR_ATCR'
        elif 'SAPMHTTP' in doc['key']:
            if 'sap/public' in doc['key']:
                search_value = 'SAPMHTTP_PUBLIC'
            elif 'sap/bc' in doc['key']:
                search_value = 'SAPMHTTP_BC'
            else:
                search_value = 'SAPMHTTP'
        elif 'AIF' in doc['key'] and 'YSOIA_BCG_' in doc['key']:
            search_value = 'AIF_YSOIA_BCG'
        elif 'F110-2020' in doc['key']:
            search_value = 'F110-2020'
        elif 'SAP_COLLECTOR_' in doc['key']:
            search_value = 'SAP_COLLECTOR'
        elif 'RPC' in doc['key']:
            search_value = 'RPC'
        else:
            csvtcode_data.append(doc['key'] + "," + transaction_type + "," + str(len(doc['user_count']['buckets'])) + "," + str(len(impacted_user_count)) + ","+ str(doc['doc_count']) + "," + str(Failed_tran_count)+"," + str(round(doc['avg_res']['value']/1000, 2)) + "," + str(maximum_user) + "," + str(round(doc['max_res']['value']/1000, 2)))
            data = data + (doc['key'] + "," + transaction_type + "," + str(len(doc['user_count']['buckets'])) + "," + str(len(impacted_user_count)) + ","+ str(doc['doc_count']) + ","
                           + str(Failed_tran_count)+"," + str(round(doc['avg_res']['value']/1000, 2)) + "," + str(maximum_user) + ","
                           + str(round(doc['max_res']['value']/1000, 2))) + ","
        if search_value:
            if search_value not in tcode_users:
                tcode_users[search_value] = [{},set()]
            for key in max_user_dict:
                if key not in tcode_users[search_value][0]:
                    tcode_users[search_value][0][key] = max_user_dict[key]
                else:
                    tcode_users[search_value][0][key] += max_user_dict[key]
            tcode_users[search_value][1].update(impacted_user_count)
            maximum_user = max(tcode_users[search_value][0], key=tcode_users[search_value][0].get)
            if search_value not in groupby_tcode_dict:
                groupby_tcode_dict[search_value] = [0,0,0,0,0,0,'',0,0]
            groupby_tcode_dict[search_value][0] = transaction_type
            groupby_tcode_dict[search_value][1] = len(tcode_users[search_value][0])
            groupby_tcode_dict[search_value][2] = len(tcode_users[search_value][1])
            groupby_tcode_dict[search_value][3] += doc['doc_count']
            groupby_tcode_dict[search_value][4] += Failed_tran_count
            groupby_tcode_dict[search_value][5] += round(doc['avg_res']['value']/1000, 2)
            groupby_tcode_dict[search_value][6] = str(maximum_user)
            groupby_tcode_dict[search_value][7] += round(doc['max_res']['value']/1000, 2)
            groupby_tcode_dict[search_value][8] += 1
            # for i in csvtcode_data:
            #     spli_arr = i.split(",")
            #     if search_value in spli_arr[0]:
            #         csvtcode_data.remove(i)
            #         spli_arr[1] = str(int(spli_arr[1])+len(doc['user_count']['buckets']))
            #         spli_arr[2] = str(int(spli_arr[2])+impacted_user_count)
            #         spli_arr[3] = str(int(spli_arr[3])+doc['doc_count'])
            #         spli_arr[4] = str(int(spli_arr[4])+Failed_tran_count)
            #         spli_arr[5] = str(int(spli_arr[5])+round(doc['avg_res']['value']/1000, 2))
            #         spli_arr[6] = str(int(spli_arr[6])+maximum_user)
            #         spli_arr[7] = str(int(spli_arr[7])+round(doc['max_res']['value']/1000, 2))
            #         spli_str = ','.join(spli_arr)
            #         csvworkstream_data.append(spli_str)
            #         break
    # myfunc = lambda val,length:str(math.ceil(val/length))
    round_func = lambda val,length:str(round(val/length,2))
    for tcode in groupby_tcode_dict:
        csvtcode_data.append(tcode + "," + str(groupby_tcode_dict[tcode][0]) + "," +\
                             str(groupby_tcode_dict[tcode][1]) + "," +\
                             str(groupby_tcode_dict[tcode][2]) + "," +\
                             str(groupby_tcode_dict[tcode][3]) + "," +\
                             str(groupby_tcode_dict[tcode][4]) + "," +\
                             round_func(groupby_tcode_dict[tcode][5],groupby_tcode_dict[tcode][8]) + "," +\
                             str(groupby_tcode_dict[tcode][6])+ "," +\
                             round_func(groupby_tcode_dict[tcode][7],groupby_tcode_dict[tcode][8]))
        data = data + (tcode + "," + str(groupby_tcode_dict[tcode][0]) + "," +\
                             str(groupby_tcode_dict[tcode][1]) + "," +\
                             str(groupby_tcode_dict[tcode][2]) + "," +\
                             str(groupby_tcode_dict[tcode][3]) + "," +\
                             str(groupby_tcode_dict[tcode][4]) + "," +\
                             round_func(groupby_tcode_dict[tcode][5],groupby_tcode_dict[tcode][8]) + "," +\
                             str(groupby_tcode_dict[tcode][6])+ "," +\
                             round_func(groupby_tcode_dict[tcode][7],groupby_tcode_dict[tcode][8])) + ","
            
    with open(dir_path + "/" + Log_Name + '_reports.csv','w') as file:
        line = "Tcode,Type,Total User Count,Impacted User Count,Total Transaction Count,Failed Transaction Count,Average Response Time (Seconds),Maximum User,Maximum Response Time (Seconds)"
        file.write(line + '\n')
        for i in csvtcode_data:
            file.write(i+"\n")  
    return data

if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    test_name = form.getvalue('Txt_testname').strip()
    prjid = form.getvalue('prjid').strip()
    userid = form.getvalue('userid').strip()
    # Manual Execution
##    test_name = "PH101_STAD_2108"
##    prjid = "861"
##    userid = "42"
##-end of manual Execution##
    test_name = test_name.lower()
    data = process(test_name,prjid,userid)
    print(data)
