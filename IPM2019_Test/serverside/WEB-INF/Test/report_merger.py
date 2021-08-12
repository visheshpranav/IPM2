# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 09:29:39 2021

@author: v.a.subhash.krishna
"""
import pandas as pd
from murex_exceptions import *

def dict_gen(final_df, old_group_dict, new_group_dict, old_cols,add_rows):
    # print(old_group_dict)
    for key,val in old_group_dict.items():
        if key in new_group_dict:
            count = new_group_dict[key]['Count'].tolist()[0]
            count += val['Count'].tolist()[0]
            # print(type(key))
            if type(key) != str:
                dump_list = list(key)
            else:
                dump_list = [key]
                # print(dump_list)
            if add_rows:
                for i in range(add_rows):
                    dump_list.append('')
            dump_list.append(count)
            # print(dump_list)
            dump_df = pd.DataFrame([dump_list],columns=old_cols)
            new_group_dict.pop(key)
            final_df = final_df.append(dump_df)
        else:
            final_df = final_df.append(val)
    for key,val in new_group_dict.items():
        final_df = final_df.append(val)
    return final_df

def output_merger(file_list, new_report_path, old_report_path, log_type):
    for file in file_list:
        # print(file)
        try:
            old_df = pd.read_csv(old_report_path+'\\'+file,keep_default_na = False)
        except:
            raise GeneralException('Error occured while parsing. Data not found for previous report selected for merge. Please check and upload again.')
        new_df = pd.read_csv(new_report_path+'\\'+file,keep_default_na = False)
        final_df = pd.DataFrame(columns=list(new_df.columns))
        if 'master' not in file:
            # final_df = pd.DataFrame(columns=list(old_df.columns))
            # print(final_df)
            old_cols = list(old_df.columns)
            cols = old_cols[:-1]
            old_group = old_df.groupby(cols)
            new_group = new_df.groupby(cols)
            old_group_dict = dict()
            new_group_dict = dict()
            add_rows = 0
            for row in old_group:
                old_group_dict[row[0]] = row[1]
            for row in new_group:
                new_group_dict[row[0]] = row[1]
            final_df = dict_gen(final_df, old_group_dict, new_group_dict, old_cols,add_rows)
            if log_type == 'TradeInsertion' and 'IMP035' in file:
                old_cols = list(old_df.columns)
                cols = old_cols[:-2]
                old_group = old_df[old_df[old_cols[-2]].isnull()].groupby(cols)
                new_group = new_df[new_df[old_cols[-2]].isnull()].groupby(cols)
                old_group_dict = dict()
                new_group_dict = dict()
                for row in old_group:
                    old_group_dict[row[0]] = row[1]
                for row in new_group:
                    new_group_dict[row[0]] = row[1]
                add_rows = 1
                final_df = dict_gen(final_df, old_group_dict, new_group_dict, old_cols,add_rows)
                # print(old_df[old_df[old_cols[-2]]==''])
                # print(old_df)
            # print(old_group)
            
        else:
            final_df = new_df.append(old_df)
        final_df.to_csv(new_report_path+'\\'+file, index=False, header=True)
            

if __name__=="__main__":
    # file_list = ['IMP035_usage.csv','murex_master.csv','typology.csv']
    # log_type = 'Trade'
    # new_report_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\PattrnMing-Rabobnk_Output\\Output\\mxdev21_trade_xmls_set1'
    # old_report_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\PattrnMing-Rabobnk_Output\\Output\\mxdev21_trade_xmls_set2'
    file_list = ['IMP036_Delivery.csv','Del_master.csv','typology.csv']
    log_type = 'Delivirable'
    new_report_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DenDo_PythonCode\\set_1'
    old_report_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\DenDo_PythonCode\\set_2'
    
    output_merger(file_list, new_report_path, old_report_path, log_type)
