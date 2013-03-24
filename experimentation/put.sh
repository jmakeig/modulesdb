#! /bin/sh

# PUT a file to a REST instance
curl --anyauth --user admin:admin -i -X PUT -H "Content-Type: application/xquery" --data-binary "'asdf'" http://localhost:9556/v1/documents?uri=/test.xqy\&perm:app-user=execute
