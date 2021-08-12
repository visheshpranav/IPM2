import pyodbc , configparser
import cgi, cgitb

#---------------------------------------------------------------------
query_dict = {"SELECT_BFC":'SELECT distinct businessflowname FROM lapam2019.bfc;'}

#---------------------------------------------------------------------

def tcode_generate():
    q_val=read_db(query_dict["SELECT_BFC"])
    bfc_list = [item[0] for item in q_val]
    return bfc_list

    
def db_connect():
    parser = configparser.ConfigParser() 
    parser.read("C:\\LAPAM2019\\Config\\configfile.config")
    DSN_NAMEE = parser.get('DSN','DSN_NAMEE')
 
    mySQLconnection = pyodbc.connect("DSN="+DSN_NAMEE)
    return mySQLconnection
    
def read_db(query):
    conn=db_connect()
    cursor=conn.cursor()
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    
    return records
 
#-------------------------------------------------------------------------------------------------------------

# Driver program

if __name__ == "__main__":
    form = cgi.FieldStorage()
    print("Content-type: text/html \n");
    tcode_list = tcode_generate()
    print(tcode_list)
	
