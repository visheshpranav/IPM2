import pandas as pd 
from datetime import datetime
import string
import copy
import json,os
import string,cgi, glob
import configparser, shutil
#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')

def get_dict(file_path):
    #data = pd.read_csv("dendo_new.csv")
    data = pd.read_csv(file_path)
    data = data[["TYPOLOGY", "CONTRACT_ID", "OSP_QUEUE_NAME", "FROM_TASK", "TO_TASK", "ENTRY TIME"]]

    data['ENTRY TIME']=data['ENTRY TIME'].apply(lambda x: x.split(" ")[1])

    data['ENTRY TIME'] = pd.to_datetime(data['ENTRY TIME'], format='%H:%M:%S.%f')

    data=data.sort_values(['TYPOLOGY'], ascending=True) \
        .groupby(['TYPOLOGY'], sort=False) \
        .apply(lambda x: x.sort_values(['ENTRY TIME'], ascending=True)) \
        .reset_index(drop=True)

    #data = data[["TYPOLOGY", "CONTRACT_ID", "OSP_QUEUE_NAME", "FROM_TASK", "TO_TASK"]]
    data['Failure']=1

    c_dict=dict()

    for index, row in data.iterrows():
        if row["CONTRACT_ID"] in c_dict:
            c_dict[row["CONTRACT_ID"]].append(row["OSP_QUEUE_NAME"]+":"+row["TYPOLOGY"]+":"+row["FROM_TASK"]+":"+row["TO_TASK"])
        else:
            c_dict[row["CONTRACT_ID"]]=[]
            c_dict[row["CONTRACT_ID"]].append(row["OSP_QUEUE_NAME"]+":"+row["TYPOLOGY"]+":"+row["FROM_TASK"]+":"+row["TO_TASK"])
            
    return c_dict

def get_contact(c_dict):
    contact_list=list(c_dict.keys())
    subset_dict=dict()
    same_list1=[]

    for v1 in contact_list:
        subset_dict[v1]=[]
        for v2 in contact_list:
            if v1 != v2:
                flag = 0
                #subset check
                c_dict[v1].sort()
                c_dict[v2].sort()
                if c_dict[v1]==c_dict[v2]:
                    sm_lst=[v1, v2]
                    sm_lst.sort()
                    same_list1.append(sm_lst)
                if(all(x in c_dict[v1] for x in c_dict[v2])):
                    flag = 1
                if flag:
                    subset_dict[v1].append(v2)

    # removing duplicate sublist 
    same_list1 = list(set(map(lambda i: tuple(sorted(i)), same_list1)))
    same_list2=[]
    same_list3=[]

    for v in same_list1:
        same_list2.append(v[0])
        same_list3.append(v[1])

    remove_list=set()
    for v in contact_list:
        for k, val_list in subset_dict.items():
            if v in val_list:
                remove_list.add(v)

    remove_list=[i for i in remove_list if i not in same_list2]
    for val in remove_list:
        subset_dict.pop(val)

    remove_list2=set()
    for v1 in list(subset_dict.keys()):
        for k, v2 in subset_dict.items():
            if v1 in subset_dict[k]:
                remove_list2.add(v1)

    for val in remove_list2:
        subset_dict.pop(val)

    return subset_dict, same_list3

def get_count(c_dict, subset_dict, same_list3):
    type_count_dict=dict()
    for k, v_lst in subset_dict.items():
        val_dict=dict()
        for val in c_dict[k]:
            val_count=1     
            for v1 in v_lst:
                if val in c_dict[v1]:
                    val_count=val_count+1
            val_dict[val]=val_count
        type_count_dict[k]=val_dict
        
    return type_count_dict

def get_df(type_count_dict):
    df_list=[]
    for key, val in type_count_dict.items():
        for k, v1 in val.items():
            temp_list=k.split(":")
            temp_list.append(key)
            temp_list.append(v1)
            df_list.append(temp_list)
        
    df = pd.DataFrame(df_list)
    df.columns = ["OSP_QUEUE_NAME", "TYPOLOGY", "FROM_TASK", "TO_TASK", "Type", "Failure"]

    df = df[[ "Type", "TYPOLOGY", "OSP_QUEUE_NAME", "FROM_TASK", "TO_TASK", "Failure"]]
    #df.rename(columns={"Type":'Category', "TYPOLOGY":'Level1', "OSP_QUEUE_NAME":"Level2", "FROM_TASK":'Level3', "TO_TASK":"Level4"}, inplace=True)

    return df

