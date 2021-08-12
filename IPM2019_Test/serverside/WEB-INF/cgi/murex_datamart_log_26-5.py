# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 10:41:41 2021

@author: v.a.subhash.krishna
"""

import pandas as pd
import json,copy, glob
import os, cgi, configparser

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def generate_groups(value, dendogroups, each_group):
    for key,values in value.items():
        # all_columns.add(key)
        each_group.append(key)
        if isinstance(values,dict):
            dendogroups,each_group = generate_groups(values,dendogroups,each_group)
        elif not values:
            final_group = copy.deepcopy(each_group)
            col_name = final_group.pop(-1)
            dendogroups.append([final_group,col_name])
        else:
            for val in values:
                final_group = copy.deepcopy(each_group)
                # all_columns.add(val)
                dendogroups.append([final_group,val])
        each_group.pop(-1)
    return dendogroups,each_group

def get_all_columns(value, all_columns):
    for key,values in value.items():
        all_columns.add(key)
        if isinstance(values,dict):
            all_columns = get_all_columns(values, all_columns)
        else:
            for val in values:
                all_columns.add(val)
    return all_columns

def generate_df(file_path):
    files = glob.glob(file_path)
    df_list = []
    for file in files:
        if file.endswith('.csv'):
            df_list.append(pd.read_csv(file))
        else:
            df_list.append(pd.excel(file))
    group_df = pd.concat(df_list)
    return group_df

# def get_master_df(dfs, column_details_df):
#     for group in dfs:
#         print(group[0])
#         master_df = group[1].join(column_details_df.set_index('REPORT_LABEL'),on=['REPORT_LABEL'])
#         yield master_df
        
def group_by_df(datamart_df):
    dfs = datamart_df.groupby('REPORT_LABEL')
    for val in dfs:
        yield val
        
def generate_dendo(datamart_df,column_details_df,output_path):
    # datamart_df = pd.read_csv(file_path)
    # column_details_df = pd.read_csv(column_names_file_path)
    patterns = json.load(open("C:\\LAPAM2019\\Config\\Datamart_dendo_patterns.json"))
    # patterns = json.load(open("C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_Input\\Datamart_dendo_patterns.json"))
    column_details_df = column_details_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    datamart_df = datamart_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    if 'REPORT_LABEL' in datamart_df.columns:
        datamart_df.rename(columns={'REPORT_LABEL':'REPORT_TABLE','INDEXES':'INDEXED'},inplace=True)
        
    column_details_df.rename(columns={'TABLE_NAME':'REPORT_TABLE'},inplace=True)
##    print(datamart_df.columns)
    # dfs = datamart_df.groupby('REPORT_LABEL')
#     all_columns = set()
#     for dm_type,value in patterns.items():
#         all_columns = get_all_columns(value, all_columns)
# ##    for group in dfs:
# ##        print(group[0])
#         for group in group_by_df(datamart_df):
#             print(group[0])
#             master_df = group[1].join(column_details_df.set_index('REPORT_LABEL'),on=['REPORT_LABEL'])
#             all_cols = list(all_columns)
#             all_cols.remove('REPORT_LABEL')
#             all_cols.insert(0,'REPORT_LABEL')
#             master_cols = list(master_df.columns)
#             rem_cols = [i for i in master_cols+all_cols if i not in master_cols or i not in all_cols]
#             all_cols.extend(rem_cols)
#             master_df = master_df[all_cols]
#             master_df.to_csv(output_path+'//Full_Datamart_Master.csv',mode = 'a',index=False, header=True)
    # print(len(datamart_df))
    # column_details_df.rename(columns={'TABLE_NAME':'REPORT_LABEL'},inplace=True)
    # master_df = datamart_df.join(column_details_df.set_index('REPORT_LABEL'),on=['REPORT_LABEL'])
    # print(datamart_df.columns)
    if 'TIME' not in datamart_df.columns:
        datamart_df['EXIT_TIME'] = pd.to_datetime(datamart_df['EXIT_TIME'])
        datamart_df['ENTRY_TIME'] = pd.to_datetime(datamart_df['ENTRY_TIME'])
        datamart_df['DIFF'] = datamart_df['EXIT_TIME'] - datamart_df['ENTRY_TIME']
        datamart_df['TIME'] = datamart_df['DIFF'].dt.total_seconds()
        datamart_df.drop('DIFF', axis=1,inplace=True)
    # print(datamart_df['TIME'])
    datamart_df['TIME'] = datamart_df['TIME'].astype('int32')
    datamart_df['TIME'] = round(datamart_df['TIME']/3600,1)
    datamart_df.fillna('Not Available', inplace=True)
    datamart_df.replace('','Not Available', inplace=True)
    output_json = {"name": "Root","tag": "Root","children": []}
    for dm_type,value in patterns.items():
        dendogroups = []
        each_group = []
        output_json["children"].append({"name": dm_type, "tag": "Node0","children": []})
        val_json = [val for val in output_json["children"] if val['name']==dm_type][0]
        # print(val_json)
        dendogroups,each_group = generate_groups(value, dendogroups, each_group)
        for each_group in dendogroups:
##            print(each_group)
            groupby_df = datamart_df.groupby(each_group[0])
            for row in groupby_df:
                sub_val = [val_json]
                # print(row[0])
                if 'COLUMNS' == each_group[1]:
                    report_label = row[0][-1]
                    column_df1 = column_details_df.loc[column_details_df['REPORT_TABLE'] == report_label]
                    # print(column_df1)
                    # print(row[0])
                    if '' not in row[0]:
                        # print(row[0])
                        unique_values = column_df1['COLUMNS'].unique()
                        for u_val in unique_values:
                            
                            sub_val = [val_json]
                            for i in range(len(row[0])):
                                if each_group[0][i] == 'SOD/EOD/INTRADAY':
                                    prev_sub_val = sub_val
                                    # print(val_json)
                                    sub_val = [val for val in sub_val[0]["children"] if val['name'] == row[0][i] and val['value'] == row[0][i]]
                                    if not len(sub_val):
                                        prev_sub_val[0]["children"].append({"name": row[0][i],"tag": "Node"+str(i+1),"value": row[0][i], "children": []})
                                        sub_val = [val for val in prev_sub_val[0]["children"] if val['name'] == row[0][i] and val['value'] == row[0][i]]
                                else:
                                    prev_sub_val = sub_val
                                    sub_val = [val for val in sub_val[0]["children"] if val['name'] == each_group[0][i] and val['value'] == row[0][i]]
                                    if not len(sub_val):
                                        prev_sub_val[0]["children"].append({"name": each_group[0][i],"tag": "Node"+str(i+1),"value": row[0][i], "children": []})
                                        sub_val = [val for val in prev_sub_val[0]["children"] if val['name'] == each_group[0][i] and val['value'] == row[0][i]]
                            # final_val.extend(row[0])
                            prev_sub_val = sub_val
                            sub_val = [val for val in sub_val[0]["children"] if val['name'] == each_group[0][i] and val['value'] == u_val]
                            if not len(sub_val):
                                prev_sub_val[0]["children"].append({"name": each_group[1],"tag": "Node"+str(i+2),"value": u_val, "Count": 1})
                                sub_val = [val for val in prev_sub_val[0]["children"] if val['name'] == each_group[1] and val['value'] == u_val]
                            else:
                                sub_val[0]['Count'] += 1
                    continue
                level4_df = row[1]
                level4_df.fillna('Not Available',inplace=True)
                unique_level6 = level4_df[each_group[1]].unique()
                for val_level6 in unique_level6:
                    if val_level6 != '':
                        flag = 1
                        count_df = level4_df[level4_df[each_group[1]] == val_level6]
                        # print(level4_df[each_group[1]])
                        sub_val = [val_json]
                        # final_val.extend(row[0])
                        # print(each_group[0], row[0])
                        for i in range(len(row[0])):
                            if '' not in row[0]:
                                if each_group[0][i] == 'SOD/EOD/INTRADAY':
                                    prev_sub_val = sub_val
                                    sub_val = [val for val in sub_val[0]["children"] if val['name'] == row[0][i] and val['value'] == row[0][i]]
                                    if not len(sub_val):
                                        prev_sub_val[0]["children"].append({"name": row[0][i],"tag": "Node"+str(i+1),"value": row[0][i], "children": []})
                                        sub_val = [val for val in prev_sub_val[0]["children"] if val['name'] == row[0][i] and val['value'] == row[0][i]]
                                else:
                                    prev_sub_val = sub_val
                                    sub_val = [val for val in sub_val[0]["children"] if val['name'] == each_group[0][i] and val['value'] == row[0][i]]
                                    if not len(sub_val):
                                        prev_sub_val[0]["children"].append({"name": each_group[0][i],"tag": "Node"+str(i+1),"value": row[0][i], "children": []})
                                        # print(prev_sub_val)
                                        sub_val = [val for val in prev_sub_val[0]["children"] if val['name'] == each_group[0][i] and val['value'] == row[0][i]]
                                        
                            else:
                                flag = 0
                                break
                        if flag:
                            # print(row[0])
                            if val_level6 != 'Not Available': 
                                prev_sub_val = sub_val
                                # print(sub_val)
                                sub_val = [val for val in sub_val[0]["children"] if val['name'] == each_group[1] and val['value'] == val_level6]
                                if not len(sub_val):
                                    prev_sub_val[0]["children"].append({"name": each_group[1],"tag": "Node"+str(i+2),"value": val_level6, "Count": len(count_df)})
                                    sub_val = [val for val in prev_sub_val[0]["children"] if val['name'] == each_group[1] and val['value'] == val_level6]
                                else:
                                    sub_val[0]['Count'] += len(count_df)
                # print(val_json)
    # # print(all_columns)
    # all_cols = list(all_columns)
    # all_cols.remove('REPORT_LABEL')
    # all_cols.insert(0,'REPORT_LABEL')
    # master_cols = list(master_df.columns)
    # rem_cols = [i for i in master_cols+all_cols if i not in master_cols or i not in all_cols]
    # all_cols.extend(rem_cols)
    # master_df = master_df[all_cols]
    # # rearrange_order = 
    # master_df.to_csv(output_path+'//Full_Datamart_Master.csv',index=False, header=True)
    # print(output_json)
    json.dump(output_json,open(output_path+'//datamart_output.json','w'))
    # final_df = pd.DataFrame(final_list,columns = ['Category','Level1','Level2','Level3','Level4','Level5','Level6','Level7',
    #                                               'Level8','Level9','Level10','Level11','Level12','Level13','Count'])
    # final_df.to_csv(output_path+'//Datamart_output_real.csv', index=False, header=True)
    # with pd.ExcelWriter(output_path+'//Full_Datamart_Master.xlsx') as writer:
    #     final_df.to_excel(writer, sheet_name='Count', index=False, header=True)
        # pd.read_csv(output_path+'//Full_Datamart_Master.csv').to_excel(writer, sheet_name='Master', index=False, header=True)
    #     master_df.to_excel(writer, sheet_name='Master', index=False, header=True)


if __name__ == '__main__':
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    userid = form.getvalue('user_id')	
    test_name = form.getvalue('report_name')	
    # logtype = form.getvalue('logtype').split("\n")[0].strip()	
    # print(logtype)	
##    userid="44"	
##    test_name="datamartchk"	
    logtype="DATAMART"
    # file_path = "C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_Input\\Datamart_R_28042021_100k.csv"
    # column_names_file_path = "C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_Input\\Column_Details_output.csv"
    	
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\"+str(logtype)	
    file_path = dir_path + "\\*"
    column_names_file_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\DM column details\\*"
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name	
    # output_path = "C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DataMart_output\\"
    if not os.path.exists(output_path):	
        os.mkdir(output_path)
    try:
        datamart_df = generate_df(file_path)
        column_details_df = generate_df(column_names_file_path)
    except:
        print('Unsupported file format. Please check and upload again.')
    else:
        generate_dendo(datamart_df, column_details_df, output_path)
