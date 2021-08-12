import xml.etree.ElementTree as ET
import os, glob, shutil
import pandas as pd  
import configparser, shutil
#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')  

def master_data(output_path,master_path,contractid_dict,unique_queue):
    #path = 'C:\\Users\\p.babu.kumar\\Documents\\DeliverablesMxml_15072020\\DeliverablesMxml_15072020\\*.xml'
    file_path = master_path + "\\*.xml"
    print(file_path)
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
            
    df = pd.DataFrame(final_list)
    df.columns = ['Types','Contractid', 'tradeTypology','tradeFamily','flowAmount','tradeGroup','instrument',
     'toBeNetted','valueDate','flowCurrency','flowSendReceive',
     'settlementDate','portfolioLabel','tradeParty']
    #OSPMaster_Outfilename = "OSP_master.csv" 
    
    df=df[df['Types']!='-']
    final_list=[]
    for val in unique_queue:
        df1 = df.loc[df['Types'] == val]
        for qname in unique_queue[val]:
            list2=[]
            for index,row in df1.iterrows():
                for col in col_list:
                    final_list.append([val,qname,col,row[col]])
    
    df = pd.DataFrame(final_list)
    #print(df)
    #df.to_csv(OSPMaster_Outfilename,index=False)
    #shutil.move(OSPMaster_Outfilename, output_path+"/"+OSPMaster_Outfilename)
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
    df.to_excel(OSPMaster_Outfilename,index=False)
    shutil.move(OSPMaster_Outfilename, output_path+"/"+OSPMaster_Outfilename)
    # df.to_csv('C:\\Users\\p.babu.kumar\\Desktop\\New folder\\output2.csv',index=False)
if __name__=='__main__':
    contractid_dict=dict()
    unique_queue=dict()
    master_data(contractid_dict,unique_queue)
