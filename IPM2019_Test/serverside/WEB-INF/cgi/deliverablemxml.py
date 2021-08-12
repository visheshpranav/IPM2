import json
import xmltodict, os
import pandas as pd
import string,cgi, glob
import configparser, shutil
#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')

#INPUT_PATH="C:\\Users\\debjit.dhar\\Desktop\\DeliverablesMxml_15072020"
COL_LIST = ['Category', 'Level1','Delivarable Primary system','Trade Typology','Portfolio',
            'Flow type(Send or receive)','Flow amount','Trade Family','Trade Group',
            'Instrument','To be Netted','Flow currency',
            'Position Type(nostro or Vostro)','Counterparty name','FlowSettlementdate','FlowValueDate']
def getTypology(file):
    with open(file) as fd:
        doc = xmltodict.parse(fd.read())
        
    xml_dict=json.loads(json.dumps(doc))
    val_str1="MxML/deliverableFlows/deliverableFlow/businessObjectId/primarySystem"
    #print(val_str1.split("/"))
    copy_dict1=xml_dict
    val_str2="MxML/deliverableFlows/deliverableFlow/flowDetails/flowDetail/AccountKey/AccountKeyDetail/mxDeliverableAccountNostroCashIACCOUNT_KEY/userDefinedField"
    lst_str="mxDeliverableAccountNostroCashIACCOUNT_KEY_TradeTypology/businessObjectId/displayLabel"

    for v in val_str2.split("/"):
        copy_dict1=copy_dict1[v]

    typology=""
    
    for v in copy_dict1:
        if lst_str.split("/")[0] in v:
            typology=v[lst_str.split("/")[0]][lst_str.split("/")[1]][lst_str.split("/")[2]]
    
    return typology    

def getDeliverableValues(Del_DATA_PATH, output_path):
    with open('Deliver.json') as f:
        delv_data = json.load(f)
    usage_df = pd.DataFrame([],columns=COL_LIST)
    df_final_list=[]
    for file in os.listdir(Del_DATA_PATH):
        with open(Del_DATA_PATH+"\\"+file) as fd:
            doc = xmltodict.parse(fd.read())

        xml_str=json.dumps(doc).replace("null",'"NA"')
        xml_dict=json.loads(xml_str)
        copy_dict1=xml_dict
        cd1=xml_dict
        cd2=xml_dict
        col_list=[]
        sub_list=[]
        row_col_list = ['Category', 'Level1']
        row = ['murex']
        for v in delv_data["Extra"]["identifier"].split("/"):
            cd1=cd1[v]

        for v in delv_data["Fields"]["Trade Typology"].split("/"):
            cd2=cd2[v]
        row.append(cd2)
##        cd2=getTypology(INPUT_PATH+"\\"+file)
        for v1 in delv_data["Fields"].keys():
            for v2 in delv_data["Fields"][v1].split("/"):
                copy_dict1=copy_dict1[v2]
            row.append(copy_dict1)
            df_final_list.append([cd1, cd2, v1, copy_dict1])
            #print(v1, copy_dict1)
            copy_dict1=xml_dict
            col_list.append(v1)
            row_col_list.append(v1)
        row_series = pd. Series(row, index = row_col_list)
        usage_df = usage_df. append(row_series, ignore_index=True)
        #print(file)
        # print(df_final_list)
        # break
        #df_final_list.append(sub_list)
    usage_df.to_csv(output_path+"\\Del_master.csv", index=False)
    df = pd.DataFrame(df_final_list)
    del_masterfilename = "Final_Delivery.csv" 
    df.to_csv(del_masterfilename, index=False)    
    shutil.move(del_masterfilename, output_path+"/"+del_masterfilename)

    v_set=set()
    v_list=list()
    
    for v1 in df_final_list:
        val="murex"+"#"+v1[1]+"#"+v1[2]+"#"+v1[3]
        v_set.add(val)
        v_list.append(val)

    v_set_count=set()

    for v1 in v_set:
        cnt=v_list.count(v1)
        v_set_count.add(v1+"#"+str(cnt))
        
    df_count_list=[]

    for v in v_set_count:
        #print(v.split("#"))
        df_count_list.append(v.split("#"))

    df = pd.DataFrame(df_count_list, columns=['Category', 'Level1', 'Level2', 'Level3', 'Count'])
    del_Outfilename = "IMP036_Delivery.csv" 
    df.to_csv(del_Outfilename, index=False)    
    shutil.move(del_Outfilename, output_path+"/"+del_Outfilename)

    
if __name__=="__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    userid = form.getvalue('user_id')
    test_name = form.getvalue('report_name')
    logtype = form.getvalue('logtype').split("\n")[1].strip()
##    userid="44"
##    test_name="test14"
##    logtype="DeliverableMXML"    
    DATA_PATH = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\DeliverableMXML"
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    if not os.path.exists(output_path):
        os.mkdir(output_path)    
    getDeliverableValues(DATA_PATH,output_path)
