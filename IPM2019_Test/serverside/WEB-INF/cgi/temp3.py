import urllib.request

with urllib.request.urlopen("https://uploads3.s3.us-west-2.amazonaws.com/uploadreports/RE_223_MxmlTrades.zip") as url:
    s = url.read()
    print(s)
