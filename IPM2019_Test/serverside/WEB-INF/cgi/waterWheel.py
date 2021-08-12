import sched, time
from datetime import datetime
import configparser
import subprocess
import cgi, cgitb; cgitb.enable()

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
Freq_Seconds = parser.get('Waterwheel','Freq_Seconds')

s = sched.scheduler(time.time, time.sleep)
def do_something(sc):
    print(datetime.now())
    uploaded_filename = "SystemOut.log"
    user_id = "empty"
    report_name = "empty"
    mode = "ONL"
    app_name = "TWA"
    rep_id = "empty"
    Imp_id = "empty"
    observation = "empty"
    imp_name = "empty"
    start_date = "empty"
    end_date = "empty"
    search_key = "Websphere"
    function_name = "mapping"
##    filename = "JVMlogs.zip"
##    userid = ""
##    test_name = ""
##    username=""
##    mode = "ONL"
##    appName = "JVM"
    fn_output = subprocess.check_output('FileEncrypt.exe %s %s %s %s %s %s %s %s %s %s %s %s %s' % (user_id, rep_id, report_name, app_name, uploaded_filename, mode, observation, Imp_id, imp_name, start_date, end_date, search_key, function_name), shell=False) #could be anything here.
    print("Content-type: text/html \n")
    out_arr = str(fn_output).split("\\r\\n")
    val = 0
    for out_val in out_arr:
        if ("Requesting" not in out_val):
            if val > 1:
                if out_val != "'":
                    print(out_val.replace("\\",""))
            else:
                val = val + 1
    #main_process(username,userid,test_name,filename,mode,appName, logtype_val)
    # do your stuff
    s.enter(int(Freq_Seconds), 1, do_something, (sc,))

s.enter(0, 1, do_something, (s,))
s.run()
