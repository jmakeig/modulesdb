#!/usr/bin/env python
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

from restput import put_file, delete_file
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def walk(top):
    "Walks the file system recursively starting at top, putting each file to the globally defined REST service."
    for root, dirs, files in os.walk(top):
        for name in files:
            # print os.path.join(root, name)
            print format_put_message(put_file_contents(os.path.join(root, name)))

def format_put_message(msg):
    # msg is of the form (HTTP verb, URI of the affected doc, status code)
    # 201 is added or
    print msg
    verb = "Stuffed"
    # TODO
    return "  " + verb + " " + msg[2]

def put_file_contents(path):
    "Sends the contents of the file at the input path to the globally configured REST URL"
    f = open(path, "r")
    msg = put_file(uri=os.path.relpath(path, BASEDIR), body=f.read(), service_url=URL)
    f.close()
    return msg


class ChangeHandler(FileSystemEventHandler):
    "Handle changes to files and directories."

    def on_created(self, event):
        # print "created event"
        if event.is_directory:
            return
        else: 
            # getext(event.src_path) == '.py':
            # print "Changed " + os.path.relpath(event.src_path, BASEDIR)
            # f = open(event.src_path, "r")
            # put_file(uri=os.path.relpath(event.src_path, BASEDIR), body=f.read(), service_url=URL)
            print format_put_message(put_file_contents(event.src_path))

    def on_modified(self, event):
        # print "modified event"
        if event.is_directory:
            return
        else: 
            # getext(event.src_path) == '.py':
            # print "Changed " + os.path.relpath(event.src_path, BASEDIR)
            # f = open(event.src_path, "r")
            # put_file(uri=os.path.relpath(event.src_path, BASEDIR), body=f.read(), service_url=URL)
            print format_put_message(put_file_contents(event.src_path))

    def on_deleted(self, event):
        print "deleted event"
        if event.is_directory:
            return
        else: 
            # getext(event.src_path) == '.py':
            # print "Changed " + os.path.relpath(event.src_path, BASEDIR)
            # f = open(event.src_path, "r")
            # put_file(uri=os.path.relpath(event.src_path, BASEDIR), body=f.read(), service_url=URL)
            print format_put_message(delete_file(uri=os.path.relpath(event.src_path, BASEDIR), service_url=URL))

    def on_moved(self, event):
        print "moved event"

    def on_any_event(self, event):
        #print event
        pass

        
        
def observe(recursive=True):
    "Observe folder and file changes. Only supports"
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, BASEDIR, recursive=recursive)
    observer.start()
    try: 
        while True: 
            time.sleep(1) 
    except KeyboardInterrupt: 
        observer.stop()
        # sys.exit(0)
    # All of the examples call .join(). I don't see how this is ever exectued, though.
    observer.join()


if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The REST API endpoint fronting the modules database, of the form protocol://host:port, where protocol is http or https")
    parser.add_argument('--walk', action='store_true', default=False)
    parser.add_argument("dir", nargs='?', help="The directory to watch", default=os.getcwd())
    args = parser.parse_args()


    # Start the script in a directory you want to observe
    BASEDIR = os.path.abspath(args.dir)
    URL = args.url

    if args.walk:
        print "Walking " + BASEDIR
        walk(BASEDIR)

    print "Observing " + BASEDIR
    observe()
