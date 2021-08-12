import requests, re
  
# Making a get request
response = requests.post('https://ttp-lapam.accenture.com')
print("Content-type: text/html \n");
print("Inside");
# printing request cookies
for c in response.cookies:
    print(c.name, c.value)
print(response.cookies)
print(response.status_code)
print(response.headers)
ses=requests.Session()
##ses.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 managedpc (Accenture)'})
##ses.headers.update({'Connection': 'keep-alive'})
print(ses.cookies.get_dict())
res = ses.post('https://ttp-lapam.accenture.com')

##show_cookie = lambda x: [re.findall(r"([^,;\s]*?=.*?(?=;|$))|(\w+(?=;|$|,))",cookie) for cookie in re.findall(r"((?:^|,\s).*?)(?=,\s\S+;|$)",x)]
##print(show_cookie(res.headers.get('Set-Cookie')))
with requests.Session() as s:
    resp = s.get("https://github.com")
    #show_cookie = lambda x: [re.findall(r"([^,;\s]*?=.*?(?=;|$))|(\w+(?=;|$|,))",cookie) for cookie in re.findall(r"((?:^|,\s).*?)(?=,\s\S+;|$)",x)]
    print(resp.headers.get('Set-Cookie'))


