import os,openpyxl,re,pyodbc,shutil
import cgi, cgitb
from pprint import pprint
from collections import Counter
import configparser
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import datetime
from itertools import groupby
from operator import itemgetter

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
STAD_INDEX_NAME = parser.get('Upload','STAD_INDEX_NAME')
NFR_INDEX_NAME = parser.get('Upload','NFR_INDEX_NAME')


def update_data(csvworkstream_data, csvlayer_data, tcode_workstream, entity,
                tcode, impacted_entity_user_count, total_users,
                Failed_entity_tran_count, total_transactions):
    search_value = ''
    if 'SAPMHTTP' in tcode:
        search_value = 'SAPMHTTP'
    elif 'ZJANUS_BGR_' in tcode:
        search_value = 'AIF_ZJANUS_BGR'
    elif 'RUN_' in tcode:
        if '_PACK_' in tcode:
            search_value = 'AIF_PACK'
        else:
            search_value = 'AIF_RUN'
    elif 'SAP_COLLECTOR_' in tcode:
        search_value = 'SAP_COLLECTOR'
    elif 'RPC' in tcode:
        search_value = 'RPC'
    else:
        if tcode_workstream != "Basis/ABAP":
            csvworkstream_data.append("WorkStream,"+tcode_workstream + "," + entity + "," + tcode + "," + str(impacted_entity_user_count) + "," + str(total_users) + "," + str(Failed_entity_tran_count) + ","+ str(total_transactions))
            csvlayer_data.append("Layers,"+entity+","+tcode_workstream+","+tcode + "," + str(impacted_entity_user_count) + "," + str(total_users) + "," + str(Failed_entity_tran_count) + "," + str(total_transactions))
    if search_value:
        ws_updated = 0
        ly_updated = 0
        for i in csvworkstream_data:
            spli_arr = i.split(",")
            if search_value in spli_arr[3] and entity in spli_arr[2]:
                csvworkstream_data.remove(i)
                ws_updated = 1
                spli_arr[4] = str(int(spli_arr[4])+impacted_entity_user_count)
                spli_arr[5] = str(int(spli_arr[5])+total_users)
                spli_arr[6] = str(int(spli_arr[6])+Failed_entity_tran_count)
                spli_arr[7] = str(int(spli_arr[7])+total_transactions)
                spli_str = ','.join(spli_arr)
                csvworkstream_data.append(spli_str)
                break
        for i in csvlayer_data:
            spli_arr = i.split(",")
            if search_value in spli_arr[3] and entity in spli_arr[1]:
                csvlayer_data.remove(i)
                ly_updated = 0
                spli_arr[4] = str(int(spli_arr[4])+impacted_entity_user_count)
                spli_arr[5] = str(int(spli_arr[5])+total_users)
                spli_arr[6] = str(int(spli_arr[6])+Failed_entity_tran_count)
                spli_arr[7] = str(int(spli_arr[7])+total_transactions)
                spli_str = ','.join(spli_arr)
                csvlayer_data.append(spli_str)
                break

        if not ws_updated:
            csvworkstream_data.append("WorkStream,"+tcode_workstream + "," + entity + "," + search_value + "," + str(impacted_entity_user_count) + "," + str(total_users) + "," + str(Failed_entity_tran_count) + ","+ str(total_transactions))
        if not ly_updated:
            csvlayer_data.append("Layers,"+entity+","+tcode_workstream+","+search_value + "," + str(impacted_entity_user_count) + "," + str(total_users) + "," + str(Failed_entity_tran_count) + "," + str(total_transactions))
    return csvworkstream_data, csvlayer_data


def process(test_name,prjid,userid,res_time):
    folder_Name = str(userid) + "_"+str(prjid)+"_"+test_name
    Log_Name = str(userid) + "_"+test_name
    Index_Name = str(userid) + "_"+test_name
    es = Elasticsearch('localhost', port=9200)    
    ws_tcode_dict={}
    csvworkstream_data = []
    csvlayer_data = []
    dir_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_Name
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
##    print(STAD_INDEX_NAME+NFR_INDEX_NAME)
    #NFR_data
    data=""
    res_nfr = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["TCODE","TARGET_RES_TIME"],"query": {"match": {"LOG_NAME.keyword":Log_Name}}}, 
                index = NFR_INDEX_NAME)

               
    #get workstream value from elasticsearch
    res_ws = elasticsearch.helpers.scan(
                client = es,
		scroll = '2m',
                query = {"_source": ["Tcode","Workstream"]}, 
                index = "sap_workstream")
    workstream_lst = []
    for doc in res_ws:
        ws_tcode_dict[doc['_source']['Tcode']]= doc['_source']['Workstream']
