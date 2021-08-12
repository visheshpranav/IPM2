#!/usr/bin/python

import sys
import re
import json

from datetime import datetime, timedelta
import jwt


#https://www.guru99.com/date-time-and-datetime-classes-in-python.html
#timedelta(days=365, hours=8, minutes=15)
#'exp': int(dt.strftime('%s'))


dt = datetime.now() + timedelta(days=1)
secret = "TTP@123"
encoded_token = jwt.encode({'user_id': "ttpuser", 'exp': dt }, secret, algorithm='HS256')
print(encoded_token)

#decode above token
decode_token=jwt.decode(encoded_token, secret, algorithms=['HS256'])

content = decode_token
print(content)
print(content['user_id'])
print('json token successfully retrieved')

if content['user_id'] =='' or content['email'] == '':
    print("Invalid Token")
else:
    print("Token is still valid")

#check if token has expired after 2 days

    if content['exp'] > dt:
        print("Token is still active")
    else:
        print("Token expired. Get new one")
