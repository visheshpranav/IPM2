#######################################################################
#Application : CBOL
#Build : v3
#Desc: Get the TestName form DB for dropdown
#Created by : Manohar
#Date of Modification:8/9/2018
########################################################################

import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc
import configparser
import cgi, os
import pathlib

parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAME = parser.get('DSN','DSN_NAMEE')

form = cgi.FieldStorage()
user_name = form.getvalue("user_name").strip()
type = form.getvalue("type").strip()
##user_name = "Murex"
#fetch test values from quaifier table
def get_values(con,user_name):
        query = 'SELECT CAST(`USER_ID` as CHAR(11)) as USER_ID,`REP_Name`,`DATE`, `Source_File` FROM report_info WHERE\
        `USER_ID` = (select distinct(`USER_ID`) from user_info where `USER_NAME` = "'+str(user_name)+'") order by DATE asc;'
        con.execute(query)
        res = con.fetchall()
        return res	

        z= str(username)
        #z.split('\'')[3]
        j= z.split('\'')[4].replace('datetime.date(', '')
        f = j.replace(',', '/')
        t = f.replace(')', '')
##        print(z.split('\'')[3],",",t[1:].strip())
        
#database connection
def create_connection(user_name):
	db1 = pyodbc.connect("DSN="+DSN_NAME)
	cur = db1.cursor()
	ret = get_values(cur,user_name)
	return ret	

print ("Content-type: text/html \n\n");
ret = create_connection(user_name)
##print(ret)
for username in ret:
        
        #print(str(username).split('\'')[1]+","+str(username).split('\'')[3])
        k=str(username).split('\'')[3]
        #print(k)
        output_path1 = "C:/LAPAM2019/DataLake/Cache/44/"+k+"/TradeInsertion"
        output_path2 = "C:/LAPAM2019/DataLake/Cache/44/"+k+"/DeliverableMXML"
        output_path3 = "C:/LAPAM2019/DataLake/Cache/44/"+k+"/OSP"
        output_path4 = "C:/LAPAM2019/DataLake/Cache/44/"+k+"/DATAMART"
        #print(output_path)
        
        z= str(username)
        #z.split('\'')[3]
        j= z.split('\'')[4].replace('datetime.date(', '')
        f = j.replace(',', '/')
        t = f.replace(')', '')
        if os.path.exists(output_path1) and os.path.exists(output_path2) and os.path.exists(output_path3):
##            src1="NA"
##            src2="NA"
##            src3=os.listdir(output_path3+"/")
##            src3=listToString(src3)
            if z.split(',')[5].strip() == "None)":
                    op= z.split(',')[5] = "NA"
            else:
                    op= z.split(',')[5] 
            print(z.split('\'')[3],",","DeliverableMXML/TradeInsertion/OSP",",",t[1:13].strip(),",",user_name,",",op,",","NA")
        elif os.path.exists(output_path1) and os.path.exists(output_path2):
            src1="NA"
            src2="NA"
            if z.split(',')[5].strip() == "None)":
                    op= z.split(',')[5] = "NA"
            else:
                    op= z.split(',')[5] 
            print(z.split('\'')[3],",","DeliverableMXML/TradeInsertion",",",t[1:13].strip(),",",user_name,",",op,",","NA")
        elif os.path.exists(output_path1) and os.path.exists(output_path3):
##            src1="NA"
##            src3=os.listdir(output_path3+"/")
##            src3=listToString(src3)
            if z.split(',')[5].strip() == "None)":
                    op= z.split(',')[5] = "NA"
            else:
                    op= z.split(',')[5] 
            print(z.split('\'')[3],",","OSP/TradeInsertion",",",t[1:13].strip(),",",user_name,",",op,",","NA")
        elif os.path.exists(output_path2) and os.path.exists(output_path3):