##    print(ws_tcode_dict)
    res=es.search(index=STAD_INDEX_NAME,body={ "query":{"bool":{"must":[{"match":{"LOG_NAME.keyword":Log_Name}}]}},"aggs":{ "uniqtcode":{"terms":{"field":"TRANSACTION_OR_JOBNAME.keyword","size":10000},"aggs":{"avg_res": {"avg": {"field": "RESPONSE_TIME"}}, "user_count":{ "terms":{"field":"USER.keyword","size":10000 },"aggs":{"Wait_count":{"filter":{"script":{ "script":"(doc['RESPONSE_TIME'].value*0.1)<doc['WAIT_TIME'].value" } } }, "cpu_count":{ "filter":{ "script":{ "script":"((doc['RESPONSE_TIME'].value-doc['WAIT_TIME'].value)*0.4)<doc['CPU_TIME'].value" } } }, "db_count":{ "filter":{ "script":{ "script":"((doc['RESPONSE_TIME'].value-doc['WAIT_TIME'].value)*0.4)<doc['DB_REQ_TIME'].value" } } }, "processing_count":{ "filter":{ "script":{ "script":"(doc['CPU_TIME'].value*2)<doc['PROCESSING_TIME'].value" } } }, "load_count":{ "filter":{ "script":{ "script":"(doc['RESPONSE_TIME'].value*0.1)<doc['LOAD_TIME'].value" } } }, "roll_count":{ "filter":{ "script":{ "script":"doc['ROLL_TIME'].value>220" } } }, "enque_count":{ "filter":{ "script":{ "script":"doc['ENQUEUE_TIME'].value>5" } } }, "gui_count":{ "filter":{ "script":{ "script":"doc['GUI_TIME'].value>200" } } } } } } } }})
##
    #fetch distinct tcode value from stad
    for nfr_val in res_nfr:
        Tcode =  nfr_val['_source']['TCODE']
        response = str(int(nfr_val['_source']['TARGET_RES_TIME'])*1000)
        agg_val=res['aggregations']['uniqtcode']['buckets']
