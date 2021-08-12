# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 21:30:18 2021

@author: v.a.subhash.krishna
"""

import pandas as pd
import string,cgi, glob, os
import configparser, shutil
from murex_master_data import master_data

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')

def is_sub(sub, lst):
    ln = len(sub)
    pos = -1
    for i in range(len(lst) - ln + 1):
        if lst[i: i + ln] == sub:
            pos = i
    return pos
    # return any(lst[i: i + ln] == sub for i in range(len(lst) - ln + 1))

def dist_type(type_list):
    queue_count = dict()
    final_list = []
    for val in type_list:
        if val.split(':')[0] in queue_count:
            queue_count[val.split(':')[0]] += 1
            final_queue_name = val.split(':')[0]+'_'+str(queue_count[val.split(':')[0]])
            final_list.append(final_queue_name+':'+':'.join(val.split(':')[1:]))
        else:
            final_list.append(val)
            queue_count[val.split(':')[0]] = 1
    for key,val in queue_count.items():
        if val > 1:
            # print(key)
            for item in final_list:
                if key == item.split(':')[0]:
                    final_queue_name = item.split(':')[0]+'_1'
                    pos = final_list.index(item)
                    final_list[pos] = final_queue_name+':'+':'.join(item.split(':')[1:])
                    break
        
    return final_list

def typename(last_type):
    # print(last_type)
    last_char = last_type[-1]
    # print(last_char)
    next_char = chr((ord(last_char)+1 - 65) % 26 + 65)
    if last_char == 'Z':
        if len(last_type) > 1:
            next_type = typename(last_type[:-1])+next_char
        else:
            next_type = next_char+next_char
    else:
        next_type = last_type[:-1]+next_char
    return next_type
        

def get_dict(file_path, c_dict, typology_dict, master_df):
    data = pd.read_csv(file_path)
    master_df = pd.concat([master_df,data])
    #data = pd.read_csv("dendo_new.csv")
    data = data[["TYPOLOGY", "CONTRACT_ID", "OSP_QUEUE_NAME", "FROM_TASK", "TO_TASK", "Entry Time"]]

    data['Entry Time']=data['Entry Time'].apply(lambda x: x.split(" ")[1])

    data['Entry Time'] = pd.to_datetime(data['Entry Time'], format='%H:%M:%S.%f')

    data=data.sort_values(['TYPOLOGY'], ascending=True) \
        .groupby(['TYPOLOGY'], sort=False) \
        .apply(lambda x: x.sort_values(['Entry Time'], ascending=True)) \
        .reset_index(drop=True)

    #data = data[["TYPOLOGY", "CONTRACT_ID", "OSP_QUEUE_NAME", "FROM_TASK", "TO_TASK"]]
    data['Count']=1

    for index, row in data.iterrows():
        if row["TYPOLOGY"] not in typology_dict:
            typology_dict[row["TYPOLOGY"]] = set()
        typology_dict[row["TYPOLOGY"]].add(row["CONTRACT_ID"])
        if row["CONTRACT_ID"] in c_dict:
            c_dict[row["CONTRACT_ID"]].append(row["OSP_QUEUE_NAME"]+":"+row["FROM_TASK"]+":"+row["TO_TASK"])
            
        else:
            c_dict[row["CONTRACT_ID"]]=[]
            c_dict[row["CONTRACT_ID"]].append(row["OSP_QUEUE_NAME"]+":"+row["FROM_TASK"]+":"+row["TO_TASK"])
            
    return c_dict, typology_dict, master_df

def type_def(c_dict, typology_dict):
    type_dict = dict()
    dendo_dict = dict()
    type_cid_dict = dict()
    dist_type_dict = dict()
    # key_list = ['Type '+val for val in key_list]
    start_type = 'Type A'
    # cid_list = list(c_dict.keys())
    # print(typology_dict)
    for typo,c_list in typology_dict.items():
        if len(type_dict):
            start_type = list(sorted(type_dict.keys()))[-1]
        c_list = list(c_list)
        dendo_dict[typo] = dict()
        for cid in c_list:
            flag = 1
            for type_id, type_set in type_dict.items():
                # pos = is_sub(c_dict[cid], type_set)
                if c_dict[cid] == type_set:
                    flag = 0
                    if type_id.split(' ')[1] not in type_cid_dict:
                        type_cid_dict[type_id.split(' ')[1]] = []
                    type_cid_dict[type_id.split(' ')[1]].append(cid)
                    if type_id not in dendo_dict[typo]:
                        dendo_dict[typo][type_id] = []
                        dendo_dict[typo][type_id].append(dist_type_dict[type_id])
                        val_list = [1 for val in range(len(c_dict[cid]))]
                        dendo_dict[typo][type_id].append(val_list)
                        # for val in c_dict[cid]:
                        #     dendo_dict[typo][type_id][val] = 1
                    else:
                        val_list = [val+1 for val in dendo_dict[typo][type_id][1]]
                        dendo_dict[typo][type_id][1] = val_list
                        # for val in c_dict[cid]:
                        #     dendo_dict[typo][type_id][val]+=1
                    break
                # need to increase the count
                # elif pos != -1:
                #     # print(c_dict[cid])
                #     # print('#'*20)
                #     # print(type_set)
                #     sub_set_range = range(pos,pos+len(c_dict[cid]))
                #     flag = 0
                #     if type_id.split(' ')[1] not in type_cid_dict:
                #         type_cid_dict[type_id.split(' ')[1]] = []
                #     type_cid_dict[type_id.split(' ')[1]].append(cid)
                #     if type_id not in dendo_dict[typo]:
                #         dendo_dict[typo][type_id] = []
                #         dendo_dict[typo][type_id].append(type_set)
                #         val_list = [1 if val in sub_set_range else 0 for val in range(len(type_set))]
                #         dendo_dict[typo][type_id].append(val_list)
                #     else:
                #         val_list = [dendo_dict[typo][type_id][1][val]+1 if val in sub_set_range else dendo_dict[typo][type_id][1][val] for val in range(len(dendo_dict[typo][type_id][1]))]
                #         dendo_dict[typo][type_id][1] = val_list
                #         # for val in c_dict[cid]:
                #         #     dendo_dict[typo][type_id][val]+=1
                #     break
                
            if flag:
                # print(start_type)
                if len(type_dict):
                    start_type = 'Type '+typename(start_type.split(' ')[-1])
                dist_type_dict[start_type] = dist_type(c_dict[cid])
                if start_type.split(' ')[1] not in type_cid_dict:
                    type_cid_dict[start_type.split(' ')[1]] = []
                type_cid_dict[start_type.split(' ')[1]].append(cid)
                type_dict[start_type] = c_dict[cid]
                dendo_dict[typo][start_type] = []
                dendo_dict[typo][start_type].append(dist_type_dict[start_type])
                val_list = [1 for val in range(len(c_dict[cid]))]
                dendo_dict[typo][start_type].append(val_list)
    return dendo_dict, type_dict, type_cid_dict

def generate_dendo(dendo_dict, type_cid_dict, master_df, output_path):
    dendo_list = []
    final_list = []
    for typo,typo_dict in dendo_dict.items():
        for Type, type_dict in typo_dict.items():
            # print(type_dict)
            type_list = type_dict[0]
            val_list = type_dict[1]
            for pos in range(len(type_list)):
                if val_list[pos]:
                    new_line = ['Murex', typo, Type]
                    key_list = type_list[pos].split(':')
                    new_line.extend(key_list)
                    new_line.append(val_list[pos])
                # for key, val in type_dict.items():
                #     key_list = key.split(':')
                #     for val2 in key_list:
                #         new_line.append(val2)
                #     new_line.append(val)
                    dendo_list.append(new_line)
    df = pd.DataFrame(dendo_list,columns=['Category','Level1','Level2','Level3','Level4','Level5','Count'])
    df.to_csv(output_path+'//OSP_Out.csv',index=False, header=True)
    download_df = pd.DataFrame(dendo_list, columns = ['Category','Trade Typology','Type','OSP Queue name','From Task','To Task','Count'])
    dev_master_df = pd.read_csv(output_path+'//Del_master.csv')
    dev_master_df.rename(columns={'Contract ID':'Del_Contract_ID', 'OSP_Contract_ID':'CONTRACT_ID'},inplace=True)
    dev_master_df.drop(['Flow amount','Flow currency'],axis=1,inplace=True)
    unique_cid = dev_master_df['CONTRACT_ID'].unique()
    dev_master_df['No of Files'] = 1
    for cid in unique_cid:
        flow_type = dev_master_df.loc[dev_master_df['CONTRACT_ID'] == cid]['Flow type(Send or receive)'].tolist()
        flowtype_val = flow_type[0]
        if 'Send' in flow_type and 'Receive' in flow_type:
            # print('entered')
            # print(cid)
            flowtype_val = 'Send/Receive'
        
        dev_master_df.loc[dev_master_df['CONTRACT_ID'] == cid, 'Flow type(Send or receive)'] = flowtype_val
        # print(dev_master_df.loc[dev_master_df['CONTRACT_ID'] == cid]['Flow type(Send or receive)'])
        dev_master_df.loc[dev_master_df['CONTRACT_ID'] == cid, 'No of Files'] = len(flow_type)
    dev_master_df.drop_duplicates(inplace=True)
    # print(dev_master_df.columns)
    master_df = master_df.join(dev_master_df.set_index('CONTRACT_ID'),on=['CONTRACT_ID'],how='inner')
    master_df.to_csv(output_path+'//OSP_Master.csv',index=False, header=True)
    # print(master_df.columns)
    values = ['' for i in range(len(master_df))]
    master_df.insert(loc = 0, column = 'TYPE', value = values)
    
    master_df.reset_index(drop=True, inplace=True)
    # print(master_df.index)
    for each_type,cid_list in type_cid_dict.items():
        for cid in cid_list:
            cid_master_df = master_df.loc[master_df['CONTRACT_ID'] == cid]
            cid_master_df['TYPE'] = 'Type '+each_type
            master_df.loc[cid_master_df.index,:]=cid_master_df
    unique_typology = list(master_df['TYPOLOGY'].unique())
    for typo in unique_typology:
        df = master_df.loc[master_df['TYPOLOGY'] == typo]
        types = list(df['TYPE'].unique())
        for _type in types:
            df1 = df.loc[df['TYPE'] == _type]
            count = len(df1['CONTRACT_ID'].unique())
            final_list.append([typo,_type,count])
    df = pd.DataFrame(final_list,columns=['Typology','Type','Count'])
    df.to_csv(output_path+'//OSP_Type_Typology.csv',index=False, header=True)
            # master_df.update(cid_master_df)
    with pd.ExcelWriter(output_path+'//OSP_Master.xlsx') as writer:
        download_df.to_excel(writer, sheet_name='Count', index=False, header=True)
        master_df.to_excel(writer, sheet_name='Master', index=False, header=True)

def generate_type_csv(type_dict, type_cid_dict,typology_dict, master_path, output_path):
    type_list = []
    unique_queue = dict()
    for type_name,dict_type in type_dict.items():
        unique_queue[type_name] = set()
        for val in dict_type:
            new_line = [type_name]
            new_line.extend(val.split(':'))
            unique_queue[type_name].add(val.split(':')[0])
            type_list.append(new_line)
        unique_queue[type_name] = list(unique_queue[type_name])
    master_data(output_path, master_path, type_cid_dict,typology_dict, unique_queue)
    df = pd.DataFrame(type_list,columns=['Type','OSP Queue name','From Task','To Task'])
    df.to_csv(output_path+'//Types.csv',index=False, header=True)

def get_typology(master_df, output_path):
    final_list = []
    unique_typology = list(master_df['TYPOLOGY'].unique())
    for typo in unique_typology:
        df = master_df.loc[master_df['TYPOLOGY'] == typo]
        count = len(df['CONTRACT_ID'].unique())
        final_list.append([typo,count])
    df = pd.DataFrame(final_list,columns=['Typology','Count'])
    df.to_csv(output_path+'//OSP_Typology.csv',index=False, header=True)

if __name__=="__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    userid = form.getvalue('user_id')
    test_name = form.getvalue('report_name')
    # logtype = form.getvalue('logtype').split("\n")[1].strip()
##    userid="44"
##    test_name="testospp"
    logtype="OSP"
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\"+str(logtype)
    master_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\DeliverableMXML"
    file_path = dir_path + "\\*.csv"
    # file_path = 'C:\\Users\\v.a.subhash.krishna\\Downloads\\murex_log_parsing\\OSP_input.csv'
    # master_path = 'C:\\Users\\v.a.subhash.krishna\\Downloads\\Murex files_old\\DeliverablesMxml_15072020'
    files = glob.glob(file_path)
    c_dict=dict()
    typology_dict = dict()
    master_df = pd.DataFrame()
    for file in files:
        c_dict, typology_dict, master_df=get_dict(file, c_dict, typology_dict, master_df)
    dendo_dict, type_dict, type_cid_dict = type_def(c_dict, typology_dict)
    # print(type_cid_dict)
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    # output_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\OSP_Output\\'
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    get_typology(master_df, output_path)
    generate_type_csv(type_dict, type_cid_dict,typology_dict, master_path, output_path)
    generate_dendo(dendo_dict, type_cid_dict, master_df, output_path)
    