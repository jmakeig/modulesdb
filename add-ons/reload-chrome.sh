#! /bin/bash

osascript -e '
tell application "Google Chrome" to tell the active tab of its first window
    reload
end tell
'