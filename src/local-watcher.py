# -*- coding: utf-8 -*-

# Copyright 2013 Justin Makeig <<https://github.com/jmakeig>>

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

"""
Monitors our code & docs for changes
"""
import os
import sys
import subprocess
import datetime
import time
import argparse

from restput import put_file
from watchdog.observers import Observer
# from watchdog.observers.kqueue import KqueueObserver as Observer
from watchdog.events import FileSystemEventHandler


# Parse the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("url", help="The REST API endpoint fronting the modules database, of the form protocol://host:port, where protocol is http or https")
parser.add_argument("dir", nargs='?', help="The directory to watch", default=os.getcwd())
args = parser.parse_args()


# Start the script in a directory you want to observe
BASEDIR = os.path.abspath(args.dir)
URL = args.url

print BASEDIR

class ChangeHandler(FileSystemEventHandler):
    """
    React to changes in Python and Rest files by
    running unit tests (Python) or building docs (.rst)
    """

    def on_any_event(self, event):
        "If any file or folder is changed"

        if event.is_directory:
            return
        else: 
            # getext(event.src_path) == '.py':
            print "Changed " + os.path.relpath(event.src_path, BASEDIR)
            f = open(event.src_path, "r")
            put_file(uri=os.path.relpath(event.src_path, BASEDIR), body=f.read(), service_url=URL)
        
def main():
    """
    Called when run as main.
    Look for changes to code and doc files.
    """

    while 1:
        event_handler = ChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, BASEDIR, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == '__main__':
    main()