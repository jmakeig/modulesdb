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

class ModulesClient(object):

    def __init__(self, config):
        # print config
        self.url = config.get('url')
        self.auth_type = config.get('auth')
        self.user = config.get('user')
        self.password = config.get('password')
        cert = None
        cert_password = None
        self.root = config.get('root')
        # TODO: Figure out how to parameterize this
        self.permissions = [{"app-user", "execute"}]

        if self.auth_type == "digest":
            self.auth = HTTPDigestAuth(self.user, self.password)
        else: 
            raise Exception("Unsupported auth_type " + self.auth_type)

    def put(self, uri, body, transaction=None):
        "Send a file to the remote modules database. URIs are prepended with the root."
        params = {"uri": self.root + uri, "perm:app-user": "execute"} # TODO: Fix perms
        headers = {}
        r = requests.put(
            self.url + "/v1/documents", 
            params=params, 
            headers=headers, 
            auth=self.auth,
            data=body
        )
        return ("PUT", r.status_code, params['uri'])

    def put_file(self, uri, file_path, transaction=None):
        "Open a file for reading, put its contents using self.put, and close it."
        f = open(file_path, "r")
        msg = self.put(uri=uri, body=f.read(), transaction=transaction)
        f.close()
        return msg

    def delete(self, uri, transaction=None):
        "Delete a remote file identified by the URI."
        params = {"uri": self.root + uri}
        headers = {}
        r = requests.delete(
            self.url + "/v1/documents", 
            params=params, 
            headers=headers, 
            auth=self.auth
        )
        return ("DELETE", r.status_code, self.root + uri)

    def move(self, from_uri, to_uri, body, transaction=None):
        pass

    def move_file(self, from_uri, to_uri, file_path, transaction=None):
        self.delete(from_uri, transaction)
        msg = self.put_file(to_uri, file_path, transaction)
        return ("MOVE", msg[1], self.root + to_uri)


