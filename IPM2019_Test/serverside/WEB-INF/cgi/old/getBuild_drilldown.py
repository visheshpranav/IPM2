import cgi, cgitb,sys
import cgitb; cgitb.enable()
from elasticsearch import Elasticsearch
import elasticsearch.helpers

form = cgi.FieldStorage()
user_id = form.getvalue("user_id")
build1 = form.getvalue("build1")
build2 = form.getvalue("build2")
workstream = form.getvalue("workstream")
##build1="STAD_18Jun"
##build2="STAD_19_Jun"
##workstream ="SD"
##user_id = "42"
build1 = user_id + "_" + build1.lower()
build2 = user_id + "_" + build2.lower()


def get_drillDown(GIVEN_WORKSTREAM, build1, build2):
    es = Elasticsearch('localhost', port=9200)

    res1 = es.search(index='sap_stad', body={"size":0,"query":{"bool":{"must":[{"match":{"LOG_NAME.keyword":build1}}]}},"aggs":{"datevalue":{"terms":{"field":"TRANSACTION_OR_JOBNAME.keyword","size": 10000},"aggs":{"avg_wait":{"avg":{"field":"WAIT_TIME"}},"avg_cpu":{"avg":{"field":"CPU_TIME"}},"avg_processing":{"avg":{"field":"PROCESSING_TIME"}},"avg_gui":{"avg":{"field":"GUI_TIME"}},"avg_db":{"avg":{"field":"DB_REQ_TIME"}},"avg_resp":{"avg":{"field":"RESPONSE_TIME"}}}}}})
    res2 = es.search(index='sap_stad', body={"size":0,"query":{"bool":{"must":[{"match":{"LOG_NAME.keyword":build2}}]}},"aggs":{"datevalue":{"terms":{"field":"TRANSACTION_OR_JOBNAME.keyword","size": 10000},"aggs":{"avg_wait":{"avg":{"field":"WAIT_TIME"}},"avg_cpu":{"avg":{"field":"CPU_TIME"}},"avg_processing":{"avg":{"field":"PROCESSING_TIME"}},"avg_gui":{"avg":{"field":"GUI_TIME"}},"avg_db":{"avg":{"field":"DB_REQ_TIME"}},"avg_resp":{"avg":{"field":"RESPONSE_TIME"}}}}}})

    tcode_avg_dict1=dict()
    tcode_avg_dict2=dict()
    
    for val in res1["aggregations"]["datevalue"]["buckets"]:
        avg_list=[val['avg_resp']['value']]
        tcode_avg_dict1[val['key']]=avg_list

    for val in res2["aggregations"]["datevalue"]["buckets"]:
        avg_list=[val['avg_resp']['value']]
        tcode_avg_dict2[val['key']]=avg_list

##    print(tcode_avg_dict1)
##    print(tcode_avg_dict2)

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

    drill_tcodes_dict=dict()

##    tcode_avg_dict1={"T1":[3], "T2":[4], "T3":[1]}
##    tcode_avg_dict2={"T1":[2], "T2":[6], "T3":[1]}
##    ws_tcodes=["T1", "T2", "T3"]

    for tcode in ws_tcodes:
        if tcode in tcode_avg_dict1:
            if tcode in tcode_avg_dict2:
                if tcode_avg_dict1[tcode][0]<tcode_avg_dict2[tcode][0]:
                    #print(tcode_avg_dict2[tcode][0],tcode_avg_dict1[tcode][0])
                    drill_tcodes_dict[tcode]=str(round(tcode_avg_dict2[tcode][0],2))+"&"+str(round((int(round(tcode_avg_dict2[tcode][0])) - int(round(tcode_avg_dict1[tcode][0])))/int(round(tcode_avg_dict1[tcode][0])) * 100))

        
    return drill_tcodes_dict

print("Content-type: text/html \n");
print(get_drillDown(workstream, build1, build2))

##val=dd_func(build1.lower(), build2.lower(), workstream)
##
##print ("Content-type: text/html \n\n");
##print(val)
