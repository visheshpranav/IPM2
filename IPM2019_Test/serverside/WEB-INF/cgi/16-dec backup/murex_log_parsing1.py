import xml.etree.ElementTree as ET
import itertools
import glob, json, copy
import pandas as pd
from datetime import datetime
import os, cgi, configparser, shutil

#fetch the upload path from config	
parser = configparser.ConfigParser() 	
parser.read("C:\\LAPAM2019\\Config\\configfile.config")	
DATA_PATH = parser.get('Upload','Oflpath')

def recursive_csv_list(xml_file_path, csv_list, status_count):
    filename_count={}
    patterns = json.load(open('C:\\LAPAM2019\\Config\\patterns.json'))
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    root_tag = root.tag.split('}')[-1]
    parent_map = [[p,c] for p in root.iter() for c in p]
    for child in root.findall('.//tradeFamily'):
        tag_array = []
        tag_list = ['Trade']
        tag_list.append(child.text)
        parent = [val[0] for val in parent_map if val[1] == child][0]
        tag_list.append(parent.findall('.//tradeGroup')[0].text)
        typology = parent.findall('.//typology')[0].text
        tag_list.append(typology)
        tag_list_1 = copy.deepcopy(tag_list)
        pattern_keys = [val.replace('_',' ') for val in patterns.keys()]
        for val in patterns['events']:
            obj_list = root.findall(patterns['events'][val])
            for obj in obj_list:
                tag_list_1.append('Events')
                tag_list_1.append(obj.tag)
                tag_set = tag_list_1
                tag_list_1.append(val)
                if str(tag_set) not in status_count:
                    status_count[str(tag_set)] = 0
                status_count[str(tag_set)] += 1
               
                tag_array.append(tag_list_1)
                tag_list_1 = copy.deepcopy(tag_list)
##            print(root.findall(val))
            
        for val in patterns['common_tags']:
            obj_list = root.findall(val)
            for obj in obj_list:
                tag_list_1.append('Trade Characteristics')
                tag_list_1.append(obj.tag)
                tag_set = tag_list_1
                tag_list_1.append(obj.text)
                if str(tag_set) not in status_count:
                    status_count[str(tag_set)] = 0
                status_count[str(tag_set)] += 1
                tag_array.append(tag_list_1)
                tag_list_1 = copy.deepcopy(tag_list)
                break
            
        if typology in pattern_keys:
            key = typology.replace(' ','_')
        else:
            csv_list = csv_list + tag_array
            continue
        for val in patterns[key]:
            obj_list = root.findall(val)
            for obj in obj_list:
                tag_list_1.append('Trade Characteristics')
                if obj.tag == 'maturity':
                    tag_list_1.append('Maturity Status')
                    maturity_date = datetime.strptime(obj.text,'%Y%m%d')
                    present_date = datetime.now()
                    difference = maturity_date - present_date
                    difference = int(difference.days/365)
                    if difference < 1:
                        tag_list_1.append('Short term')
                        # tag_list_1.append('physicalStatus')
                        
                    elif difference > 1 and difference <= 5:
                        tag_list_1.append('Medium term')
                        # tag_list_1.append('physicalStatus')
                        
                    else:
                        tag_list_1.append('Long term')
                        # tag_list_1.append('physicalStatus')
                        
                
                else:
                    tag_list_1.append(obj.tag)    
                    tag_list_1.append(obj.text)
                tag_set = tag_list_1
                if str(tag_set) not in status_count:
                    status_count[str(tag_set)] = 0
                status_count[str(tag_set)] += 1
                tag_array.append(tag_list_1)
                tag_list_1 = copy.deepcopy(tag_list)
                break
        csv_list = csv_list + tag_array
            
    csv_list.sort()
    csv_list = list(csv_list for csv_list,_ in itertools.groupby(csv_list))
    
    return csv_list, status_count

    
