import json

azure={
'client_id':'',
'client_secret':'',
'redirect_uri':''
}

with open('azure.json','w') as f:
    json.dump(azure,f,indent=4)
