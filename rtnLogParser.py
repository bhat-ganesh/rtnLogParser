#!/usr/bin/python
# -*- coding: utf-8 -*-

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

bfsInit = ""
ipAddress = ""
macAddress = ""

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
    logIt("*****************************************************", LB_N, FORCE)
    logIt("                 RTN Log Parser", LB_N, FORCE)
    logIt("-----------------------------------------------------", LB_N, FORCE)
    logIt("Usage:", LB_Y, FORCE)
    logIt(sys.argv[0]+" logFile [logging]", LB_Y, FORCE)
    logIt("Example  : ./rtnLogParser.py slog", LB_Y, FORCE)
    logIt("-----------------------------------------------------", LB_N, FORCE)
    logIt("Required argument:", LB_Y, FORCE)
    logIt("@logFile : <path>/<logFile>", LB_Y, FORCE)
    logIt("-----------------------------------------------------", LB_N, FORCE)
    logIt("Optional argument:", LB_Y, FORCE)
    logIt("@logging : used for script debugging", LB_N, FORCE)
    logIt("         : Possible values = silent, normal, verbose", LB_N, FORCE)
    logIt("         : Default = normal", LB_N, FORCE)
    logIt("         : silent  : no logs", LB_N, FORCE)
    logIt("         : normal  : high level logs", LB_N, FORCE)
    logIt("         : verbose : function level logs", LB_Y, FORCE)
    logIt("*****************************************************", LB_N, FORCE)
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

def uiLoadedParser( line ):
    
    
    return False

#.............................................................................#

