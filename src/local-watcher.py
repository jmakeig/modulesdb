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
import fnmatch
import re

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from modulesclient import ModulesClient

def walk(top, exclusions=[]):
    "Walks the file system recursively starting at top, putting each file to the globally defined REST service."

    # TODO: Figure out how to separate out directory and file exclusions
    # http://stackoverflow.com/a/5141829/563324
    excludes = r'|'.join([fnmatch.translate(x) for x in exclusions]) or r'$.'
    # print excludes

    def _rel(path, start):
        "Pass-through to os.path.relpath except that it returns an empty string instead of '.' for exact matches."
        r = os.path.relpath(path, start)
        if "." == r:
            return ""
        return r

    for root, dirs, files in os.walk(top):
        
        # print top, root, dirs, [os.path.join(os.path.relpath(root, top), d) for d in dirs]
        
        # dirs[:] = [os.path.join(top, d) for d in dirs]
        # print dirs
        # print (root, top, os.path.relpath(root, top))
        # for d in dirs:
        #     print (os.path.join(_rel(root, top), d), bool(re.match(excludes, os.path.join(_rel(root, top), d))))
        dirs[:] = [d for d in dirs if not re.match(excludes, os.path.join(_rel(root, top), d))]        
        #print dirs

        for name in files:
            asb = os.path.join(root, name)
            rel = _rel(asb, top)
            #print (rel, os.path.join(os.path.relpath(root, top)))
            if not re.match(excludes, rel):
                print format_put_message(
                    modules_client.put_file(
                        uri=rel,
                        file_path=asb
                    )
                )
            # else:
            #     print "  Ignoring " + rel

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

    def __init__(self, directory, exclusions=[], after=[]):
        "Initialize with the base directory."
        self.directory = directory
        self.exclusions = exclusions
        self.exclusions_re = r'|'.join([fnmatch.translate(x) for x in exclusions]) or r'$.'
        self.after = after # after is a list of strings, each of which is a path to a shell script. TODO: Is that the best way?

    def _rel(self, path):
        "Use the stored base directory to calculate the relative path with os.path.relpath."
        r = os.path.relpath(path, self.directory)
        if "." == r:
            return ""
        return r

    def _is_excluded(self, path):
        "Whether a particular path is excluded based on the list passed in at initialization."
        return bool(re.match(self.exclusions_re, self._rel(path)))

    def _run_after(self, event):
        "Loops through the list of scripts and runs each in a separate subprocess"
        # TODO: Figure out if there are acutal requirements for I/O in and out of the script.
        for script in self.after:
            # TODO: Need some try/catch logic here
            subprocess.call([script])


    # TODO: Exclusion lists (e.g. .git, .DS_Store, Thumbs.db), similar to the way .gitignore works. 
    # Call it .mlignore? Is there a Python class that already does this matching?

    def on_created(self, event):
        # print "created event"
        if event.is_directory or self._is_excluded(event.src_path):
            return
        else: 
            print format_put_message(
                modules_client.put_file(uri=self._rel(event.src_path), file_path=event.src_path)
            )
            self._run_after(event)

    def on_modified(self, event):
        # print "modified event " + self._rel(event.src_path)
        if event.is_directory or self._is_excluded(event.src_path):
            return
        else: 
            print format_put_message(
                modules_client.put_file(uri=self._rel(event.src_path), file_path=event.src_path)
            )
            self._run_after(event)

    def on_deleted(self, event):
        # print "deleted event"
        if event.is_directory or self._is_excluded(event.src_path):
            return
        else: 
            print format_put_message(
                modules_client.delete(uri=self._rel(event.src_path))
            )
            self._run_after(event)

    def on_moved(self, event):
        # TODO: Clean all of this logic and repeated code up
        if self._is_excluded(event.src_path) and not self._is_excluded(event.dest_path):
            print format_put_message(
                modules_client.put_file(uri=self._rel(event.dest_path), file_path=event.dest_path)
            )
            return
        if not self._is_excluded(event.src_path) and self._is_excluded(event.dest_path):
            print format_put_message(
                modules_client.delete(uri=self._rel(event.src_path))
            )
            return
        # print "moved event"
        print format_put_message(
            # put_file_contents(event.dest_path)
            modules_client.move_file(from_uri=self._rel(event.src_path), to_uri=self._rel(event.dest_path), file_path=event.dest_path)
        )
        self._run_after(event)

    def on_any_event(self, event):
        # print event
        pass

        
        
def observe(directory, recursive=True, exclusions=[], after=[]):
    "Observe folder and file changes. Only supports"
    event_handler = ChangeHandler(directory, exclusions, after)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=recursive)
    observer.start()
    try: 
        while True: 
            time.sleep(1) 
    except KeyboardInterrupt: 
        observer.stop()
    # All of the examples call .join(). I don't see how this is ever exectued, though, except right after the interrupt is handled. What does join do?
    observer.join()

