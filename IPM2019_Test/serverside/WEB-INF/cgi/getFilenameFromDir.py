import os
import cgi, cgitb 
import cgitb; cgitb.enable()

if __name__ == "__main__":
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()    
    user_id = form.getvalue('user_id')
    rep_id = form.getvalue('rep_id')
    Imperative_name = form.getvalue('Imperative_name')
    mode = form.getvalue('mode')
    isTxtfile = 0
##    user_id="5"
##    rep_id = "506"
##    Imperative_name = "memory analysis"
##    mode="OFL"
    servicecall = []
    filepath="" 
    if mode == "OFL":   
        folderpath = user_id +"_"+ rep_id
        filepath = "../../../WEB-INF/classes/static/html/Reports/"+folderpath
    else:
        filepath = "../../../WEB-INF/classes/static/html/online"
        
    for file in os.listdir(filepath):
        if (file.endswith(".txt")) and (Imperative_name in file):
            isTxtfile = 1
            print(file)            
        elif (file.endswith(".csv")) and (Imperative_name in file) and (isTxtfile == 0):
            remove_ext, ext = os.path.splitext(file)
            getservicecall = remove_ext.split("_")
            if len(getservicecall) > 5:
                print(getservicecall)
                if mode == "OFL":
                    servicecall.append(getservicecall[len(getservicecall) - 2])
                else:
                    servicecall.append(getservicecall[len(getservicecall) - 3])
    if servicecall and (isTxtfile == 0):
        servicecall = set(servicecall)
        print(servicecall)
