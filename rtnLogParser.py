#!/usr/bin/python

import sys
import re

#######################################################################################

# globals

keyMap = {
    '48' : '0',
    '49' : '1',
    '50' : '2',
    '51' : '3',
    '52' : '4',
    '53' : '5',
    '54' : '6',
    '55' : '7',
    '56' : '8',
    '57' : '9',
    '13' : 'select/ok',
    '33' : 'page+',
    '34' : 'page-',
    '38' : 'up',
    '40' : 'down',
    '37' : 'left',
    '39' : 'right',
    '458' : 'guide',
    '405' : 'A',
    '406' : 'B',
    '403' : 'C',
    '404' : 'D',
    '462' : 'menu',
    '457' : 'info',
    '409' : 'standby',
    '427' : 'ch+',
    '428' : 'ch-',
    '415' : 'play',
    '19'  : 'pause',
    '413' : 'stop',
    '416' : 'record',
    '417' : 'fwd',
    '412' : 'rew',
    '1073741868' : 'exit',
    '1073742341' : 'fav',
    '1073741981' : 'live',
    '1073741999' : 'last',
    '1073742336' : '#',
    '1073742337' : '*',
    '1073742340' : 'skip',
    '1073742341' : 'settings',
    '1073742342' : 'pip on/off',
    '1073742343' : 'pip swap',
    '1073742337' : 'pip move',
    '1073742345' : 'pip ch+',
    '1073742346' : 'pip ch-',
    '1073742347' : 'video source',
    '1073742359' : 'list',
    '1073742360' : 'day+',
    '1073742361' : 'day-'
}

counter = 0
keyCounter = 0
logSearchInfo = "_rtnLogParser_"
keyPressInfo = "<LINE> : <TIME> : <KEY>\n\n"

#######################################################################################

# patterns

keyPressPattern = re.compile("^.*\|.sending key.*: .*$")
firstKeyPattern = re.compile("\+key\:")
keyTimePattern = re.compile("... .. ..:..:..")

#######################################################################################

# functions

def usageInfo():
    print ">>>>>"
    print "RTN log parser"
    print "Usage: "+sys.argv[0]+" <path>/<logfile>"
    print "Look for: " + logSearchInfo
    print "Output: <path>/<logfile>_changed"
    print "<<<<<"
    return

def keyPressParser( line ):
    global counter
    global keyCounter
    global keyPressInfo

    matchKeyPress = re.search(keyPressPattern, line)
    if matchKeyPress:
        counter = counter+1
        keyCode = re.sub('^.*\|.key.*: ', '',matchKeyPress.group())
        keyCode = keyCode.strip()
        try:
            keyName = keyMap[keyCode];
        except:
            keyName = keyCode
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo +" KEY_PRESS = " + keyName + "\n"

        matchFirstKeyPress = re.search(firstKeyPattern, line)
        if matchFirstKeyPress:
            keyCounter = keyCounter + 1
            matchKeyTime = re.search(keyTimePattern, line)
            keyTime = matchKeyTime.group()
            keyPressInfo += str(lineCount+1) + " : " + keyTime + " : " + keyName + "\n"
    return

def lineParser( line ):
    keyPressParser( line )
    return

#######################################################################################

# main

try:
    inFile = sys.argv[1]
    f = open(inFile, "r")
except:
    print "ERR: invalid use"
    usageInfo()
    quit()

print ">>>>>"
print "Processing file: " + inFile
contents = f.readlines()
f.close()

with open(sys.argv[1], 'r') as file:
    for lineCount, line in enumerate(file):
        lineParser(line)

# post process

if counter:
    outFile = inFile+"_changed"
    f = open(outFile, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()
    print inFile + " processed successfully.\n"
    print "Total number of key presses = " + str(keyCounter)
    print keyPressInfo
    
    print "Output file : " + outFile
    print "Look for " + logSearchInfo + " in the log file."
    print "\nTo compare files before use run:"
    print "vimdiff " + outFile + " " + inFile
    print "\nTo use changed file run:"
    print "mv " + outFile + " " + inFile + "\n"
print "<<<<<"

#######################################################################################
