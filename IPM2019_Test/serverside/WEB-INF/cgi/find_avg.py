from elasticsearch import Elasticsearch
import elasticsearch.helpers

GIVEN_WORKSTREAM="WS"

def get_avg(GIVEN_WORKSTREAM):
    es = Elasticsearch('localhost', port=9200)

    res = es.search(index='sap_stad', body={"size":0,"aggs":{"datevalue":{"terms":{"field":"TRANSACTION_OR_JOBNAME.keyword"},"aggs":{"avg_wait":{"avg":{"field":"WAIT_TIME"}},"avg_cpu":{"avg":{"field":"CPU_TIME"}},"avg_processing":{"avg":{"field":"PROCESSING_TIME"}},"avg_gui":{"avg":{"field":"GUI_TIME"}},"avg_db":{"avg":{"field":"DB_REQ_TIME"}},"avg_resp":{"avg":{"field":"RESPONSE_TIME"}}}}}})


    tcode_avg_dict=dict()

    for val in res["aggregations"]["datevalue"]["buckets"]:
    ##    print(val['key'])
        avg_list=[val['avg_processing']['value'], val['avg_wait']['value'], val['avg_cpu']['value'], val['avg_db']['value'], val['avg_gui']['value'], val['avg_resp']['value']]
        tcode_avg_dict[val['key']]=avg_list

##    print(tcode_avg_dict)

    ws_dict=dict()

    res = es.search(index='sap_workstream', body={"size":1000, "query": {"match_all": {}}} )

    for val in res['hits']['hits']:
        if val['_source']['Workstream'] in ws_dict:
            ws_dict[val['_source']['Workstream']].append(val['_source']['Tcode'])
        else:
            ws_dict[val['_source']['Workstream']] = []

    ws_item_avg=[]

##    print(ws_dict)
##    print(ws_dict[GIVEN_WORKSTREAM])

    ws_tcodes=ws_dict[GIVEN_WORKSTREAM]

##    print(ws_tcodes)

    total_avg_list=[]

    for val in ws_tcodes:
        if val in tcode_avg_dict:
            total_avg_list.append(tcode_avg_dict[val])
            
##    print(tcode_avg_dict)
    
    wait_time=0
    cpu_time=0
    db_time=0
    process_time=0
    gui_time=0
    response_time=0

    for val in total_avg_list:
        wait_time+=val[0]
        cpu_time+=val[1]
        db_time+=val[2]
        process_time+=val[3]
        gui_time+=val[4]
        response_time+=val[5]
        

    return [round(wait_time), round(cpu_time), round(db_time), round(process_time), round(gui_time), round(response_time)]

print(get_avg("Basis/ABAP"))
    
##for k, v in ws_dict.items():
##    ws_tcode_avg_list=[]
##    
##    for val in ws_dict[k]:
##        if val in tcode_avg_dict:
##            ws_tcode_avg_list.append(tcode_avg_dict[val])
##
##    print(ws_tcode_avg_list)

    
##[DB,CPU,Process,4,5]

##RETURN: {"W1":[1,2,3,4,5], "W2":[1,2,3,4,5]...........}  





##D1, D2, 
##Res : W1 W2
