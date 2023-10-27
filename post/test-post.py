import requests
import json

url = 'http://127.0.0.1:8090/ocr'
files = {'file': open(r'E:\dev\datasets\html\ocr{}_text_347_323_82.png', 'rb')}
r = requests.post(url, files=files)
print(r.text)
