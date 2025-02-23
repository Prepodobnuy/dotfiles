#!/usr/bin/fish

set filename (hyprshotgun region)
wl-copy <$filename
rm $filename
