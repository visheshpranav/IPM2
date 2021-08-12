import pandas as pd
import cgi, cgitb,sys, re
import cgitb; cgitb.enable()

def sort_csv(col_no, folder_Name, Tcode):
    #filepath = 'C:\\Users\\kusuluv\\Downloads\\42_stad_09_jun_AS03.csv'
    
    dir_path = "../../../WEB-INF/classes/static/html/Reports/"+folder_Name
    Tcode = re.sub(r"[()\#/<>{}~|!?,]", "", Tcode)
    Tcode = Tcode.replace(" ", "")
    filepath = dir_path+"/"+folder_Name+"_"+Tcode+ ".csv"
    print(filepath)
    df = pd.read_csv(filepath, header=0, low_memory=False)
    header_list = list(df.columns)
    print(header_list)
    column_name = header_list[int(col_no)]
    print(column_name)
    df.sort_values(by=column_name, ascending=False, inplace=True)
    filepath = dir_path+"/"+folder_Name+"_"+Tcode+ "_"+col_no+".csv"
    df.to_csv(filepath, index=False)
    
if __name__ == '__main__':
    print("Content-type: text/html \n");
    form = cgi.FieldStorage()
    col_no = form.getvalue("col_no")
    userid = form.getvalue("userid")
    test_name = form.getvalue("test_name")
    Tcode = form.getvalue("Tcode")
    folder_Name = str(userid) + "_"+test_name.lower()
    sort_csv(col_no, folder_Name,Tcode)
