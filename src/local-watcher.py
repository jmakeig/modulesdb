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
import copy
import argparse
import json

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
    # print msg
    verb = "* Updated"
    if msg[0] == "DELETE": 
        verb = "- Removed"
    if msg[0] == "PUT" and msg[1] == 201:
        verb = "+ Added"
    return verb + " " + msg[2]

def put_file_contents(path):
    "Sends the contents of the file at the input path to the globally configured REST URL"
    f = open(path, "r")
    msg = put_file(uri=os.path.relpath(path, BASEDIR), body=f.read(), service_url=URL)
    f.close()
    return msg


class ChangeHandler(FileSystemEventHandler):
    "Handle changes to files and directories."

    # TODO: Exclusion lists (e.g. .git, .DS_Store, Thumbs.db), similar to the way .gitignore works. 
    # Call it .mlignore? Is there a Python class that already does this matching?

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
        # print "deleted event"
        if event.is_directory:
            return
        else: 
            # getext(event.src_path) == '.py':
            # print "Changed " + os.path.relpath(event.src_path, BASEDIR)
            # f = open(event.src_path, "r")
            # put_file(uri=os.path.relpath(event.src_path, BASEDIR), body=f.read(), service_url=URL)
            print format_put_message(delete_file(uri=os.path.relpath(event.src_path, BASEDIR), service_url=URL))

    def on_moved(self, event):
        # print "moved event"
        # TODO: This needs to be wrapped in a transaction and give better feedback

        #move_file(src_uri=os.path.relpath(event.src_path, BASEDIR), dest_uri=)

        delete_file(uri=os.path.relpath(event.src_path, BASEDIR), service_url=URL)
        print format_put_message(put_file_contents(event.dest_path))

    def on_any_event(self, event):
        print event
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
    # All of the examples call .join(). I don't see how this is ever exectued, though, except right after the interrupt is handled. What does join do?
    observer.join()

if __name__ == '__main__':
    # TODO: Look for settings in a config file, override with command line
    #   * Directory to watch: Defaults to current working directory if not specified. Command line only.
    #   * Whether to do a full recursive walk first: Command line only
    #   * URL for the REST service (http, https)
    #   * Root modules database directory: Do we need this?
    #   * Authentication (basic, digest, none) and credentials (user, password, client cert): Should this be command-line only?
    #   * List of exclusions: First .dot files globally then should support .gitignore-style match expressions
    #   * Permissions on files: Can this be global (i.e. does XQuery only need execute perms and JavaScript only need read?)? Map to directory? Extension?

    # What else needs to be done to support running this in the background and logging somewhere else? (Perhaps nothing)
    # What about when something fails? A local rm that results in a connection or auth error on the server will leave things in an inconsistent state, for example.


    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", nargs='?', help="The REST API endpoint fronting the modules database, of the form protocol://host:port, where protocol is http or https")
    parser.add_argument('--walk', action="store_true", default=None) # , action='store_true', default=False
    parser.add_argument("dir", nargs='?', help="The directory to watch", default=os.getcwd())

    # UGLY: Is this the only way to do this?
    args = copy.deepcopy(
        vars(
            parser.parse_args()
        )
    )

    # UGLY
    if args['url'] is None:
        del args['url']
    if args['walk'] is None:
        del args['walk']

    print "command-line args"
    print args

    # Get the preferences out of a dot file in the target directory
    # Command-line options take precedence
    prefs = {}
    pref_path = args['dir'] + "/.modulesdb"
    if os.path.exists(pref_path):
        print "Reading preferences from " + pref_path
        pref_file = open(pref_path, "r")
        prefs = json.load(pref_file)
        print prefs

    prefs.update(args)

    print prefs

    # Start the script in a directory you want to observe
    BASEDIR = os.path.abspath(prefs['dir'])
    URL = prefs['url']

    if prefs['walk']:
        print "Walking " + BASEDIR
        walk(BASEDIR)

    print "Observing " + BASEDIR + "…"
    observe()