##            src2="NA"
##            src3=os.listdir(output_path3+"/")
##            src3=listToString(src3)
            if z.split(',')[5].strip() == "None)":
                    op= z.split(',')[5] = "NA"
            else:
                    op= z.split(',')[5] 
            print(z.split('\'')[3],",","DeliverableMXML/OSP",",",t[1:13].strip(),",",user_name,",",op,",","NA")
        elif os.path.exists(output_path1):
            src1="NA"
            if z.split(',')[5].strip() == "None)":
                    op= z.split(',')[5] = "NA"
            else:
                    if len(z.split(',')) == 6:
                            op= z.split(',')[5]
                    elif len(z.split(',')) == 7:
                            op= z.split(',')[5]+"/"+z.split(',')[6]
                            
                    elif len(z.split(',')) == 8:
                            op= z.split(',')[5]+"/"+z.split(',')[6]+"/"+z.split(',')[7]
                            
                    elif len(z.split(',')) == 9:
                            op= z.split(',')[5]+"/"+z.split(',')[6]+"/"+z.split(',')[7]+"/"+z.split(',')[8]
                            
                    elif len(z.split(',')) == 10:
                            op= z.split(',')[5]+"/"+z.split(',')[6]+"/"+z.split(',')[7]+"/"+z.split(',')[8]+"/"+z.split(',')[9]
                            
                    elif len(z.split(',')) == 11:
                            op= z.split(',')[5]+"/"+z.split(',')[6]+"/"+z.split(',')[7]+"/"+z.split(',')[8]+"/"+z.split(',')[9]+"/"+z.split(',')[10]
                    elif len(z.split(',')) == 12:
                            op= z.split(',')[5]+"/"+z.split(',')[6]+"/"+z.split(',')[7]+"/"+z.split(',')[8]+"/"+z.split(',')[9]+"/"+z.split(',')[10]+"/"+z.split(',')[11]
                    elif len(z.split(',')) == 13:
                            op= z.split(',')[5]+"/"+z.split(',')[6]+"/"+z.split(',')[7]+"/"+z.split(',')[8]+"/"+z.split(',')[9]+"/"+z.split(',')[10]+"/"+z.split(',')[11]+"/"+z.split(',')[12]
            filestatus = pathlib.Path("C:/LAPAM2019/DataLake/Cache/44/"+k+"/Status.txt")
            if filestatus.exists ():
                    f = open("C:/LAPAM2019/DataLake/Cache/44/"+k+"/Status.txt", "r")
                    status=f.read()
            else:
                    status="NA"
            print(z.split('\'')[3],",","TradeInsertion",",",t[1:13].strip(),",",user_name,",",op,",",status)                
        
                            
                     
##            print(z.split('\'')[3],",","TradeInsertion",",",t[1:13].strip(),",",user_name,",",op,",","NA")
        elif os.path.exists(output_path2):
            src2="NA"
            if z.split(',')[5].strip() == "None)":
                    op= z.split(',')[5] = "NA"
            else:
                    op= z.split(',')[5] 
            print(z.split('\'')[3],",","DeliverableMXML",",",t[1:13].strip(),",",user_name,",",op,",","NA")
        elif os.path.exists(output_path3):
##            src3=os.listdir(output_path3+"/")
##            src3=listToString(src3)
            if z.split(',')[5].strip() == "None)":
                    op= z.split(',')[5] = "NA"
            else:
                    op= z.split(',')[5] 
            print(z.split('\'')[3],",","OSP",",",t[1:13].strip(),",",user_name,",",op,",","NA")
        elif os.path.exists(output_path4):
##                    src4=os.listdir(output_path4+"/DATAMART/")
##                    src4=listToString(src4)
##                    src5=os.listdir(output_path4+"/DM column details/")
##                    src5=listToString(src5)
            if z.split(',')[5].strip() == "None)":
                    op= z.split(',')[5] = "NA"
            else:
                    op= z.split(',')[5] 
            print(z.split('\'')[3],",","DATAMART",",",t[1:13].strip(),",",user_name,",",op,",","NA")
            
    

	
	