def change_col_name(df):
    unq_cat_list=df.Category.unique()
    alpha_list=list(string.ascii_lowercase)
    
    c=0
    cat_change_dict=dict()
    
    for i in range(0,len(unq_cat_list)):
        cat_change_dict[unq_cat_list[i]]= alpha_list[i]

    df['Category']=df['Category'].apply(lambda x: "type"+cat_change_dict[x])

    return df
    
if __name__=="__main__":    
    print("Content-type: text/html \n");
##    form = cgi.FieldStorage()
##    userid = form.getvalue('user_id')
##    test_name = form.getvalue('report_name')
##    logtype = form.getvalue('logtype').split("\n")[1].strip()
    userid="44"
    test_name="O10k"
    logtype="OSP"
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\OSP"
    file_path = dir_path + "\\*.csv"
    files = glob.glob(file_path)
    osp_filepath=""
    for file in files:
        osp_filepath = file
        c_dict=get_dict(file)
    subset_dict, same_list3=get_contact(c_dict)
    type_count_dict=get_count(c_dict, subset_dict, same_list3)
    df=get_df(type_count_dict)
    #df=change_col_name(df)

    #df=df[["OSP_QUEUE_NAME", "TYPOLOGY", "Failure"]]
    queue_name=set()
    for indx, row in df.iterrows():
        queue_name.add(row["OSP_QUEUE_NAME"])

    queue_name=list(queue_name)
    queue_name.sort()

    print(queue_name)
    print("###############################################################################")
    #print(df.Type)
    bar_chart_dict=dict()
    unique_contractid = list(df['Type'].unique())
    df2 = pd.read_csv(osp_filepath)
    #print (unique_contractid)
    typology_dict={}
    for cid in unique_contractid:
        df3 = df2.loc[df2['CONTRACT_ID']==cid]
        
        typology_dict[df3['TYPOLOGY'].unique()[0]] = {}
        typology_dict[df3['TYPOLOGY'].unique()[0]]['Family']=df3['FAMILY'].unique()[0]
        typology_dict[df3['TYPOLOGY'].unique()[0]]['Group']=df3['GROUP'].unique()[0]
    #print(typology_dict)
        
    for index, row in df.iterrows():
        if row["TYPOLOGY"] in bar_chart_dict:
            if row["OSP_QUEUE_NAME"] in bar_chart_dict[row["TYPOLOGY"]]:
                bar_chart_dict[row["TYPOLOGY"]][row["OSP_QUEUE_NAME"]]=int(bar_chart_dict[row["TYPOLOGY"]][row["OSP_QUEUE_NAME"]])+row['Failure']
            else:
                bar_chart_dict[row["TYPOLOGY"]][row["OSP_QUEUE_NAME"]]=row["Failure"]
        else:
            bar_chart_dict[row["TYPOLOGY"]]=copy.deepcopy({row["OSP_QUEUE_NAME"]:row["Failure"]})
            # print(row['Type'])
##    print(bar_chart_dict)

    final_df_list=[]
    for k1, v1_dict in bar_chart_dict.items():
        temp_list=[]
        temp_list.append(k1)
        for v2 in queue_name:
            if v2 in v1_dict:
                temp_list.append(bar_chart_dict[k1][v2])
            else:
                temp_list.append("")    
        final_df_list.append(temp_list)

    print(final_df_list)
    df = pd.DataFrame(final_df_list)
    df.columns = [""]+queue_name
##    df.to_csv("bar_graph.csv", index=False)
    typology_list=[]
    for val in final_df_list:
        typology_list.append(val.pop(0))
    dict1 = {"Queue":"", "name":"", "count":""}
    queue_list=[]
    j=0
   
    for key in bar_chart_dict.keys():
        for values in bar_chart_dict[key].keys():
            val_list = [val for val in queue_list if val['Queue']==values]
            if val_list:
                val_list[0]['tops'].append({'name':key,'count': bar_chart_dict[key][values],\
                                            'family':typology_dict[key]['Family'],\
                                           'group':typology_dict[key]['Group']})
            else:
                dict1 =dict()
                dict1['Queue'] = values
                dict1['tops'] = []
                dict1['tops'].append({'name':key,'count': bar_chart_dict[key][values],\
                                      'family':typology_dict[key]['Family'],\
                                           'group':typology_dict[key]['Group']})
                queue_list.append(dict1)
        
##    out = df.to_json(orient = "records")
##    print(out)
    OSP_Outfilename = "OSP_queuecount.json" 
    with open(OSP_Outfilename, 'w') as f:
        json.dump(queue_list,f)   
      
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    if not os.path.exists(output_path):
        os.mkdir(output_path) 
    shutil.move(OSP_Outfilename, output_path+"/"+OSP_Outfilename)
    df.to_csv(output_path+"/"+test_name+"_OSP_queuecount.csv", index=False)
