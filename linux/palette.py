#!/usr/bin/env python
# Copyright (C) 2006 by Johannes Zellner, <johannes@zellner.org>
# modified by mac@calmar.ws to fit my output needs
# modified by crncosta@carloscosta.org to fit my output needs

# Original source: https://github.com/incitat/eran-dotfiles/blob/master/bin/terminalcolors.py

import sys
import os

def echo(msg):
    os.system('echo -n "' + str(msg) + '"')

def out(n):
    os.system("tput setab " + str(n) + "; echo -n " + ("\"% 4d\"" % n))
    os.system("tput setab 0")

# normal colors 1 - 16
os.system("tput setaf 16")
for n in range(8):
    out(n)
echo("\n")
for n in range(8, 16):
    out(n)
echo("\n")
echo("\n")

echo("\033[0m00:Normal \033[01m01:Bold \033[0;04m04:Underscore\033[0;05m 05:Blink \033[0;07m07:Reverse\033[0m\n")
echo("\n")

os.system("tput setaf 16")
for y in range(0,12):

    if y == 6:
        echo ("\n")
    for z in range(0,6):
        out(16+y*6+z)
    echo (" ")

    for z in range(72,78):
        out(16+y*6+z)
    echo(" ")

    for z in range(144,150):
        out(16+y*6+z)
    echo("\n")
echo("\n")

for n in range(232, 256):
    out(n)
    if n == 237 or n == 243 or n == 249:
        echo("\n")

echo("\n")
os.system("tput setaf 7")
os.system("tput setab 0")
