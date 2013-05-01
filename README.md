# modulesdb

Listen to changes in a local directory and automatically push them to a modules database. This implementation uses the REST API, but that’s an implementation detail.

## Getting Started 

Run ```config/setup.sh``` to get the required dependencies using ```pip```. 

From the command line in the directory you want to push to your remote modules database run

```python ~/path/to/cloned/projects/modulesdb/src/local-watcher.py -url http://localhost:9556 --user modules-writer --walk```

where ```http://localhost:9556``` is the base URL of the REST API instance fronting your target modules database.

```--walk``` will recusively walk the directory structure an push everything prior to enabling the long-running directory watcher.

The log should show a message whenever it receives a change event and pushes something. 

Stop listening for changes using ```Ctl+c```.

### Command line usage

    usage: local-watcher.py [-h] [--url URL] [--auth {none,digest,basic,cert}]
                            [--user USER] [--password PASSWORD]
                            [--permission [PERMISSIONS]] [--ignore [IGNORE]]
                            [--config CONFIG] [--walk] [--debug]
                            [dir]

    positional arguments:
      dir                   The directory to watch. Defaults to the current
                            working directory.

    optional arguments:
      -h, --help            show this help message and exit
      --url URL             The REST API endpoint fronting the modules database,
                            of the form protocol://host:port, where protocol is
                            http or https
      --auth {none,digest,basic,cert}
                            The HTTP authentication method to use.
      --user USER, -u USER  The username to use to authenticate against the REST
                            service.
      --password PASSWORD, -p PASSWORD
                            The password to use to authenticate against the REST
                            service. If the authentication method requires a
                            password and you don't supply one at the command line
                            or in the prefrences file you will be prompted for it.
      --permission [PERMISSIONS], -perm [PERMISSIONS]
                            The permissions that should be set on all files.
      --ignore [IGNORE]     A gitignore-style path to ignore for observation and
                            walking.
      --config CONFIG, -K CONFIG
                            The location of the JSON configuration file. Command-
                            line options take precedence. Defaults to .modulesdb
                            at the root of the directory being observed.
      --walk                Whether to recusively push all of the files to the
                            modules database before begining observation.
      --debug               Print out some extra debugging information.

### Dot file configuration
Alernatively, you can specify a JSON file with configuration. By default the script looks for ```.modulesdb``` in the root directory of the tree you’re observiging or you can specify another path using the ```--config``` or ```-K``` command-line option. 

    {
      "url": "http://localhost:9556",
      "auth": "digest",
      "user": "admin",
      "password": "*************",
      "root": "/",
      "permissions": {
        "app-user":["read", "update", "execute"]
      },
      "ignore": [".modulesdb", ".*", "*/.*"]
    }

## License
Copyright 2013 Justin Makeig <<https://github.com/jmakeig>>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

### Third-Party Licenses

None (yet).
