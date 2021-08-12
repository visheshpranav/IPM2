import os
import cgi, configparser

parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")

def store_json(fileitem,userid,test_name):
    Log_Name = str(userid) +"_"+test_name
    dir_path = "../../../WEB-INF/classes/static/html/Reports/"+Log_Name
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    fn = os.path.basename(fileitem.filename)
    if fn:        
        if fn.endswith(".json"):
            g = open(dir_path + "\\IMP030.json", 'wb').write(fileitem.file.read())

if __name__=='__main__':
    form = cgi.FieldStorage()
    json_fileitems = form['Dlg_jsonfilename'] 
    userid = form.getvalue('userid').strip()
    test_name = form.getvalue('reportname').lower()
    print ("Content-type: text/html \n")
    store_json(json_fileitems,userid,test_name)