##        print(agg_val)
        for doc in agg_val:
            
            if (doc['key'] == Tcode) and (round(doc['avg_res']['value']/1000, 2) > int(res_time)):
                print(doc['key'],doc['avg_res']['value']) 
                impacted_wait_user_count=0
                Failed_wait_tran_count=0
                impacted_db_user_count=0
                Failed_db_tran_count=0
                impacted_cpu_user_count=0
                Failed_cpu_tran_count=0
                impacted_pro_user_count=0
                Failed_pro_tran_count=0
                impacted_load_user_count=0
                Failed_load_tran_count=0
                impacted_roll_user_count=0
                Failed_roll_tran_count=0
                impacted_enq_user_count=0
                Failed_enq_tran_count=0
                impacted_gui_user_count=0
                Failed_gui_tran_count=0

                for get_details in doc['user_count']['buckets']:
                    if get_details['Wait_count']['doc_count'] != 0:
                        impacted_wait_user_count = impacted_wait_user_count+1
                        Failed_wait_tran_count = Failed_wait_tran_count + get_details['Wait_count']['doc_count']                    
                    if get_details['cpu_count']['doc_count'] != 0:
                        impacted_cpu_user_count = impacted_cpu_user_count+1
                        Failed_cpu_tran_count = Failed_cpu_tran_count + get_details['cpu_count']['doc_count']                    
                    if get_details['db_count']['doc_count'] != 0:
                        impacted_db_user_count = impacted_db_user_count+1
                        Failed_db_tran_count = Failed_db_tran_count + get_details['db_count']['doc_count']                    
                    if get_details['processing_count']['doc_count'] != 0:
                        impacted_pro_user_count = impacted_pro_user_count+1
                        Failed_pro_tran_count = Failed_pro_tran_count + get_details['processing_count']['doc_count']
                    if get_details['load_count']['doc_count'] != 0:
                        impacted_load_user_count = impacted_load_user_count+1
                        Failed_load_tran_count = Failed_load_tran_count + get_details['load_count']['doc_count']
                    if get_details['roll_count']['doc_count'] != 0:
                        impacted_roll_user_count = impacted_roll_user_count+1
                        Failed_roll_tran_count = Failed_roll_tran_count + get_details['roll_count']['doc_count']
                    if get_details['enque_count']['doc_count'] != 0:
                        impacted_enq_user_count = impacted_enq_user_count+1
                        Failed_enq_tran_count = Failed_enq_tran_count + get_details['enque_count']['doc_count']
                    if get_details['gui_count']['doc_count'] != 0:
                        impacted_gui_user_count = impacted_gui_user_count+1
                        Failed_gui_tran_count = Failed_gui_tran_count + get_details['gui_count']['doc_count']
                if doc['key'] in ws_tcode_dict:
                    tcode_workstream = ws_tcode_dict[doc['key']]
                else:
                    tcode_workstream = "Custom"
                    
                if Failed_wait_tran_count != 0:
                    csvworkstream_data, csvlayer_data = update_data(csvworkstream_data, csvlayer_data,
                                                                    tcode_workstream, 'Wait time',
                                                                    doc['key'],impacted_wait_user_count,
                                                                    len(doc['user_count']['buckets']),
                                                                    Failed_wait_tran_count, doc['doc_count'])
                    # csvworkstream_data.append("WorkStream,"+tcode_workstream+",Wait time,"+doc['key'] + "," + str(impacted_wait_user_count) + "," + str(len(doc['user_count']['buckets'])) + "," + str(Failed_wait_tran_count) + ","+ str(doc['doc_count']))
                    # csvlayer_data.append("Layers,Wait time,"+tcode_workstream+","+doc['key'] + "," + str(impacted_wait_user_count) + "," + str(len(doc['user_count']['buckets'])) + "," + str(Failed_wait_tran_count) + "," + str(doc['doc_count']))
                if Failed_cpu_tran_count != 0:
                    csvworkstream_data, csvlayer_data = update_data(csvworkstream_data, csvlayer_data,
                                                                    tcode_workstream, 'CPU time',
                                                                    doc['key'],impacted_cpu_user_count,
                                                                    len(doc['user_count']['buckets']),
                                                                    Failed_cpu_tran_count, doc['doc_count'])
                    # csvworkstream_data.append("WorkStream,"+tcode_workstream+",CPU time,"+doc['key'] + "," + str(impacted_cpu_user_count) + "," + str(len(doc['user_count']['buckets'])) + "," + str(Failed_cpu_tran_count) + ","+ str(doc['doc_count']))
                    # csvlayer_data.append("Layers,CPU time,"+tcode_workstream+","+doc['key'] + "," + str(impacted_cpu_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_cpu_tran_count) + ","+ str(doc['doc_count']))
                if Failed_db_tran_count != 0:
                    csvworkstream_data, csvlayer_data = update_data(csvworkstream_data, csvlayer_data,
                                                                    tcode_workstream, 'DB req. time',
                                                                    doc['key'],impacted_db_user_count,
                                                                    len(doc['user_count']['buckets']),
                                                                    Failed_db_tran_count, doc['doc_count'])
                    # csvworkstream_data.append("WorkStream,"+tcode_workstream+",DB req. time,"+doc['key'] + "," + str(impacted_db_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_db_tran_count) + ","+ str(doc['doc_count']))
                    # csvlayer_data.append("Layers,DB req. time,"+tcode_workstream+","+doc['key'] + "," + str(impacted_db_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_db_tran_count) + ","+ str(doc['doc_count']))
                if Failed_pro_tran_count != 0:
                    csvworkstream_data, csvlayer_data = update_data(csvworkstream_data, csvlayer_data,
                                                                    tcode_workstream, 'Processing time',
                                                                    doc['key'],impacted_pro_user_count,
                                                                    len(doc['user_count']['buckets']),
                                                                    Failed_pro_tran_count, doc['doc_count'])
                    # csvworkstream_data.append("WorkStream,"+tcode_workstream+",Processing time,"+doc['key'] + "," + str(impacted_pro_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_pro_tran_count) + ","+ str(doc['doc_count']))
                    # csvlayer_data.append("Layers,Processing time,"+tcode_workstream+","+doc['key'] + "," + str(impacted_pro_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_pro_tran_count) + ","+ str(doc['doc_count']))
                if Failed_load_tran_count != 0:
                    csvworkstream_data, csvlayer_data = update_data(csvworkstream_data, csvlayer_data,
                                                                    tcode_workstream, 'Load time',
                                                                    doc['key'],impacted_load_user_count,
                                                                    len(doc['user_count']['buckets']),
                                                                    Failed_load_tran_count, doc['doc_count'])
                    # csvworkstream_data.append("WorkStream,"+tcode_workstream+",Load time,"+doc['key'] + "," + str(impacted_load_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_load_tran_count) + ","+ str(doc['doc_count']))
                    # csvlayer_data.append("Layers,Load time,"+tcode_workstream+","+doc['key'] + "," + str(impacted_load_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_load_tran_count) + ","+ str(doc['doc_count']))
                if Failed_roll_tran_count != 0:
                    csvworkstream_data, csvlayer_data = update_data(csvworkstream_data, csvlayer_data,
                                                                    tcode_workstream, 'Roll (i+w) time',
                                                                    doc['key'],impacted_roll_user_count,
                                                                    len(doc['user_count']['buckets']),
                                                                    Failed_roll_tran_count, doc['doc_count'])
                    # csvworkstream_data.append("WorkStream,"+tcode_workstream+",Roll (i+w) time,"+doc['key'] + "," + str(impacted_roll_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_roll_tran_count) + ","+ str(doc['doc_count']))
                    # csvlayer_data.append("Layers,Roll (i+w) time,"+tcode_workstream+","+doc['key'] + "," + str(impacted_roll_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_roll_tran_count) + ","+ str(doc['doc_count']))
                if Failed_enq_tran_count != 0:
                    csvworkstream_data, csvlayer_data = update_data(csvworkstream_data, csvlayer_data,
                                                                    tcode_workstream, 'Enqueue time',
                                                                    doc['key'],impacted_enq_user_count,
                                                                    len(doc['user_count']['buckets']),
                                                                    Failed_enq_tran_count, doc['doc_count'])
                    # csvworkstream_data.append("WorkStream,"+tcode_workstream+",Enqueue time,"+doc['key'] + "," + str(impacted_enq_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_enq_tran_count) + ","+ str(doc['doc_count']))
                    # csvlayer_data.append("Layers,Enqueue time,"+tcode_workstream+","+doc['key'] + "," + str(impacted_enq_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_enq_tran_count) + ","+ str(doc['doc_count']))
                if Failed_gui_tran_count != 0:
                    csvworkstream_data, csvlayer_data = update_data(csvworkstream_data, csvlayer_data,
                                                                    tcode_workstream, 'GUI time',
                                                                    doc['key'],impacted_gui_user_count,
                                                                    len(doc['user_count']['buckets']),
                                                                    Failed_gui_tran_count, doc['doc_count'])
                    # csvworkstream_data.append("WorkStream,"+tcode_workstream+",GUI time,"+doc['key'] + "," + str(impacted_gui_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_gui_tran_count) + ","+ str(doc['doc_count']))
                    # csvlayer_data.append("Layers,GUI time,"+tcode_workstream+","+doc['key'] + "," + str(impacted_gui_user_count) + "," + str(len(doc['user_count']['buckets'])) + ","+ str(Failed_gui_tran_count) + ","+ str(doc['doc_count']))
                break

    ws_RCAfileName_chart ="RCAWorkStreamChart_"+res_time+".csv"
    ws_fp_chart = open(ws_RCAfileName_chart,"w")
    ws_RCAfileName ="RCAWorkStream_"+res_time+".csv"
    ws_fp = open(ws_RCAfileName,"w")
    ws_fp_chart.write("Category,Level1,Level2,Level3,UserCount,TotalUserCount,Failures,TcodeCount\n")
    ws_fp.write("Workstream,Layer,Tcode,Impacted_UsersCount,Total_UserCount,Impacted_TcodesCount,Total_TcodeCount\n")
    for i in csvworkstream_data:
        spli_arr = i.split(",")
        ws_fp_chart.write(i+"\n")
        ws_fp.write(spli_arr[1]+","+spli_arr[2]+","+spli_arr[3]+","+spli_arr[4]+","+spli_arr[5]+","+spli_arr[6]+","+spli_arr[7]+"\n")
    ws_fp_chart.close()
    ws_fp.close()
    
    ly_RCAfileName_chart ="RCALayersChart_"+res_time+".csv"
    ly_fp_chart = open(ly_RCAfileName_chart,"w")
    ly_RCAfileName = "RCALayers_"+res_time+".csv"
    ly_fp = open(ly_RCAfileName,"w")
    ly_fp_chart.write("Category,Level1,Level2,Level3,UserCount,TotalUserCount,Failures,TcodeCount\n")
    ly_fp.write("Layer,Workstream,Tcode,Impacted_UsersCount,Total_UserCount,Impacted_TcodesCount,Total_TcodeCount\n")
    for i in csvlayer_data:
        spli_arr = i.split(",")
        ly_fp_chart.write(i+"\n")
        ly_fp.write(spli_arr[1]+","+spli_arr[2]+","+spli_arr[3]+","+spli_arr[4]+","+spli_arr[5]+","+spli_arr[6]+","+spli_arr[7]+"\n")
    ly_fp_chart.close()
    ly_fp.close()
    
    shutil.move(ws_RCAfileName_chart, dir_path+"/"+ws_RCAfileName_chart)
    shutil.move(ws_RCAfileName, dir_path+"/"+ws_RCAfileName)
    shutil.move(ly_RCAfileName_chart, dir_path+"/"+ly_RCAfileName_chart)
    shutil.move(ly_RCAfileName, dir_path+"/"+ly_RCAfileName)

if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    test_name = form.getvalue('Txt_testname').strip()
    prjid = form.getvalue('prjid').strip()
    userid = form.getvalue('userid').strip()
    res_time = form.getvalue('res_time').strip()
##    test_name = "stad_2207"
##    prjid = "838"
##    userid = "42"
##    res_time = "10"
    test_name = test_name.lower()
    #print("Start process - " + str(datetime.datetime.now()))
    process(test_name,prjid,userid,res_time)
    #print("endprocess - " + str(datetime.datetime.now()))