def bfsInitDoneParser( line ):
    #Jan 25 10:47:55 powertv syslog: DLOG|BFSUTILITY|EMERGENCY|BFS Init Done!
    global logHighlights
    global bfsInit

    pattern = re.compile("^.*\|BFS Init Done!$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*\|BFS', 'BFS', match.group())
        val = val.strip()

        if (bfsInit == val):
            logIt("bfsInitDoneParser: data already parsed, ignoring", LB_Y, VERBOSE)
            return True
        
        bfsInit = val
        logStr = " : "
        logIt("bfsInitDoneParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def bfsDnldCrashParser( line ):
    #Jan 27 11:23:28 powertv syslog: DLOG|BFS_GET_MODULE|EMERGENCY|get_filter_setting_for_module - 625 assertion failed
    global logHighlights

    pattern = re.compile("^.* - 625 assertion failed$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.* - 625 assertion failed$', '625 assertion failed', match.group())
        val = val.strip()

        logStr = " : BFS dnld crash CSCux30595 : "
        logIt("bfsDnldCrashParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#
def bfsBrokenPipeParser( line ):
    #Jan 20 12:28:14 powertv csp_CPERP: DLOG|BFS_GET_MODULE|ERROR|bool CSCI_BFS_API::ActiveContext::_serializeAndSendPacket(int, BfsIpc::PacketBuilder&) - 222 Error sending eIpc_BeginDownload packet to BFS server - send /tmp/bfs_server error Broken pipe
    global logHighlights

    pattern = re.compile("^.*BFS.* error Broken pipe$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*BFS.* error Broken pipe$', 'UI not available due to BFS error broken pipe', match.group())
        val = val.strip()

        logStr = " : "
        logIt("bfsBrokenPipeParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False
#.............................................................................#

def ipAddressParser( line ):
    #Jan 27 11:24:16 powertv syslog: DLOG|MDA|NORMAL|mda_network_get_string: IP address = 7.255.4.141
    global logHighlights
    global ipAddress

    pattern = re.compile("^.*: IP address = .*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*: IP address = ', '', match.group())
        val = val.strip()

        if (ipAddress == val):
            logIt("ipAddressParser: data already parsed, ignoring", LB_Y, VERBOSE)
            return True
        
        ipAddress = val
        logStr = " : IP Address : "
        logIt("ipAddressParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def macAddressParser( line ):
    #Dec 31 19:00:52 powertv syslog: DLOG|SAILMSG|ERROR|MAC ADDRESS OF BOX is:84:8D:C7:6D:41:E0
    global logHighlights
    global macAddress

    pattern = re.compile("^.*MAC ADDRESS OF BOX is.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*MAC ADDRESS OF BOX is:', '', match.group())
        val = val.strip()

        if (macAddress == val):
            logIt("macAddressParser: data already parsed, ignoring", LB_Y, VERBOSE)
            return True
        
        macAddress = val
        logStr = " : MAC Address : "
        logIt("macAddressParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recFail_lowDiskSpaceParser( line ):
    #Jan 25 06:00:04 powertv csp_CPERP: DLOG|DVR|Recording Failure|TimerHandler: Failure not enough disk space to record Breakfast Television AID 113
    global logHighlights

    pattern = re.compile("^.*Failure not enough disk space to record.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*Failure not enough disk space to record.*$', 'not enough disk space to record', match.group())
        val = val.strip()

        logStr = " : Recording failed : "
        logIt("recFail_lowDiskSpaceParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recFail_CLMstart( line ):
    #Jan 13 21:19:16 powertv csp_CPERP: DLOG|DVR|Recording Failure|FDR_log: DVRTXN050030: CLM UPDATE START
    global logHighlights

    pattern = re.compile("^.*CLM UPDATE START")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*CLM UPDATE START', 'Channel Map update has started', match.group())
        val = val.strip()

        logStr = " : Recording failed : "
        logIt("recFail_CLMstart" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recFail_CLMsuccess( line ):
    #Jan 13 21:19:38 powertv csp_CPERP: DLOG|DVR|Recording Failure|FDR_log: DVRTXN050040: CLM UPDATE SUCCESS
    global logHighlights

    pattern = re.compile("^.*CLM UPDATE SUCCESS")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*CLM UPDATE SUCCESS', 'Channel Map update successful', match.group())
        val = val.strip()

        logStr = " : Recording failed : "
        logIt("recFail_CLMsuccess" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recDel_lowDiskSpaceParser( line ):
    #Dec 29 10:09:33 powertv syslog: DLOG|DVR|Recording Failure|FDR_log: DVRTXN080030: 1006|Liberty's Kids|17|1450921500|RECORDING DELETED:DISK SPACE CRITICAL 95%
    global logHighlights

    pattern = re.compile("^.*RECORDING DELETED:DISK SPACE CRITICAL .*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*RECORDING DELETED:DISK SPACE CRITICAL', 'disk space critical', match.group())
        val = val.strip()

        logStr = " : Recording deleted : "
        logIt("recDel_lowDiskSpaceParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recNotPlayable_BadStateParser( line ):
    #Dec 22 16:14:53 powertv syslog: DLOG|MSP_DVR|ERROR|RecSession:stopConvert:808 RecordSessionStateError: Error Bad state: 3
    global logHighlights

    pattern = re.compile("^.*RecordSessionStateError: Error Bad state: 3$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*RecordSessionStateError:', '', match.group())
        val = val.strip()

        logStr = " : Recording not playable : "
        logIt("recNotPlayable_BadStateParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recNotPlayable_deAuthParser( line ):
    #Nov 13 10:49:26 powertv csp_CPERP: DLOG|CA_CAK|NORMAL|****** ECM 16 Digital_Response, result 0xb
    global logHighlights

    pattern = re.compile("^.*ECM 16 Digital_Response, result 0xb$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Recording not playable : due to deauthorization"
        logIt("recNotPlayable_deAuthParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def blackScreen_Err19Parser( line ):
    #Jan 11 09:26:29 powertv csp_CPERP: DLOG|MSP_MPLAYER|ERROR|DisplaySession:stop:1352 cpe_media_Stop error -19
    global logHighlights

    pattern = re.compile("^.*cpe_media_Stop error -19$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*cpe_media_Stop error -19', 'cpe_media_Stop2yy error -19', match.group())
        val = val.strip()

        logStr = " : CSCup37738 Black Screen on all channels : due to "
        logIt("blackScreen_Err19Parser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def blackScreen_vodStreamIssueParser( line ):
    #Dec 21 15:35:08 powertv csp_CPERP: DLOG|MSP_MPLAYER|ERROR|Zapper:handleEvent:225 PsiTimeOutError: Warning - PSI not available. DoCallback – ContentNotFound!!
    global logHighlights

    pattern = re.compile("^.*PSI not available.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : VOD playback black screen : due to stream issue"
        logIt("blackScreen_vodStreamIssueParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def blackScreen_signalStreamIssueParser( line ):
    #Dec 20 03:50:21 powertv csp_CPERP: DLOG|MSP_MPLAYER|EMERGENCY|Zapper:handleEvent:220 Warning - Tuner lock timeout.May be signal strength is low or no stream on tuned frequency!!
    global logHighlights

    pattern = re.compile("^.*signal strength is low or no stream.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Black screen : stream issue - low signal or no stream"
        logIt("blackScreen_signalStreamIssueParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def blackScreen_patTimeoutParser( line ):
    #Dec 11 15:36:10 powertv syslog: DLOG|MSP_PSI|ERROR|Psi:dispatchEvent:125 PsiTimeOutError: Time out while waiting for PAT
    global logHighlights

    pattern = re.compile("^.*PsiTimeOutError: Time out while waiting for PAT$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Black screen : PAT timeout"
        logIt("blackScreen_patTimeoutParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def blackScreen_pmtNoInfoParser( line ):
    #Nov 11 00:10:17 powertv csp_CPERP: DLOG|MSP_MPLAYER|ERROR|Zapper:GetComponents:1717 PSI/PMT Info Not found
    global logHighlights

    pattern = re.compile("^.*PMT Info Not found$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Black screen : stream issue - no pmt"
        logIt("blackScreen_pmtNoInfoParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def stuck04Parser( line ):
    #Dec 31 19:01:37 powertv csp_CPERP: DLOG|SAM|ERROR|Thread Setname Failed:threadRetValue:0
    global logHighlights

    pattern = re.compile("^.*SAM.*Thread Setname Failed.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Stuck at -04- : due to SAM not ready "
        logIt("stuck04Parser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def serviceDeAuthParser( line ):
    #Nov 21 05:25:25 powertv csp_CPERP: DLOG|MSP_DVR|ERROR|dvr:dispatchEvent:1022 Service DeAuthorized by CAM
    global logHighlights

    pattern = re.compile("^.*Service DeAuthorized by CAM$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Service deauthorized "
        logIt("serviceDeAuthParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def noAuthECMParser( line ):
    #Nov 21 05:25:25 powertv csp_CPERP: DLOG|CA_CAK|ERROR|PkCakDvrRecordSession_cronus.cpp:383 Async No authorized ECM in CA message
    global logHighlights

    pattern = re.compile("^.*No authorized ECM in CA message$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : No authorized ECM in CA message "
        logIt("noAuthECMParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def channelNAParser( line ):
    #Nov 13 01:43:41 powertv syslog: DLOG|SDV|ERROR|ccmisProtocol.cpp HandleProgramSelectIndication Channel is not available
    global logHighlights

    pattern = re.compile("^.*Channel is not available$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Channel is not available"
        logIt("channelNAParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def uiErrLoadingParser( line ):
    #Nov 12 21:20:30 powertv bfsdnld: DLOG|BFS_GET_MODULE|ERROR|directory_update_timeout directory update taking more than 120 seconds
    global logHighlights

    pattern = re.compile("^.*directory update taking more than 120 seconds$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Stuck on -05- due to ui error loading"
        logIt("uiErrLoadingParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def bootUpSequenceParser( line ):
    #Dec 31 19:01:13 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling:      Application started => Waiting for SessInit : 49.64 seconds, total time: 91.46 seconds (BUFFERED)
    #Dec 31 19:01:29 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -00- SessInit is ready => Waiting for Hub Id : 2.02 seconds, total time: 93.48 seconds (BUFFERED)
    #Dec 31 19:01:29 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -01- Hub Id is ready => Waiting for SI : 15.04 seconds, total time: 108.53 seconds (BUFFERED)
    #Jan 27 11:21:07 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -02- SI is ready => Waiting for BFS : 65.44 seconds, total time: 173.96 seconds (BUFFERED)
    #Jan 27 11:21:07 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -03- BFS is ready => Waiting for SAM : 0.02 seconds, total time: 173.99 seconds
    #Jan 27 11:21:09 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -04- SAM is ready => Waiting for global config : 2.03 seconds, total time: 176.01 seconds
    #Jan 27 11:21:16 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -05- Global config is ready => Launching UI : 2.02 seconds, total time: 178.03 seconds
    #Jan 27 11:24:50 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling:      UI launched => System ready : 218.45 seconds, total time: 396.48 seconds
    global logHighlights

    pattern = re.compile("^.*Bootup profiling:.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub( ' =>.*$', '', re.sub('^.*Bootup profiling: ', '', match.group()))
        val = val.strip()
        
        logStr = " : Bootup step : "
        logIt("bootUpSequenceParser" + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line" + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

parsers = [
        keyPressParser,
        boxTypeParser,
        buildInfoParser,
        uiLoadedParser,
        bfsInitDoneParser,
        bfsDnldCrashParser,
        bfsBrokenPipeParser,
        ipAddressParser,
        macAddressParser,
        recFail_lowDiskSpaceParser,
        recFail_CLMstart,
        recFail_CLMsuccess,
        recDel_lowDiskSpaceParser,
        recNotPlayable_BadStateParser,
        recNotPlayable_deAuthParser,
        blackScreen_Err19Parser,
        blackScreen_vodStreamIssueParser,
        blackScreen_signalStreamIssueParser,
        blackScreen_patTimeoutParser,
        blackScreen_pmtNoInfoParser,
        stuck04Parser,
        serviceDeAuthParser,
        noAuthECMParser,
        channelNAParser,
        uiErrLoadingParser,
        bootUpSequenceParser
        ]

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
    logIt("ERR: invalid use", LB_Y, FORCE)
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