def df_gen(status_count,output_path):
    
    final_df = pd.DataFrame(columns = ['Category','Level1','Level2','Level3','Level4',
                                       'lastContractEventReference','partyName',
                                       'physicalStatus','portfolioLabel','tradeDestination',
                                       'Maturity Status','initialCapitalAmount','templateLabel',
                                       'expiryDate','futureDisplayLabel','nominalAmount','currency'])
    
    # result_df=pd.DataFrame()
##    print(status_count)
    for val in status_count:
        temp_df = pd.DataFrame(columns = ['Category','Level1','Level2','Level3','Level4',
                                          'lastContractEventReference','partyName','physicalStatus',
                                          'portfolioLabel','tradeDestination','Maturity Status',
                                          'initialCapitalAmount','templateLabel','expiryDate',
                                          'futureDisplayLabel','nominalAmount','currency'])
        main_list = val[:5]
        df1 = final_df.loc[final_df['Category'] == main_list[0]]
        df1 = df1.loc[df1['Level1'] == main_list[1]]
        df1 = df1.loc[df1['Level2'] == main_list[2]]
        df1 = df1.loc[df1['Level3'] == main_list[3]]
        df1 = df1.loc[df1['Level4'] == main_list[4]]
        if not len(df1):
            cors_values = [val1 for val1 in status_count if val1[:5] == main_list]
            completed_columns = {}
            column_count = {}
            for val1 in cors_values:
                if val1[5] not in completed_columns:
                    completed_columns[val1[5]] = {}
                    column_count[val1[5]] = 0
                completed_columns[val1[5]][val1[6]] = val1[7]
                column_count[val1[5]] += val1[7]
            max_val = 0
            max_key = ''
            for key,value in column_count.items():
                if value > max_val:
                    max_val = value
                    max_key = key
            
            # print(completed_columns)
            # print(column_count)
            for col_val in completed_columns[max_key]:
                new_row={'Category':val[0],'Level1':val[1],'Level2':val[2],'Level3':val[3],'Level4':val[4],max_key:col_val}
                for i in range(completed_columns[max_key][col_val]):
                    temp_df=temp_df.append(new_row,ignore_index=True)
            completed_columns.pop(max_key)
##            print(completed_columns)
            for col_name in completed_columns:
                counter = 0
                for col_val in completed_columns[col_name]:
                    if len(temp_df) == 1:
                        temp_df[col_name] = col_val
##                        print(temp_df[col_name])
                    else:
                        temp_df[counter:completed_columns[col_name][col_val]][col_name] = col_val
                        counter += completed_columns[col_name][col_val]

            final_df=final_df.append(temp_df,ignore_index=True)
            print(final_df)
    filename = 'murex_master.csv'
    final_df.to_csv(filename, index=False)
    shutil.move(filename, output_path+"/"+filename)

if __name__ == '__main__':	
    print("Content-type: text/html \n");	
    form = cgi.FieldStorage()	
    userid = form.getvalue('user_id')	
    test_name = form.getvalue('report_name')	
    logtype = form.getvalue('logtype').split("\n")[0].strip()	
    print(logtype)	
##    userid="44"	
##    test_name="nov10_12"	
##    logtype="Trade"	
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\"+str(logtype)	
    file_path = dir_path + "\\*.xml"	
    print(file_path)	
    files = glob.glob(file_path)	
##    print(files)	
    val = 0	
    csv_list = []	
    status_count = {}	
    for file in files:
        csv_list,status_count = recursive_csv_list(file, csv_list, status_count)		
    for val in csv_list:	
        if str(val) in status_count:	
            val.append(status_count[str(val)])	
        else:	
            val.append('0')	
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name	
    if not os.path.exists(output_path):	
        os.mkdir(output_path)		
    df_gen(csv_list, output_path)
    my_df_new = pd.DataFrame(csv_list, columns = ['Category','Level1','Level2','Level3','Level4','Level5','Level6','Count'])	
    filename = 'IMP035_usage.csv'	
    my_df_new.to_csv(filename, index=False, header=True)
    shutil.move(filename, output_path+"/"+filename)
    shutil.copy(output_path+"/"+filename, output_path+"/TradeInsertionEvents.csv")
