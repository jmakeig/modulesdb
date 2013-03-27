# -*- coding: utf-8 -*-

# Copyright 2013 Justin Makeig <<https://github.com/jmakeig>>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
from requests.auth import HTTPDigestAuth

def put_file(uri, body, service_url):
    user = "admin"
    passw = "admin" # Duh! That's obviously a bad idea.
    # uri = "/test.xqy"
    params = {"uri": "/" + uri, "perm:app-user": "execute"}
    headers = {}
    # headers = {'content-type': 'application/xquery'}
    # body = "'Hello, from Python requests!'"
    r = requests.put(
        service_url + "/v1/documents", 
        params=params, 
        headers=headers, 
        auth=HTTPDigestAuth(user, passw),
        data=body
    )
    print r.status_code