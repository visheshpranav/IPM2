#######################################################################
#Application : LAPAM
#Build : 2019
#Desc: Update user datatable fields
#Modified by: Rajkumar
#Date of Modification:5/2/2019
########################################################################
import cgi, cgitb 
import cgitb; cgitb.enable()
import pyodbc
import configparser

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
IKEA_DATA_PATH = parser.get('Upload','ikea')
 
''' database connection '''
def fetch_imp(matched_patterns, userid, report_name,mode,appName,logtype_val):
        if mode == "OFL":
                con = pyodbc.connect("DSN="+DSN_NAMEE)
                cur = con.cursor()
                query = 'SELECT imp_id, pat_list, OUTPUT, LOGIC from App_Imperative_Pattern_Info;'
                response_arr = con.execute(query).fetchall()
                matched_pat_list = matched_patterns[0].split(',')
        ##        matched_pat_list = list(matched_pat_list.sort())
                imp_ids = []
                for impid, pattern, outcome, logic in response_arr:
                    #if isPatternExist(pattern, matched_patterns):
                    imp_pat_list = pattern.split(',')
                    if(set(imp_pat_list).issubset(matched_pat_list)):
                        rep_id = insert_ImpDetails(impid, userid, report_name,pattern,outcome, logic,logtype_val)
                        query1 = 'SELECT IMP_DESCRIPTION from imperative_info where IMP_ID = "'+impid+'";'
                        imp_name = con.execute(query1).fetchone()[0]
                        imp_ids.append(impid+"-"+imp_name)
        elif mode == "ONL":
                con = pyodbc.connect("DSN="+DSN_NAMEE)
                cur = con.cursor()
                query = 'SELECT Imp_Id from Online_Imperative_Info where App_Name = "'+appName+'";'
                response_arr = con.execute(query).fetchall()
##                matched_pat_list = response_arr[0].split(',')
                imp_ids = []
                for impid in response_arr:
                        query1 = 'SELECT IMP_DESCRIPTION from imperative_info where IMP_ID = "'+impid[0]+'";'
                        imp_name = con.execute(query1).fetchone()[0]
                        imp_ids.append(str(impid[0])+"-"+imp_name) 
        ##        matched_pat_list = list(matched_pat_list.sort())
##                print(imp_ids)
        return imp_ids

#insert upload details into log_info table
def insert_ImpDetails(impid, userid, report_name,pattern,outcome, logic,logtype_val):
    db1 = pyodbc.connect("DSN="+DSN_NAMEE)
    cursor = db1.cursor()
    report_query = 'SELECT rep_id FROM report_info where user_id='+userid+' and rep_name ="'+report_name+'";'
    print(report_query)
    rep_id= cursor.execute(report_query).fetchone()[0]
    print(rep_id)
    query = """INSERT INTO report_imperatives_patterns (`USER_ID`, `REP_ID`, `IMP_ID`, `PAT_LIST`, `LOG_TYPE`, `OUTPUT`, `LOGIC`)
                VALUES (%s,%s,'%s','%s','%s','%s','%s');"""
    print(query)
    cursor.execute(query %(userid,rep_id,impid,pattern,logtype_val,outcome, logic))
    db1.commit()
    return rep_id
    
#main function
if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    #matched_patterns = form.getvalue("matched_patterns")
    matched_patterns = ""
    userid = ""
    report_name = ""
    mode = "ONL"
    appName = "TWA"
    fetch_imp(matched_patterns, userid, report_name,mode,appName)
