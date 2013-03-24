import requests
from requests.auth import HTTPDigestAuth

def put_file(body):
  user = "admin"
  passw = "admin"
  uri = "/test.xqy"
  params = {"uri": uri, "perm:app-user": "execute"}
  headers = {'content-type': 'application/xquery'}
  #body = "'Hello, from Python requests!'"
  r = requests.put("http://localhost:9556/v1/documents", params=params, headers=headers, data=body, auth=HTTPDigestAuth(user, passw))
  print r.status_code