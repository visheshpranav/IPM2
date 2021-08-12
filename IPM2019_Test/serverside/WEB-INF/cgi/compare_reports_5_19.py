# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 10:51:10 2021

@author: v.a.subhash.krishna
"""

import os, cgi, configparser
import json
import pandas as pd
from murex_log_parsing import generate_dendo
from murex_exceptions import GeneralException
# from murex_trade_log import generate_dendo
# from compare_reports_dendo import compare_reports_dendo

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
TEMPLATE_PATH = parser.get('Upload','templatepath2')


def compare_reports_master(base_master_df,compare_master_df,cols,event_values):
    result_df = pd.DataFrame(columns=base_master_df.columns)
    base_groupby_df = base_master_df.groupby(cols)
    missing_cols = [val for val in cols if val not in compare_master_df.columns]
##    print(missing_cols)
    for column in missing_cols:
        compare_master_df[column] = ''
##    base_list = list(dict(base_groupby_df.groups).keys())
##    print(type(base_list))
##    print(base_list)
    compare_groupby_df = compare_master_df.groupby(cols)
    compare_list = list(dict(compare_groupby_df.groups).keys())
    for b_row in base_groupby_df:
        if b_row[0] not in compare_list:
            if event_values:
                flag = [val for val in event_values if val in b_row[0]]
                if not len(flag):
                    continue
##            print(b_row[0])
            result_df = result_df.append(b_row[1])
##    for b_row in base_groupby_df:
##        flag = 1
##        for c_row in compare_groupby_df:
####            print(b_row[0],c_row[0])
##            if b_row[0] == c_row[0]:
##                # print(c_row[0])
##                flag = 0
##                break
##        if flag:
##            # print('entered')
##            result_df = result_df.append(b_row[1])
    return result_df

if __name__ == '__main__':
    print("Content-type: text/html \n");
    try:
        form = cgi.FieldStorage()	
        userid = form.getvalue('user_id')
        log_type = form.getvalue('log_type')
        template_name = form.getvalue('template_name')
        base_name = form.getvalue('base_report')
        compare_name = form.getvalue('compare_report')
        comparison_reportname = form.getvalue('comparison_reportname')
    
##        userid = "44"
##        log_type = "TradeInsertion"
##        template_name = "TRD_UAT_TEST1"
##        base_name = "PROD1"
##        compare_name = "REG1"
##        comparison_reportname = "COMP_PR1"
    
        base_folder_name = userid+"_"+base_name
        compare_folder_name = userid+"_"+compare_name
        output_folder_name = userid+"_"+comparison_reportname
        template_path = TEMPLATE_PATH + '\\' + userid + '\\' + log_type
        event_values = []
        # template_name = 'sample'
        # template_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\template\\'
        # template_json = json.load(open(template_path+'\\'+template_name+'.json'))
        if template_name:
            template_json = json.load(open(template_path+'\\'+template_name+'.json'))
            cols = []
            for key,val in template_json.items():
                if key == 'events':
                    event_values = list(val.keys())
                    cols.append('lastContractEventReference')
                else:
                    header_list = list(val.keys())
                    cols.extend(header_list)
        else:
            template_json = dict()
            patterns_path = 'C:\\LAPAM2019\\Config\\'+str(userid)+'_patterns.json'
            if not os.path.exists(patterns_path):
                patterns_path = 'C:\\LAPAM2019\\Config\\patterns.json'
            # patterns_path = 'C:\\Users\\v.a.subhash.krishna\\Downloads\\murex_log_parsing\\patterns.json'
            template_json = json.load(open(patterns_path))
            cols = template_json['Dendo_list']
            template_json.pop('internalId')
            template_json.pop('Contract Id')
            template_json.pop('Dendo_list')
            template_json.pop('events')
            template_json.pop('lastContractEventReference')
            cols.remove('Trade Characteristics')
            # cols.remove('lastContractEventReference')
            cols.remove('tradeInternalId')
            # for key,value in patterns_json.items():
            #     if len(key.split('_'))>1:
            #         updated_key = ' '.join(key.split('_'))
            #     else:
            #         updated_key = key
            #     template_json[updated_key] = value
            template_json['Common Tags'] = template_json['common_tags']
            template_json.pop('common_tags')
        base_path = "../../../WEB-INF/classes/static/html/Reports/"+base_folder_name
        compare_path = "../../../WEB-INF/classes/static/html/Reports/"+compare_folder_name
        compare_output_path = "../../../WEB-INF/classes/static/html/Reports/"+output_folder_name
        if not os.path.exists(compare_output_path):
            os.mkdir(compare_output_path)
        # base_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\PattrnMing-Rabobnk_Output\\Output\\mxdev21_trade_xmls_set1'
        # compare_path = 'C:\\Users\\v.a.subhash.krishna\\Desktop\\Deliverable\\PattrnMing-Rabobnk_Output\\Output\\mxdev21_trade_xmls_set2'
        # compare_output_path = template_path
        try:
            base_master_df = pd.read_csv(base_path+'/murex_master.csv',keep_default_na = False)
        except:
            raise GeneralException('Error occured while reading base report details. Base report details not found.')
        try:
            compare_master_df = pd.read_csv(compare_path+'/murex_master.csv',keep_default_na = False)
        except:
            raise GeneralException('Error occured while reading compare report details. Compare report details not found.')
        base_master_df.fillna('', inplace=True)
        compare_master_df.fillna('', inplace=True)
    ##    missing_cols = [val for val in cols if val not in base_master_df.columns]
        cols = [val for val in cols if val in base_master_df.columns]
        if not cols:
            raise GeneralException('Template does not exist in base report. Please try again with appropriate values.')
##        print(cols)
    ##    print(len(compare_master_df))
        result_df = compare_reports_master(base_master_df,compare_master_df,cols,event_values)
        if result_df.empty:
            raise GeneralException('Base Report and Compare Report are identical.')
        cols.extend(['Category','tradeFamily','tradeGroup','tradeType','Trade Characteristics','Contract Id','tradeInternalId'])
        cols = list(set(cols))
        generate_dendo(result_df,compare_output_path,cols,comparison_reportname,'Compare')
        result_df.to_csv(compare_output_path+'/murex_master.csv', index=False, header=True)
        # print(len(result_df))
    except GeneralException as e:
        print(e)
    except Exception as e:
        print('Error occured while Comparing. Please contact Administrator.')
        print(e)
