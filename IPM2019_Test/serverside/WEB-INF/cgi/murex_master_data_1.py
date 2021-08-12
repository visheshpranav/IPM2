import xml.etree.ElementTree as ET
import os, glob, shutil
import pandas as pd  
import configparser, shutil
#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')  

def master_data(output_path,master_path,contractid_dict,unique_queue):
    # path = 'C:\\Users\\p.babu.kumar\\Documents\\DeliverablesMxml_15072020\\DeliverablesMxml_15072020\\*.xml'
    file_path = master_path + "\\*.xml"
    files=glob.glob(file_path)   
    head=['tradeTypology','tradeFamily','flowAmount','tradeGroup','instrument',
     'toBeNetted','valueDate','flowCurrency','flowSendReceive',
     'settlementDate','portfolioLabel']
    col_list=['Contractid', 'tradeTypology','tradeFamily','flowAmount','tradeGroup','instrument',
     'toBeNetted','valueDate','flowCurrency','flowSendReceive',
     'settlementDate','portfolioLabel','tradeParty']
    # contractid_dict={'A': [800], 'B': [801, 813], 'C': [798], 'D': [794], 'E': [793], 'F': [790], 
    #         'G': [802], 'H': [804], 'I': [805], 'J': [810], 'K': [812], 'M': [806], 
    #         'N': [808], 'O': [809]}
    
    # unique_queue={'Type A': ['Initiate Settlement', 'Match Contracts With Confirmation Generated Outside of MX', 
    #                   'Monitor Next Days Netting', 'Net Before EOD', 'Validate Contract Non-Economic Exceptions',
    #                   'doc_settlementMsg_errorQueue', 'doc_settlementMsg_holdMsg'], 
    #         'Type B': ['Initiate Settlement', 
    #                   'Match Contracts With Confirmation Generated Outside of MX','Monitor Next Days Netting', 
    #                   'Monitoring of Trades', 'Net Before EOD', 'Validate Contract Non-Economic Exceptions',
    #                   'Validate Events']} 
    final_list=[]
    for file in files:  
        list1=[]
        list1.append(os.path.basename(file).split('_')[0])
        doc = ET.parse(file)
    
        root = doc.getroot()
        
        for val in head:
            for elem in root.iter(tag=val):
                list1.append(elem.text)
        for elem in root.iter(tag='tradeParty'):
            for i in list(elem):
                list1.append(i.text)
        final_list.append(list1)
    for val in final_list:
        key = [key for key,value in contractid_dict.items() if int(val[0]) in value]
        if key!=[]:
            val.insert(0,'Type '+key[0])
        else:
            val.insert(0,'-')
    main_df = pd.DataFrame(final_list)
    main_df.columns = ['Types','Contractid', 'tradeTypology','tradeFamily','flowAmount','tradeGroup','instrument',
     'toBeNetted','valueDate','flowCurrency','flowSendReceive',
     'settlementDate','portfolioLabel','tradeParty']
    df=main_df[main_df['Types']!='-']
    final_list=[]
    for val in unique_queue:
        df1 = df.loc[df['Types'] == val]
        for qname in unique_queue[val]:
            for index,row in df1.iterrows():
                list2=[]
                list2.append(val)
                list2.append(qname)
                for col in col_list:
                    list2.append(row[col])
            print(list2)
            final_list.append(list2)
           
    df = pd.DataFrame(final_list)
    df.columns = ['Types','QueueName','Contractid', 'tradeTypology','tradeFamily','flowAmount','tradeGroup','instrument',
     'toBeNetted','valueDate','flowCurrency','flowSendReceive',
     'settlementDate','portfolioLabel','tradeParty']
    df = df.drop_duplicates()
    return_df = df
    OSPMaster_Outfilename = "OSP_master1.csv" 
    df.to_csv(OSPMaster_Outfilename,index=False)
    shutil.move(OSPMaster_Outfilename, output_path+"/"+OSPMaster_Outfilename)
   
    df = main_df[main_df['Types']!='-']
    final_list=[]
    for val in unique_queue:
        df1 = df.loc[df['Types'] == val]
        for qname in unique_queue[val]:
            list2=[]
            for index,row in df1.iterrows():
                for col in col_list:
                    final_list.append([val,qname,col,row[col]])
                   
    df = pd.DataFrame(final_list)
    print(df)
    df.columns = ['Types','QueueName','Name','Value']
    dups=pd.DataFrame(df.groupby(df.columns.tolist(),as_index=True).size(),columns=['Count'])
    dups.reset_index(level= ['Types','QueueName','Name','Value'],inplace=True)
    output_list=[]
    for index,row in dups.iterrows():
        for val in output_list:
            if row['Types'] in val and row['QueueName'] in val and row['Name'] in val:
                val[3]=val[3]+';'+str(row['Value'])
                val[4]=val[4]+';'+str(row['Count'])
                break
               
        else:
            output_list.append([row['Types'],row['QueueName'],row['Name'],
                                str(row['Value']),str(row['Count'])])
  
    df = pd.DataFrame(output_list)
    df.columns = ['Types','QueueName','Name','Value','Count']
    OSPMaster_Outfilename = "OSP_master.csv" 
    df.to_csv(OSPMaster_Outfilename,index=False)
    shutil.move(OSPMaster_Outfilename, output_path+"/"+OSPMaster_Outfilename)
    output_list2=[]
    for types in df['Types'].unique():
        df1 = df[df['Types']==types]
        str1= df1['QueueName'].unique().tolist()
        output_list2.append([types,'QueueName',str1])
        for col in col_list:
            str2 = df1[df1['Name']==col]
            output_list2.append([types,col,str2['Value'].unique()[0]])
           
    df5 = pd.DataFrame(output_list2)
    df5.columns = ['Types','Name','Value']
    OSPMaster_type_Outfilename = "OSP_master_types.csv" 
    df5.to_csv(OSPMaster_type_Outfilename,index=False)
    shutil.move(OSPMaster_type_Outfilename, output_path+"/"+OSPMaster_type_Outfilename)
    return return_df

