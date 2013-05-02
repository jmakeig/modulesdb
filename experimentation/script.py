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
Reloads the front-most tab in Chrome on OSX. 
"""

import os
# http://stackoverflow.com/questions/2091235/mac-reloading-document-in-chrome-or-firefox
script = r"""osascript -e '
tell application "Google Chrome" to tell the active tab of its first window
    reload
end tell
'"""
os.system(script)