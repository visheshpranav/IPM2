import subprocess
import cgi, cgitb; cgitb.enable()

form = cgi.FieldStorage()
user_id = form.getvalue("user_id")
rep_id = form.getvalue("rep_id").strip()
report_name = form.getvalue("report_name").strip()
app_name = form.getvalue("app_name").strip()
uploaded_filename = form.getvalue("uploaded_filename").strip()
mode = form.getvalue("mode").strip()
Imp_id = form.getvalue("Imp_id").strip()
observation = form.getvalue("observation").strip()
imp_name = form.getvalue("imp_name").strip()
start_date = form.getvalue("start_date").strip().replace(' ', 'T')
end_date = form.getvalue("end_date").strip().replace(' ', 'T')
search_key = form.getvalue("search_key").strip()
function_name = form.getvalue("function_name").strip()

##user_id = "5"
##rep_id = "empty"
##report_name = "may6"
##app_name = "TWA"
##function_name = "mapping"
##uploaded_filename="WebSphere-SystemOut_19.03.08_00.58.30.log"
##mode = "OFL"
##Imp_id = "empty"
##observation = "empty"
##imp_name = "empty"
##start_date = "empty"
##end_date = "empty"
##search_key = "empty"

##Manual execution
##uploaded_filename = "empty"
##user_id = "41"
##mode = "OFL"
##app_name = "Workshop"
##report_name = "de113"
##rep_id = "795"
##mode = "OFL"
##Imp_id = "empty"
##observation = "empty"
##imp_name = "empty"
##start_date = "empty"
##end_date = "empty"
##search_key = "empty"
##function_name = "SAPUsageAnalysis"

try:
    fn_output = subprocess.check_output('FileEncrypt.exe %s %s %s %s %s %s %s %s %s %s %s %s %s' % (user_id, rep_id, report_name, app_name, uploaded_filename, mode, observation, Imp_id, imp_name, start_date, end_date, search_key, function_name), shell=False) #could be anything here.
    print("Content-type: text/html \n")
    out_arr = str(fn_output).split("\\r\\n")
    val = 0
    for out_val in out_arr:
        if ("Requesting" not in out_val):
            if val > 1:
                if out_val != "'":
                    if out_val:
                        print(out_val.replace("\\",""))
            else:
                val = val + 1
except Exception as e:
    print(e)
