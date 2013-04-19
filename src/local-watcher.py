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
Pushes changes to a local directory to a remote modulues database fronted by a REST API endpoint.
"""
import os
import sys
import subprocess
import datetime
import time
import copy
import argparse
import getpass
import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from modulesclient import ModulesClient

def walk(top):
    "Walks the file system recursively starting at top, putting each file to the globally defined REST service."
    for root, dirs, files in os.walk(top):
        for name in files:
            print format_put_message(
                modules_client.put_file(
                    uri=os.path.relpath(os.path.join(root, name), BASEDIR),
                    file_path=os.path.join(root, name)
                )
            )

def format_put_message(msg):
    "Format the return values for reporting to stdout"
    # msg is of the form (HTTP verb, URI of the affected doc, status code)
    # 201 is added or
    # print msg
    verb = "* Updated"
    if msg[0] == "DELETE": 
        verb = "- Removed"
    if msg[0] == "PUT" and msg[1] == 201:
        verb = "+ Added"
    return verb + " " + msg[2]



class ChangeHandler(FileSystemEventHandler):
    "Handle changes to files and directories."

    # TODO: Exclusion lists (e.g. .git, .DS_Store, Thumbs.db), similar to the way .gitignore works. 
    # Call it .mlignore? Is there a Python class that already does this matching?

    def on_created(self, event):
        # print "created event"
        if event.is_directory:
            return
        else: 
            print format_put_message(
                modules_client.put_file(uri=os.path.relpath(event.src_path, BASEDIR), file_path=event.src_path)
            )

    def on_modified(self, event):
        # print "modified event"
        if event.is_directory:
            return
        else: 
            print format_put_message(
                modules_client.put_file(uri=os.path.relpath(event.src_path, BASEDIR), file_path=event.src_path)
            )

    def on_deleted(self, event):
        # print "deleted event"
        if event.is_directory:
            return
        else: 
            print format_put_message(
                modules_client.delete(uri=os.path.relpath(event.src_path, BASEDIR))
            )

    def on_moved(self, event):
        # delete_file(uri=os.path.relpath(event.src_path, BASEDIR), service_url=URL)
        print format_put_message(
            # put_file_contents(event.dest_path)
            modules_client.move_file(from_uri=os.path.relpath(event.src_path, BASEDIR), to_uri=os.path.relpath(event.dest_path, BASEDIR), file_path=event.dest_path)
        )

    def on_any_event(self, event):
        # print event
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
    parser.add_argument("--url", default=None, help="The REST API endpoint fronting the modules database, of the form protocol://host:port, where protocol is http or https")
    parser.add_argument('--auth', default=None, choices=["none", "digest", "basic", "cert"]) # None here means that it can be pruned such taht the overlay on the dot file just works
    parser.add_argument('--user', "-u", default=None, help="The username to use to authenticate against the REST service")
    parser.add_argument('--password', "-p", default=None, help="The password to use to authenticate against the REST service")
    #parser.add_argument('--cert', "-E", help="(SSL) Tells curl to use the specified client certificate file when getting a file with HTTPS, FTPS or another SSL-based protocol. The certificate must be in PEM format. If the optional password isn't specified, it will be queried for on the terminal. Note that this option assumes a \"certificate\" file that is the private key and the private certificate concatenated! See --cert and --key to specify them independently.")
    #parser.add_argument('--key', help="(SSL/SSH) Private key file name. Allows you to provide your private key in this separate file.")
    #parser.add_argument('--insecure', "-k")
    
    # Command-line only
    parser.add_argument('--walk', action="store_true", default=False, help="Whether to recusively push all of the files to the modules database before begining observation")
    parser.add_argument("--debug", action="store_true", default=False)
    #parser.add_argument('--quiet', '-q', action="store_true", default=False, help="")

    parser.add_argument("dir", nargs='?', help="The directory to watch", default=os.getcwd())

    # UGLY: Turn the Namesapce into a dictionary. Is this the only way to do this?
    args = copy.deepcopy(vars(parser.parse_args()))

    # Prune Nones from command-line args
    # http://stackoverflow.com/questions/2544710/how-i-can-get-rid-of-none-values-in-dictionary
    args = dict((k,v) for k,v in args.iteritems() if v is not None)

    # Get the preferences out of a dot file in the target directory
    # Command-line options take precedence
    prefs = {}
    pref_path = args['dir'] + "/.modulesdb"
    if os.path.exists(pref_path):
        print "Reading preferences from " + pref_path
        pref_file = open(pref_path, "r")
        prefs = json.load(pref_file)
        # print prefs

    # Overlay command-line arguments on top of the preferences read from the dot file
    prefs.update(args)

    # Ask for a password if it's not provided
    if prefs['auth'] in ['digest', 'basic'] and "password" not in prefs:
        prefs['password'] = getpass.getpass("Password for " + prefs['url'] + ": ")

    if prefs['debug']:
        print prefs

    modules_client = ModulesClient(prefs)

    # Start the script in a directory you want to observe
    BASEDIR = os.path.abspath(prefs['dir'])

    if prefs['walk']:
        print "Walking " + BASEDIR
        walk(BASEDIR)

    print "Observing " + BASEDIR + "…"
    observe()
