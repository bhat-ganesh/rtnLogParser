#!/usr/bin/python

import sys
import re

#-----------------------------------------------------------------------------#

# globals

NORMAL = "normal"
VERBOSE = "verbose"
FORCE = "force"

LB_Y = "line break yes"
LB_N = "line break no"

loggingMode = ""
logHighlights = ""
logSearchInfo = "_rtnLogParser_"

keyCounter = 0
keyCode = 0
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

boxType = ""
boxTypeMap = {
    '9k'  : 'G8 9K',
    '8k'  : 'G6 8K',
    '4k'  : 'G6 4K',
    '10k' : 'G10 10K'
}

#-----------------------------------------------------------------------------#

# functions

def logIt( message, breakLine=LB_Y, displayLog=NORMAL ):
    global loggingMode

    if ( (loggingMode == displayLog) or (loggingMode == VERBOSE) or (displayLog == FORCE) ):
        if (displayLog == VERBOSE):
            message = "[VERBOSE] " + message
        if (breakLine == LB_Y):
            message = message + "\n"

        print message
    return

#.............................................................................#

def usageInfo():
    logIt("*************************************", LB_N, FORCE)
    logIt("            RTN log parser", LB_N, FORCE)
    logIt("-------------------------------------", LB_N, FORCE)
    logIt("Usage:", LB_Y, FORCE)
    logIt(sys.argv[0]+" logFile [logging]", LB_Y, FORCE)
    logIt("-------------------------------------", LB_N, FORCE)
    logIt("Required argument:", LB_N, FORCE)
    logIt("@logFile : <path>/<logFile>", LB_Y, FORCE)
    logIt("-------------------------------------", LB_N, FORCE)
    logIt("Optional argument:", LB_N, FORCE)
    logIt("@logging : silent, normal, verbose", LB_N, FORCE)
    logIt("         : Default = normal", LB_N, FORCE)
    logIt("  silent : no logs", LB_N, FORCE)
    logIt("  normal : high level logs", LB_N, FORCE)
    logIt(" verbose : function level logs", LB_Y, FORCE)
    logIt("*************************************", LB_N, FORCE)
    return

#.............................................................................#

def dateTimeParser( line ):
    dateTimePattern = re.compile("... .. ..:..:..")
    matchDateTime = re.search(dateTimePattern, line)
    dateTime = matchDateTime.group()
    # logIt("dateTimeParser: " + dateTime, LB_N, VERBOSE)
    return dateTime

#.............................................................................#

def keyPressParser( line ):
    #Jan 27 16:53:41 powertv syslog: DLOG|GALIO|NORMAL| -- sending key 462 --
    global logHighlights
    global keyCounter
    global keyCode
    
    pattern = re.compile("^.*\| -- sending key .* --$")
    match = re.search(pattern, line)

    if match:
        val = re.sub(' --', '', re.sub('^.*\| -- sending key ', '', match.group()))
        val = val.strip()
        
        try:
            val = keyMap[val]
        except:
            val = val
        
        if (keyCode == val):
            logIt("keyPressParser: ignoring second key signal", LB_Y, VERBOSE)
            return True
        
        keyCode = val
        logStr = " : Key Press : "
        keyCounter = keyCounter + 1
        logIt("keyPressParser" + logStr + val, LB_N, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def boxTypeParser( line ):
    #Image created for 9k box.
    global logHighlights
    global boxType

    pattern = re.compile("^Image created for .* box.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub( ' box.*$', '', re.sub('^Image created for ', '', match.group()))
        val = val.strip()

        try:
            val = boxTypeMap[val]
        except:
            val = val

        if (boxType == val):
            logIt("boxTypeParser: data already parsed, ignoring", LB_Y, VERBOSE)
            return True
        
        boxType = val
        logStr = " : Box Type : "
        logIt("boxTypeParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def buildInfoParser( line ):
    return False

#.............................................................................#

def bootTimeParser( line ):
    return False

#.............................................................................#

def uiLoadedParser( line ):
    return False

#.............................................................................#

def networkObtainedParser( line ):
    return False

#.............................................................................#

parsers = [
        keyPressParser,
        boxTypeParser,
        buildInfoParser,
        bootTimeParser,
        uiLoadedParser,
        networkObtainedParser
        ]

#.............................................................................#

def lineParser( line ):
    for parser in parsers:
        # logIt("Parsing line" + str(lineCount) + " calling " + str(parser.__name__), LB_N, VERBOSE)
        ret = parser(line);
        if ret:
            break
    return

#-----------------------------------------------------------------------------#

# main

try:
    inFile = sys.argv[1]
    f = open(inFile, "r")
except:
    logIt("ERR: invalid use", LB_N, FORCE)
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

#.............................................................................#

# post process

if logHighlights:
    outFile = inFile+"_changed"
    f = open(outFile, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()
    
    logIt(inFile + " processed successfully.", LB_N)
    logIt("Following are highlights in " + inFile + ":")
    
    logIt("************************************************", LB_N)
    logIt("Total number of key presses = " + str(keyCounter))
    logIt(logHighlights.strip(),0)
    logIt("************************************************")
    
    logIt("Log highlights are also embedded in output file : " + outFile, LB_N)
    logIt("Look for " + logSearchInfo + " in " + outFile)
    
    logIt("To compare files:", LB_N)
    logIt("vimdiff " + outFile + " " + inFile)
    
    logIt("To use changed file:", LB_N)
    logIt("mv " + outFile + " " + inFile)
else:
    logIt("WARN: nothing to parse in " + inFile)

#-----------------------------------------------------------------------------#
