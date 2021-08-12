import pandas as pd 
from datetime import datetime
from murex_master_data import *
import string,cgi, glob
import configparser, shutil
#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DATA_PATH = parser.get('Upload','Oflpath')

def get_dict(file_path):
    data = pd.read_csv(file_path)
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
    print("RAW", subset_dict)
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
    df.columns = ["OSP_QUEUE_NAME", "TYPOLOGY", "FROM_TASK", "TO_TASK", "Type", "Count"]
    df = df[[ "Type", "TYPOLOGY", "OSP_QUEUE_NAME", "FROM_TASK", "TO_TASK", "Count"]]
    df.rename(columns={"Type":'Category', "TYPOLOGY":'Level1', "OSP_QUEUE_NAME":"Level2", "FROM_TASK":'Level3', "TO_TASK":"Level4"}, inplace=True)

    return df

def change_col_name(df):
    unq_cat_list=df.Category.unique()
    alpha_list=list(string.ascii_uppercase)
    
    c=0
    cat_change_dict=dict()
    
    for i in range(0,len(unq_cat_list)):
        cat_change_dict[unq_cat_list[i]]= alpha_list[i]

    df['Category']=df['Category'].apply(lambda x: "Type "+cat_change_dict[x])
   
    return df,cat_change_dict

def groupby_all_typology(df):
    unique_type=list(df['Category'].unique())
    grouped_type=dict()
    temp1=list(unique_type)
    for val in unique_type:
        temp1.remove(val)
        sub_df1=df.loc[df['Category']==val,["Level2","Level3","Level4"]]
        sub_df1.reset_index(drop=True, inplace=True)
        len_df1=len(sub_df1)
        for val2 in temp1:
            sub_df2=df.loc[df['Category']==val2,['Level2','Level3','Level4']]
            sub_df2.reset_index(drop=True, inplace=True)
            len_df2=len(sub_df2)
            if len_df1<len_df2:
                if sub_df1[:len_df1].equals(sub_df2[:len_df1]):
                    print("equals",val+" == "+val2)
                    grouped_type[val]=[]
                    grouped_type[val].append(val2)
            else:
                if sub_df1[:len_df2].equals(sub_df2[:len_df2]):
                    print("equals",val+" == "+val2)
                    grouped_type[val]=[]
                    grouped_type[val].append(val2)
                      
    print(grouped_type)
    for key,value in grouped_type.items():
        print(key,value)
        for val in value:
            df["Category"].replace({val:key}, inplace=True)
    df.rename(columns={'Category':'Level2','Level2':'Level3','Level3':'Level4','Level4':'Level5'}, inplace=True)
    df['Category']='murex'
    df=df[['Category','Level1','Level2','Level3','Level4','Level5','Count']]
    return df,grouped_type
                
        

if __name__=="__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    userid = form.getvalue('user_id')
    test_name = form.getvalue('report_name')
    logtype = form.getvalue('logtype').split("\n")[1].strip()
##    userid="44"
##    test_name="testospp"
##    logtype="OSP"
    xlsx_filename='OSP_Master.xlsx'                      #Excel Filename
    writer = pd.ExcelWriter(xlsx_filename, engine='xlsxwriter') # Excel writer declaration
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\"+str(logtype)
    master_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\DeliverableMXML"
    file_path = dir_path + "\\*.csv"
    files = glob.glob(file_path)
    for file in files:
        c_dict=get_dict(file)
    #c_dict=get_dict()
    subset_dict, same_list3=get_contact(c_dict)
    print("Subset",subset_dict)
    print("Processed:",subset_dict)
    type_count_dict=get_count(c_dict, subset_dict, same_list3)
    df=get_df(type_count_dict)
    df,cat_change_dict = change_col_name(df)
    contractid_dict=dict()
    for key,val in cat_change_dict.items():
        contractid_dict[val]=[]
        contractid_dict[val].append(key)
        
    # df.to_csv("def.csv", index=False)
    df,grouped_type =groupby_all_typology(df)
    OSP_Outfilename = "OSP_Out.csv"    
    folder_name=userid+"_"+test_name
    output_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_name
    if not os.path.exists(output_path):
        os.mkdir(output_path)    
    df.to_csv(OSP_Outfilename, index=False)
    shutil.move(OSP_Outfilename, output_path+"/"+OSP_Outfilename)
    


    for key,val in grouped_type.items():
        for val1 in val:
            contractid_dict[key.split(" ")[1]].extend(contractid_dict[val1.split(" ")[1]])
            del contractid_dict[val1.split(" ")[1]]
    unique_queue=dict()
    for val in df['Level2'].unique():
        df1 = df.loc[df['Level2']==val]
        unique_queue[val]=df1['Level3'].unique().tolist()
    print(unique_queue)
    df.rename(columns={'Level1':'Trade Typology','Level2':'Type','Level3':'OSP Queue name','Level4':'From Task','Level5':'To Task'}, inplace=True)
    df = df.drop(columns='Category')
    df.to_excel(writer,sheet_name='Count',index=False)  #convert to Excel sheet
    
    df2 = master_data(output_path,master_path,contractid_dict,unique_queue)
    df2.to_excel(writer,sheet_name='Master',index=False)  #convert to Excel sheet
    writer.save()
    shutil.move(xlsx_filename, output_path+"/"+xlsx_filename)  #moving excel sheet to output_path
    
    # df.to_csv("def2.csv", index=False)
    # df.rename(columns={'Category':'Project','Level1':'Typology','Level2':'Types','Level3':'Queue name','Level4':'From task','Level5':'To task','Failures':'Count'}, inplace=True)
    # df.to_csv("QueueTraversalFlow.csv ", index=False)
