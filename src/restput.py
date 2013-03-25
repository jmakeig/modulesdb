# -*- coding: utf-8 -*-

import requests
from requests.auth import HTTPDigestAuth

def put_file(uri, body, host="localhost", port=9556, protocol="http"):
    user = "admin"
    passw = "admin"
    # uri = "/test.xqy"
    params = {"uri": "/" + uri, "perm:app-user": "execute"}
    headers = {}
    # headers = {'content-type': 'application/xquery'}
    # body = "'Hello, from Python requests!'"
    r = requests.put(
        protocol + "://" + host + ":" + str(port) + "/v1/documents", 
        params=params, 
        headers=headers, 
        auth=HTTPDigestAuth(user, passw),
        data=body
    )
    print r.status_code