##    part1 = df[['Types','QueueName']]
##    part1.drop_duplicates(inplace=True)
##    part1.reset_index(drop=True, inplace=True)
##    # print(part1)
##    final_df = pd.DataFrame()
##    part2 = df[['Name', 'Value']]
##    sub_df = pd.DataFrame()
##    for i in range(int(len(part2)/13)):        
##        temp1 = part2[13*i:13*(i+1)]
##        temp1.set_index('Name',inplace=True)
##        temp1 = temp1.transpose().reset_index(drop=True)
##        sub_df = pd.concat([sub_df,temp1])
##    sub_df.reset_index(drop=True, inplace=True)
##    final_df = part1.merge(sub_df, left_index=True, right_index=True)
##    final_df1 = (final_df.set_index(['Types', 'QueueName'])
##   .stack()
##   .str.split(';', expand=True)
##   .stack()
##   .unstack(-2)
##   .reset_index(-1, drop=True)
##   .reset_index())
##    final_df1 = final_df.drop('flowAmount', axis=1) \
##        .join(final_df['flowAmount'] \
##        .str \
##        .split(';', expand=True) \
##        .stack() \
##        .reset_index(level=1, drop=True).rename('flowAmount')) \
##        .reset_index(drop=True)
##    OSPMaster_Finaloutfilename = "OSP_final_master.csv" 
##    final_df1.to_csv(OSPMaster_Finaloutfilename,index = False)
##    shutil.move(OSPMaster_Finaloutfilename, output_path+"/"+OSPMaster_Finaloutfilename)
    # df.to_csv('C:\\Users\\p.babu.kumar\\Desktop\\New folder\\output2.csv',index=False)
if __name__=='__main__':
    contractid_dict=dict()
    unique_queue=dict()
    master_data(contractid_dict,unique_queue)
