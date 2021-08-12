import pyodbc , configparser
import cgi, cgitb
from elasticsearch import Elasticsearch


parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
STAD_INDEX_NAME = parser.get('Upload','STAD_INDEX_NAME')


##if not os.path.exists(dir_path):
##    os.mkdir(dir_path)

##q_val=es = es.search(index=index_name, body={"aggs": {"distinct_tcode": {"terms": {"field": "tcode","size": 1000}}}})
##---------------------------------------------------------------------
##query_dict = {"SELECT_TCODE":'SELECT distinct substring_index(ENTRY_ID,"  ",1) as tcode FROM lapam2019.tcount;'}

#---------------------------------------------------------------------

def tcode_generate(user_id):
    tcode_list=[]
    es = Elasticsearch('localhost', port=9200)

    
    q_val=es.search(index=STAD_INDEX_NAME, body={"query":{"bool":{"must":[{"wildcard":{"LOG_NAME":user_id+"*"}}]}},"aggs": {"distinct_tcode": {"terms": {"field": "TRANSACTION_OR_JOBNAME.keyword", "size":9999999}}}})
    for val in q_val['aggregations']['distinct_tcode']['buckets']:
        tcode_list.append(val['key'])
##    q_val=read_db(query_dict["SELECT_TCODE"])
##    tcode_list = [item[0] for item in q_val]
    tcode_list.sort()
    return tcode_list

    
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
    cursor
    return records
 
#-------------------------------------------------------------------------------------------------------------

# Driver program

if __name__ == "__main__":
    form = cgi.FieldStorage()
    print("Content-type: text/html \n");
    user_id = form.getvalue('user_id').strip()
##    user_id  ="42"
    tcode_list = tcode_generate(user_id)
    print(tcode_list)
	
