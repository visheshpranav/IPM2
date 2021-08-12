# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 10:40:38 2021

@author: v.a.subhash.krishna
"""

from boto3.session import Session
import configparser,os
import boto3

#fetch the upload path from config
parser = configparser.ConfigParser() 
parser.read("C:\\LAPAM2019\\Config\\configfile.config")
ACCESS_KEY = parser.get('AWS_CRED','accesskey')
SECRET_KEY = parser.get('AWS_CRED','secretkey')
BUCKET_NAME = parser.get('AWS_CRED','bucketname')
DATA_PATH = parser.get('Upload','Oflpath')




def file_download(fileitem,userid,test_name,logtype):
##    print(ACCESS_KEY,SECRET_KEY,BUCKET_NAME)
    
    session = Session(aws_access_key_id=ACCESS_KEY,
                  aws_secret_access_key=SECRET_KEY)
##    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
##                      aws_secret_access_key=SECRET_KEY)
    s3 = session.resource('s3')
    your_bucket = s3.Bucket(BUCKET_NAME)
    if not os.path.exists(DATA_PATH + "Cache\\" + userid):
        os.mkdir(DATA_PATH + "Cache\\" + userid)
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    dir_path = DATA_PATH + "Cache\\" + userid + "\\" + test_name+"\\"+str(logtype)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    full_dir_path = dir_path + "\\"
##    for s3_file in your_bucket.objects.all():
##        print(s3_file.key) # prints the contents of bucket
    
    your_bucket.download_file(test_name+"/"+fileitem,full_dir_path+fileitem)
    #s3.download_file(BUCKET_NAME,test_name+"/"+fileitem,full_dir_path+fileitem)
    return full_dir_path+fileitem


if __name__ == "__main__":
    print(file_download("RE_223_MxmlTrades.zip","44","uploadreports","TradeInsertion"))
    






