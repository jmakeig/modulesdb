# This creates an HTTP message
# with the content of BODY as the enclosed representation
# for the resource http://localhost:8080/foobar
# import httplib, urllib
# BODY = "xdmp:get-request-field-names()"
# conn = httplib.HTTPConnection("localhost", 9556)
# headers = {"Content-type": "application/xquery"}
# params = urllib.urlencode({'@number': 12524, '@type': 'issue', '@action': 'show'})
# conn.request("PUT", "/v1/documents?uri=/test.xqy&perm:app-user=execute", BODY, headers)
# response = conn.getresponse()
# print response.status, response.reason

import requests
from requests.auth import HTTPDigestAuth
user = "admin"
passw = "admin"
uri = "/test.xqy"
params = {"uri": uri, "perm:app-user": "execute"}
headers = {'content-type': 'application/xquery'}
body = "'Hello, from Python requests!'"
r = requests.put("http://localhost:9556/v1/documents", params=params, headers=headers, data=body, auth=HTTPDigestAuth(user, passw))
print r.status_code