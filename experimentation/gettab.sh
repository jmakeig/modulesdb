#! /bin/bash

osascript -e '
tell application "Google Chrome" to tell the active tab of its first window
  set tabid to id
  return tabid as number
end tell
'