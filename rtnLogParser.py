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
keySignalIgnore = 0
logSearchInfo = "_rtnLogParser_"
logHighlights = ""
loggingMode = ""
NORMAL = "normal"
VERBOSE = "verbose"
FORCE = "force"

#######################################################################################

# patterns


#######################################################################################

# functions

def logIt( message, newLine=1, displayLog=NORMAL):
    global loggingMode
    newLineStr = "\n"
    verboseStr = "[Verbose] "

    if ( (loggingMode == displayLog) or (loggingMode == VERBOSE) or (displayLog == FORCE) ):
        if (displayLog == VERBOSE):
            message = verboseStr + message
        if newLine:
            message = message + newLineStr

        print message
    return

def usageInfo():
    logIt("*************************************", 0, FORCE)
    logIt("            RTN log parser", 0, FORCE)
    logIt("-------------------------------------", 0, FORCE)
    logIt("Usage:", 1, FORCE)
    logIt(sys.argv[0]+" logFile [logging]", 1, FORCE)
    logIt("-------------------------------------", 0, FORCE)
    logIt("Required argument:", 0, FORCE)
    logIt("@path : <path>/<logFile>", 1, FORCE)
    logIt("-------------------------------------", 0, FORCE)
    logIt("Optional argument:", 0, FORCE)
    logIt("@logging   : silent, normal, verbose", 0, FORCE)
    logIt("             Default = normal", 0, FORCE)
    logIt("   silent  : no logs", 0, FORCE)
    logIt("   normal  : high level logs", 0, FORCE)
    logIt("   verbose : function level logs", 1, FORCE)
    logIt("*************************************", 0, FORCE)
    return

def keyPressParser( line ):
    global counter
    global keyCounter
    global logHighlights
    global keySignalIgnore
    
    keyPressPattern = re.compile("^.*\|.key.*: .*$")
    keyTimePattern = re.compile("... .. ..:..:..")

    matchKeyPress = re.search(keyPressPattern, line)
    if matchKeyPress:
        
        if keySignalIgnore :
            logIt("keyPressParser: ignoring second key signal", 1, VERBOSE)
            keySignalIgnore = 0;
            return
        
        keySignalIgnore = 1
        counter = counter+1
        keyCounter = keyCounter + 1
        
        keyCode = re.sub('^.*\|.key.*: ', '',matchKeyPress.group())
        keyCode = keyCode.strip()
        try:
            keyName = keyMap[keyCode];
        except:
            keyName = keyCode
        
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo +" KEY_PRESS = " + keyName + "\n"

        matchKeyTime = re.search(keyTimePattern, line)
        keyTime = matchKeyTime.group()
        logHighlights += "line" + str(lineCount+1) + " : " + keyTime + " : " + keyName + "\n"
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
    logIt("ERR: invalid use", 1, FORCE)
    usageInfo()
    quit()

try:
    loggingMode = sys.argv[2]
except:
    loggingMode = NORMAL

logIt("Processing file: " + inFile)
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
    
    logIt(inFile + " processed successfully.", 0)
    logIt("Following are highlights in " + inFile + ":")
    
    logIt("****************************************************************************",0)
    logIt("Total number of key presses = " + str(keyCounter))
    logIt(logHighlights.strip(),0)
    logIt("****************************************************************************")
    
    logIt("Log highlights are also embedded in output file : " + outFile, 0)
    logIt("Look for " + logSearchInfo + " in " + outFile)
    
    logIt("To compare files:", 0)
    logIt("vimdiff " + outFile + " " + inFile)
    
    logIt("To use changed file:",0)
    logIt("mv " + outFile + " " + inFile)
else:
    logIt("WARN: nothing to parse in " + inFile)

#######################################################################################
