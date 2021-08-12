import os
import pandas as pd 
import numpy as np
import cgi
import csv, shutil

form = cgi.FieldStorage()
fileName = form.getvalue("filename")
filename = "C:/LAPAM2019/DataLake/Cache/44/Sample/"+fileName
values = form.getvalue('values')
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w") as f:
    f.write(values)