if __name__ == '__main__':
    def get_configuration(working_dir, command_line):
        "Get the configuration from a combination of the command line input and a dot file"
        # Parse the command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("--url", default=None, help="The REST API endpoint fronting the modules database, of the form protocol://host:port, where protocol is http or https")
        parser.add_argument('--auth', default=None, choices=["none", "digest", "basic", "cert"], help="The HTTP authentication method to use.") # None here means that it can be pruned such taht the overlay on the dot file just works
        parser.add_argument('--user', '-u', default=None, help="The username to use to authenticate against the REST service.")
        parser.add_argument('--password', '-p', default=None, help="The password to use to authenticate against the REST service. If the authentication method requires a password and you don't supply one at the command line or in the prefrences file you will be prompted for it.")
        parser.add_argument('--database', '-d', default=None, help="The name of the database to write to")
        #parser.add_argument('--cert', "-E", help="(SSL) Tells curl to use the specified client certificate file when getting a file with HTTPS, FTPS or another SSL-based protocol. The certificate must be in PEM format. If the optional password isn't specified, it will be queried for on the terminal. Note that this option assumes a \"certificate\" file that is the private key and the private certificate concatenated! See --cert and --key to specify them independently.")
        #parser.add_argument('--key', help="(SSL/SSH) Private key file name. Allows you to provide your private key in this separate file.")
        #parser.add_argument('--insecure', "-k")                
        parser.add_argument('--permission', '-perm', dest="permissions", nargs="?", action="append", default=None, help="Zero or more permissions that should be set on all files. Each entry should be an individaul role:capability, where capability is in {read, update, execute}, for example -perm app-user:execute.")
        parser.add_argument('--ignore', nargs="?", action="append", default=None, help="A gitignore-style path to ignore for observation and walking.")
        
        # Command-line only
        parser.add_argument('--config', '-K', default=".modulesdb", help="The location of the JSON configuration file. Command-line options take precedence. Defaults to .modulesdb at the root of the directory being observed.")
        parser.add_argument('--walk', action="store_true", default=False, help="Whether to recusively push all of the files to the modules database before begining observation.")
        parser.add_argument("--debug", action="store_true", default=False, help="Print out some extra debugging information.")
        #parser.add_argument('--quiet', '-q', action="store_true", default=False, help="")
        parser.add_argument('--after', '-a', action="append", default=None, help="A script to be invoked after a file is pushed to the remote modules database. This is _not_ invoked after a directory walk (--walk). This also doesn't currently support piping input in or handling output or errors.")

        parser.add_argument("dir", nargs='?', help="The directory to watch. Defaults to the current working directory.", default=working_dir)

        # UGLY: Turn the Namesapce into a dictionary. Is this the only way to do this?
        args = copy.deepcopy(
            vars(
                # http://docs.python.org/2/library/sys.html#sys.argv
                parser.parse_args(command_line[1:])
            )
        )

        # Prune Nones from command-line args
        # http://stackoverflow.com/questions/2544710/how-i-can-get-rid-of-none-values-in-dictionary
        args = dict((k,v) for k,v in args.iteritems() if v is not None)

        # Get the preferences out of a dot file in the target directory
        # Command-line options take precedence
        prefs = {}
        pref_path = args['dir'] + "/" + args['config']
        if os.path.isfile(pref_path):
            print "Reading preferences from " + pref_path
            pref_file = open(pref_path, "r")
            prefs = json.load(pref_file)
            # print prefs

        # Overlay command-line arguments on top of the preferences read from the dot file
        prefs.update(args)

        def parse_perms(perms, prefix):
            "Turns something like ['a:A', 'b:B', 'a:C'] into {'a': ['A', 'C'], 'b': ['B']}"
            d = {}
            for p in perms:
                kv = p.split(':')
                k = prefix + kv[0]
                if k not in d:
                    d[k] = [kv[1]]
                else:
                    d[k].append(kv[1])
            return d

        # Ask for a password if it's not provided
        if prefs['auth'] in ['digest', 'basic'] and "password" not in prefs:
            prefs['password'] = getpass.getpass("Password for " + prefs['url'] + ": ")

        if not isinstance(prefs['permissions'], dict):
            prefs['permissions'] = parse_perms(prefs['permissions'], 'perm:')
        else:
            prefs['permissions'] = dict(('perm:' + k,v) for k,v in prefs['permissions'].iteritems())

        if "after" not in prefs:
            # UGLY: Reset proper default of after if it hasn't been set in the dot file or the command line
            prefs['after'] = []

        if prefs['debug']:
            print prefs

        return prefs

    config = get_configuration(os.getcwd(), sys.argv)

    modules_client = ModulesClient(config)

    # Start the script in a directory you want to observe
    BASEDIR = os.path.abspath(config['dir'])

    if config['walk']:
        print "Walking " + BASEDIR
        walk(BASEDIR, config['ignore'])

    print "Observing " + BASEDIR + "…"
    observe(BASEDIR, recursive=True, exclusions=config['ignore'], after=config.get('after'))
