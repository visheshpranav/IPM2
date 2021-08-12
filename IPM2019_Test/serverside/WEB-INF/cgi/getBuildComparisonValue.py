import cgi, cgitb,sys
import cgitb; cgitb.enable()
from elasticsearch import Elasticsearch
import elasticsearch.helpers

form = cgi.FieldStorage()
user_id = form.getvalue("user_id")
build1 = form.getvalue("build1")
build2 = form.getvalue("build2")
workstream = form.getvalue("workstream")
#For manual verification
##build1="QH1_STAD_0708"
##build2="QH1_STAD_0308"
##workstream ="FI"
##user_id = "42"
############################
build1 = user_id + "_" + build1.lower()
build2 = user_id + "_" + build2.lower()

def dd_func(build1, build2, workstream):
##    if workstream=="CO":
##        return [[4,3,2,3,2,3],[5,2,1,1,4,2]]
##    else:
##        return [[2,1,5,2,4,1],[1,3,4,4,1,5]]
    return [get_avg(workstream, build1),get_avg(workstream, build2)]
##    return [[4,3,2,3,2,3],[5,2,1,1,4,2]]


def get_avg(GIVEN_WORKSTREAM, build):
    es = Elasticsearch('localhost', port=9200)

    res = es.search(index='sap_stad', body={"size":0,"query":{"bool":{"must":[{"match":{"LOG_NAME.keyword":build}}]}},"aggs":{"datevalue":{"terms":{"field":"TRANSACTION_OR_JOBNAME.keyword","size": 10000},"aggs":{"avg_wait":{"avg":{"field":"WAIT_TIME"}},"avg_cpu":{"avg":{"field":"CPU_TIME"}},"avg_processing":{"avg":{"field":"PROCESSING_TIME"}},"avg_gui":{"avg":{"field":"GUI_TIME"}},"avg_db":{"avg":{"field":"DB_REQ_TIME"}},"avg_resp":{"avg":{"field":"RESPONSE_TIME"}}}}}})
    print(len(res["aggregations"]["datevalue"]["buckets"]))
    tcode_avg_dict=dict()
    for val in res["aggregations"]["datevalue"]["buckets"]:
        avg_list=[val['avg_processing']['value'], val['avg_wait']['value'], val['avg_cpu']['value'], val['avg_db']['value'], val['avg_gui']['value'], val['avg_resp']['value']]
        tcode_avg_dict[val['key']]=avg_list

    #print(tcode_avg_dict)

    ws_dict=dict()
    res = es.search(index='sap_workstream', body={"size":10000, "query": {"match_all": {}}} )

    for val in res['hits']['hits']:
        if val['_source']['Workstream'] in ws_dict:
            ws_dict[val['_source']['Workstream']].append(val['_source']['Tcode'])
        else:
            ws_dict[val['_source']['Workstream']] = []

    ws_item_avg=[]
    #print(ws_dict)
    ws_tcodes=ws_dict[GIVEN_WORKSTREAM]
    total_avg_list=[]
    for val in ws_tcodes:
        if val in tcode_avg_dict:
            total_avg_list.append(tcode_avg_dict[val])     
    
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
    final_list = [wait_time,cpu_time,db_time,process_time,gui_time,response_time]
    #print(val)
    myfunc = lambda val,length:round(val/length,2) if round(val/length,2) else 'NA'
##    print(final_list,total_avg_list)
    if total_avg_list:
        return [myfunc(val,len(total_avg_list)) for val in final_list]
##    return [round(wait_time,2), cpu_time , round(db_time,2), round(process_time,2), round(gui_time,2), round(response_time,2)]
    else:
        return []



val=dd_func(build1.lower(), build2.lower(), workstream)

print ("Content-type: text/html \n\n");
print(val)
