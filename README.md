# modulesdb

Listen to changes in a local directory and automatically push them to a modules database. This implementation uses the REST API, but that’s an implementation detail.

## Getting Started 

Run ```config/setup.sh``` to get the required dependencies using ```pip```. 

From the command line in the directory you want to push to your remote modules database run

```python ~/path/to/cloned/projects/modulesdb/src/local-watcher.py --walk http://localhost:9556```

where ```9556``` is the port of the REST API instance fronting your target modules database.

```--walk``` will recusively walk the directory structure an push everything.

### Notes
This assumes ```admin:admin``` credentials (D’oh! Don’t do anything important with this.) and a root of ```/``` in your modules database.

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
