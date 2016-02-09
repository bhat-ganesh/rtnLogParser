#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import argparse
import textwrap
import os
import subprocess

#-----------------------------------------------------------------------------#

# globals

NORMAL = "normal"
QUIET = "quiet"
VERBOSE = "verbose"
FORCE = "force"

LB_Y = "line break yes"
LB_N = "line break no"

loggingMode = NORMAL
logHighlights = ""
logSearchInfo = "_rtnLogParser_"

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

vodPlaybackSpeedMap = {
    '100.000000'    : 'normal speed = 1x',
    '0.000000'      : 'paused speed = 0x',
    '750.000000'    : 'fast forward speed = 7.5x',
    '3000.000000'   : 'fast forward speed = 30x',
    '6000.000000'   : 'fast forward speed = 60x',
    '-750.000000'   : 'rewind speed = -7.5x',
    '-3000.000000'  : 'rewind speed = -30x',
    '-6000.000000'  : 'rewind speed = -60x'
}

#-----------------------------------------------------------------------------#

# functions

def logIt(message, breakLine=LB_Y, displayLog=NORMAL):
    global loggingMode

    if ((loggingMode == displayLog) or (loggingMode == VERBOSE) or (displayLog == FORCE)):
        if (displayLog == VERBOSE):
            message = "[VERBOSE] " + message
        if (breakLine == LB_Y):
            message = message + "\n"

        print message
    return

#.............................................................................#

def dateTimeParser( line ):
    dateTimePattern = re.compile("... .. ..:..:..")
    matchDateTime = re.search(dateTimePattern, line)
    dateTime = matchDateTime.group()
    # logIt("sys._getframe().f_code.co_name: " + dateTime, LB_N, VERBOSE)
    return dateTime

#.............................................................................#

def keyPressParser( line ):
    #Jan 27 16:53:41 powertv syslog: DLOG|GALIO|NORMAL| -- sending key 462 --
    global logHighlights
    global keyCode

    pattern = re.compile("^.*\| -- sending key .* --.*$")
    match = re.search(pattern, line)

    if match:
        val = re.sub(' --', '', re.sub('^.*\| -- sending key ', '', match.group()))
        val = val.strip()
        
        try:
            val = keyMap[val]
        except:
            val = val
        
        if (keyCode == val):
            logIt(sys._getframe().f_code.co_name + " : ignoring second key signal", LB_Y, VERBOSE)
            keyCode = ""
            return True
        
        keyCode = val
        logStr = " : Key Press : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_N, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
            logIt(sys._getframe().f_code.co_name + ": data already parsed, ignoring", LB_Y, VERBOSE)
            return True
        
        boxType = val
        logStr = " : Box Type : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def buildInfoParser( line ):
    

    return False

#.............................................................................#

def bfsInitDoneParser( line ):
    #Jan 25 10:47:55 powertv syslog: DLOG|BFSUTILITY|EMERGENCY|BFS Init Done!
    global logHighlights
    global bfsInit

    pattern = re.compile("^.*\|BFS Init Done!.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*\|BFS', 'BFS', match.group())
        val = val.strip()

        if (bfsInit == val):
            logIt(sys._getframe().f_code.co_name + ": data already parsed, ignoring", LB_Y, VERBOSE)
            return True
        
        bfsInit = val
        logStr = " : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def bfsDnldCrashParser( line ):
    #Jan 27 11:23:28 powertv syslog: DLOG|BFS_GET_MODULE|EMERGENCY|get_filter_setting_for_module - 625 assertion failed
    global logHighlights

    pattern = re.compile("^.* - 625 assertion failed.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.* - 625 assertion failed$', '625 assertion failed', match.group())
        val = val.strip()

        logStr = " : BFS dnld crash CSCux30595 : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def bfsBrokenPipeParser( line ):
    #Jan 20 12:28:14 powertv csp_CPERP: DLOG|BFS_GET_MODULE|ERROR|bool CSCI_BFS_API::ActiveContext::_serializeAndSendPacket(int, BfsIpc::PacketBuilder&) - 222 Error sending eIpc_BeginDownload packet to BFS server - send /tmp/bfs_server error Broken pipe
    global logHighlights

    pattern = re.compile("^.*BFS.* error Broken pipe$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : BFS error broken pipe "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def bfsEPGDataDownloadFailureParser( line ):
    #Jan 28 11:17:18 powertv epg: DLOG|EPG_LOAD|SIGNIFICANT_EVENT|gi_load: GI for day 2 not found either in disk cache nor memory cache, check wheather it is loading
    global logHighlights

    pattern = re.compile("^.*gi_load: GI for day 2 not found either in disk cache nor memory cache, check wheather it is loading.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : BFS is up but NOT able to download EPG data "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def ipAddressParser( line ):
    #Jan 28 12:20:13 powertv syslog: doc_StoreParameter: Host IPv4 address: 100.109.176.144.
    global logHighlights

    pattern = re.compile("^.*: Host IPv4 address: .*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*: Host IPv4 address: ', '', match.group())
        val = val.strip()

        logStr = " : IP Address : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def macAddressParser( line ):
    #Jan 28 12:19:15 powertv syslog: DLOG|MDA|ERROR|mda_network_init:336: MAC address = 68:EE:96:6F:15:B8
    global logHighlights

    pattern = re.compile("^.*mda_network_init.*MAC address = .*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*mda_network_init.*MAC address = ', '', match.group())
        val = val.strip()

        logStr = " : MAC Address : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recordingStartedParser( line ):
    # Jan 29 13:02:57 powertv syslog: DLOG|MSP_MPLAYER|EMERGENCY|IMediaPlayer:IMediaPlayerSession_PersistentRecord:685 sess: 0x3ab3ee0  recordUrl: sadvr://dElWnhPo  start: 0.000000   stop: -2.000000    **SAIL API**
    global logHighlights

    pattern = re.compile("^.*IMediaPlayer:IMediaPlayerSession_PersistentRecord.*recordUrl.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : recording started"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recordingStarted2Parser( line ):
    #Jan 29 15:10:30 powertv syslog: DLOG|GALIO|NORMAL|SCHED: record added dvr://recording/00000000-0000-0000-0000-00000000000000000641 rec [@03989318: dvr://recording/00000000-0000-0000-0000-00000000000000000641 play 0 state mom_recording_RECORDING rel @0396c668 Zooville Zooo]
    #Jan 27 11:24:56 powertv syslog: DLOG|GALIO|NORMAL|SCHED: record added dvr://recording/00000000-0000-0000-0000-00000000000000000570 rec [@01a57220: dvr://recording/00000000-0000-0000-0000-00000000000000000570 play 1 state mom_recording_RECORDING rel @01a57ee0 The Price Is Right]
    global logHighlights

    pattern = re.compile("^.*GALIO\|NORMAL.*record added.*_RECORDING.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub( '].*$', '', re.sub('^.*GALIO\|NORMAL.*record added.*_RECORDING rel @........ ', '', match.group()))
        val = val.strip()

        logStr = " : start recording program = "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recordingStoppedParser( line ):
    # Jan 29 13:04:28 powertv syslog: DLOG|MSP_MRDVR|ERROR|MRDvrServer:Csci_Msp_MrdvrSrv_NotifyRecordingStop:112 URL is : sctetv://003
    global logHighlights

    pattern = re.compile("^.*Csci_Msp_MrdvrSrv_NotifyRecordingStop.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : recording stopped"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recordingStopped2Parser( line ):
    # Jan 29 15:12:42 powertv syslog: DLOG|GALIO|NORMAL|SCHED: record updated dvr://recording/00000000-0000-0000-0000-00000000000000000641 rec [@03989318: dvr://recording/00000000-0000-0000-0000-00000000000000000641 play 1 state mom_recording_STOPPED rel <NULL> Zooville]
    global logHighlights

    pattern = re.compile("^.*GALIO\|NORMAL.*record updated.*_STOPPED.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub( '].*$', '', re.sub('^.*GALIO\|NORMAL.*record updated.*_STOPPED rel <NULL> ', '', match.group()))
        val = val.strip()

        logStr = " : recording stopped = "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recordingDeletedParser( line ):
    # Jan 29 13:05:15 powertv syslog: DLOG|DVRUTIL|ERROR|Successfully Deleted file /mnt/dvr0/vNA4T1Rn
    global logHighlights

    pattern = re.compile("^.*DVRUTIL.*Successfully Deleted file.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : recording deleted"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recordingDeleted2Parser( line ):
    # Jan 29 15:19:06 powertv syslog: DLOG|GALIO|NORMAL|SCHED: record deleted (state != mom_recording_RECORDING) dvr://recording/00000000-0000-0000-0000-00000000000000000641 rec [@03989318: dvr://recording/00000000-0000-0000-0000-00000000000000000641 play 1 state mom_recording_STOPPED rel <NULL> Zooville]
    global logHighlights

    pattern = re.compile("^.*GALIO\|NORMAL.*record deleted.*_STOPPED.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub( '].*$', '', re.sub('^.*GALIO\|NORMAL.*record deleted.*_STOPPED rel <NULL> ', '', match.group()))
        val = val.strip()
        
        logStr = " : recording deleted = "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recordingPlaybackStartedParser( line ):
    # Jan 29 13:11:57 powertv syslog: DLOG|MSP_MPLAYER|EMERGENCY|IMediaPlayer:IMediaPlayerSession_Load:434  URL: sadvr://mnt/dvr0/6oxGuu4M  session: 0x1b0a978     **SAIL API**
    global logHighlights

    pattern = re.compile("^.*IMediaPlayer:IMediaPlayerSession_Load.*URL: sadvr:.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : recording playback started"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#
def recordingPlaybackStarted2Parser( line ):
    # Jan 29 15:14:01 powertv syslog: DLOG|GALIO|NORMAL|package://5415C3E6-8DBEB1FC/js/zapp_modes.js at line 375 ZapperModeVideo::Connect is now Playing [object MOMScheduledRecording] : Name : dvr://recording/00000000-0000-0000-0000-00000000000000000641 : Zooville
    global logHighlights

    pattern = re.compile("^.*GALIO\|NORMAL.*Connect is now Playing.*dvr.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*GALIO\|NORMAL.*Connect is now Playing.*dvr.* : ', '', match.group())
        val = val.strip()
        
        logStr = " : recording playback started = "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recordingFailureParser( line ):
    #Dec 29 10:09:33 powertv syslog: DLOG|DVR|Recording Failure|FDR_log: DVRTXN080030: 1006|Liberty's Kids|17|1450921500|RECORDING DELETED:DISK SPACE CRITICAL 95%
    #Jan 25 06:00:04 powertv csp_CPERP: DLOG|DVR|Recording Failure|TimerHandler: Failure not enough disk space to record Breakfast Television AID 113
    #Jan 13 21:19:16 powertv csp_CPERP: DLOG|DVR|Recording Failure|FDR_log: DVRTXN050030: CLM UPDATE START
    #Jan 13 21:19:38 powertv csp_CPERP: DLOG|DVR|Recording Failure|FDR_log: DVRTXN050040: CLM UPDATE SUCCESS
    global logHighlights

    pattern = re.compile("^.*Recording Failure.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*RECORDING DELETED:DISK SPACE CRITICAL', 'disk space critical', match.group())
        if (val == match.group()):
            val = re.sub('^.*Failure not', 'not', match.group())
            if (val == match.group()):
                val = re.sub('^.*CLM UPDATE START', 'Channel Map update has started', match.group())
                if (val == match.group()):
                    val = re.sub('^.*CLM UPDATE SUCCESS', 'Channel Map update successful', match.group())
        val = val.strip()
        
        logStr = " : Recording failed : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def recNotPlayable_BadStateParser( line ):
    #Dec 22 16:14:53 powertv syslog: DLOG|MSP_DVR|ERROR|RecSession:stopConvert:808 RecordSessionStateError: Error Bad state: 3
    global logHighlights

    pattern = re.compile("^.*RecordSessionStateError: Error Bad state: 3$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Recording not playable : Error Bad state: 3"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def blackScreen_Err19Parser( line ):
    #Jan 11 09:26:29 powertv csp_CPERP: DLOG|MSP_MPLAYER|ERROR|DisplaySession:stop:1352 cpe_media_Stop error -19
    global logHighlights

    pattern = re.compile("^.*cpe_media_Stop error -19$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Black Screen on all channels : due to cpe_media_Stop2 error -19 CSCup37738 "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
        logStr = " : Black screen due to no authorized ECM in CA message "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def uiErrLoadingParser( line ):
    #Nov 12 21:20:30 powertv bfsdnld: DLOG|BFS_GET_MODULE|ERROR|directory_update_timeout directory update taking more than 120 seconds
    global logHighlights

    pattern = re.compile("^.*directory update taking more than 120 seconds.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Stuck on -05- due to ui error loading"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def certInfoParser( line ):
    # Feb  1 10:04:55 powertv syslog:  Settop Extender Bridge: UpnPInitializeSSLContext - Retrying (# 182) to get DOCSIS cert info!
    global logHighlights

    pattern = re.compile("^.*Retrying .* to get DOCSIS cert info.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Stuck on -05- due to failure in getting docsis cert info"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def uiExceptionParser( line ):
    #Sep 11 15:08:44 powertv root: SCRIPT: unhandled exception: Attempt to convert null or undefined value recording to Object
    #Sep 11 19:08:52 powertv root: SCRIPT: unhandled exception: SETTINGS.CheckboxPane() is not defined
    global logHighlights

    pattern = re.compile("^.*SCRIPT: unhandled exception.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : exception in rtnui !!!"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def notStagedParser( line ):
    #Jan 28 12:47:57 powertv syslog: DLOG|DNCS_SETTINGS|EMERGENCY|SetStagingstatus:94 isStagingDefsApplied: 0 isHubSpecficStagingDefsApplied: 1 isAddressableStaged: 0
    global logHighlights

    pattern = re.compile("^.*SetStagingstatus.* isStagingDefsApplied: 0.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Stuck on -05- after Factory Restore due to not staged CSCux18653/CSCuu47200"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def grpDefParser( line ):
    # Feb  1 11:26:52 powertv csp_CPERP: DLOG|DLM|NORMAL|[downloadAppAndArtFile][96] Value of sam_isGrpDefParsed from BFS() = 0
    global logHighlights

    pattern = re.compile("^.*downloadAppAndArtFile.* Value of sam_isGrpDefParsed from.* = 0.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Stuck on -05- download manager is blocked on downloading grps_defs.txt"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
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
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def network2WayReadyParser( line ):
    #Jan 28 12:21:13 powertv syslog: DLOG|SPM_VODCTLG|ERROR|vod-internal.cpp:void* tr_VodInit(void*):959: Network is two way and System is Ready
    global logHighlights

    pattern = re.compile("^.*Network is two way and System is Ready.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Network is two way and System is Ready"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def maintSequenceParser( line ):
    # Jan 28 12:22:01 powertv syslog: DLOG|DLM|EMERGENCY|[sendSailMessage][1517] dlmWarningType:MAINT_DOWNLOAD_WARNING
    # Jan 28 12:22:21 powertv syslog: DLOG|DLM|EMERGENCY|[sendSailMessage][1517] dlmWarningType:MAINT_DOWNLOAD_REQUEST
    # Jan 28 12:23:00 powertv syslog: DLOG|DLM|EMERGENCY|[sendSailMessage][1517] dlmWarningType:MAINT_DOWNLOAD_COMPLETE
    global logHighlights

    pattern = re.compile("^.*MAINT_DOWNLOAD_.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('^.*MAINT_DOWNLOAD_', '', match.group())
        val = val.strip()
        
        logStr = " : Maintenance download : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def vodSessionSetUpFailureParser( line ):
    #Jan 28 14:41:31 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|SeaChange_SessCntrl:HandleSessionConfirmResp:915 WARNING - SERVER NOT READY - Invalid DSMCC response received : 6 !!
    global logHighlights

    pattern = re.compile("^.*SERVER NOT READY - Invalid DSMCC response.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : vod session setup failed - vod server not ready"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def vodSessionSetUpFailure2Parser( line ):
    #Jan 29 10:55:23 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|VOD_SessCntl(TID:5470b340):ProcessTimeoutCallBack:415  NOT RECEIVED SERVER RESPONSE  - sending error to service layer !!
    global logHighlights

    pattern = re.compile("^.*VOD_SessCntl.* NOT RECEIVED SERVER RESPONSE.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : vod session setup failed - no response from vod server"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def vodSessionTearDownParser( line ):
    #Jan 29 10:38:33 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|StreamTearDown:122 Closing the socket[400]
    global logHighlights

    pattern = re.compile("^.*StreamTearDown.*Closing the socket.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : vod session torn down. It's normal if vod playback was stopped"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def vodPlaybackInitParser( line ):
    #Jan 29 10:53:52 powertv syslog: DLOG|MSP_MPLAYER|EMERGENCY|IMediaPlayer:IMediaPlayerSession_Load:434  URL: lscp://AssetId=1135&AppId=524289&BillingId=0&PurchaseTime=1454082831&RemainingTime=85482&EndPos=5635&srmManufacturer=Seachange&streamerManufacturer=Seachange&connectMgrIp=0x4161e479&Title=ForestGumpMultiTrick3 - 60x  session: 0x1b143b0     **SAIL API**
    # Feb  1 16:36:47 powertv syslog: DLOG|GALIO|NORMAL|package://5415C3E6-9E841FCC/js/zapp_modes.js at line 375 ZapperModeVideo::Connect is now Playing [object MOMVODAsset] : Name : undefined : ForestGumpMultiTrick3 - 60x
    global logHighlights

    pattern = re.compile("^.*IMediaPlayer:IMediaPlayerSession_Load.*AssetId.*Title.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub( ' session.*$', '', re.sub('^.*IMediaPlayer:IMediaPlayerSession_Load.*AssetId.*Title=', '', match.group()))
        val = val.strip()

        logStr = " : vod playback of asset : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def vodPlaybackParser( line ):
    # Jan 29 11:12:30 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:1 Den:1 Speed:100.000000 #####
    # Jan 29 11:21:18 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:0 Den:0 Speed:0.000000 #####
    # Jan 29 11:22:26 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:15 Den:2 Speed:750.000000 ####
    # Jan 29 11:27:22 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:300 Den:10 Speed:3000.000000 #####
    # Jan 29 11:27:26 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:600 Den:10 Speed:6000.000000 #####
    # Jan 29 11:23:27 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:-15 Den:2 Speed:-750.000000 #####
    # Jan 29 11:27:56 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:-300 Den:10 Speed:-3000.000000 #####
    # Jan 29 11:28:00 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:-600 Den:10 Speed:-6000.000000 #####
    global logHighlights

    pattern = re.compile("^.*OnDemand.*HandleCallback.*Speed:.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub(' ####.*$', '', re.sub('^.*OnDemand.*HandleCallback.*Speed:', '', match.group()))
        val = val.strip()

        try:
            val = vodPlaybackSpeedMap[val]
        except:
            val = val

        logStr = " : vod playback ongoing at "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def tunedProgramParser( line ):
    #Jan 28 14:46:11 powertv syslog: DLOG|GALIO|NORMAL|antclient://library/js/gadget_baseinfo.js at line 99 In base info update      Programme Name is : General Hosp. : CHANNEL NUMBER : 7
    global logHighlights

    pattern = re.compile("^.*gadget_baseinfo.* Programme Name is.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub(':.*$', '', re.sub('^.*gadget_baseinfo.* Programme Name is : ', '', match.group()))
        val = val.strip()

        logStr = " : Tuned to program : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def tunedChannelParser( line ):
    #Jan 28 14:46:11 powertv syslog: DLOG|GALIO|NORMAL|antclient://library/js/gadget_baseinfo.js at line 340 RTNUI : gadget_baseinfo : reallyUpdate : 7 <span>CITYT</span>
    global logHighlights

    pattern = re.compile("^.*gadget_baseinfo : reallyUpdate .*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub('<\/?span>', '', re.sub('^.*gadget_baseinfo : reallyUpdate : ', '', match.group()))
        val = val.strip()
        
        logStr = " : Tuned to channel : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def tunedChannelNumberParser( line ):
    #Jan 29 12:54:18 powertv syslog: DLOG|MSP_MPLAYER|EMERGENCY|IMediaPlayer:IMediaPlayerSession_Load:434  URL: sctetv://022  session: 0x1c6f4f8     **SAIL API**
    global logHighlights

    pattern = re.compile("^.*IMediaPlayer:IMediaPlayerSession_Load.*sctetv.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub(' session.*$', '', re.sub('^.*IMediaPlayer:IMediaPlayerSession_Load.*sctetv:\/\/', '', match.group()))
        val = val.strip()
        
        logStr = " : Tuned to channel : "
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def docsisParser( line ):
    #Jan 28 12:20:36 powertv syslog: DLOG|GALIO|NORMAL|antclient://library/js/config.js at line 2039 RTNUI : Communication mode has been updated to : docsis : new IP Address : 100.109.176.144
    global logHighlights

    pattern = re.compile("^.*Communication mode has been updated to : docsis.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Communication mode has been updated to : docsis"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

def davicParser( line ):
    # Feb  1 10:04:31 powertv syslog: DLOG|DIAG_WS_PRIVATE|ERROR|(Not an Error) Informative: [UpdateLogFwdState][392]Box is either in davic mode or in one way!!!!! Disabling the log forwarding feature]
    global logHighlights

    pattern = re.compile("^.*Box is either in davic mode or in one way.*$")
    match = re.search(pattern, line)
    
    if match:
        val = ""
        logStr = " : Box in DAVIC mode or in one way"
        logIt(sys._getframe().f_code.co_name + logStr + val, LB_Y, VERBOSE)
        line = line.rstrip('\n')
        contents[lineCount] = line + " " + logSearchInfo + logStr + val + "\n"
        logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + logStr + val + "\n"
        return True
    return False

#.............................................................................#

parsers = [
        keyPressParser,
        boxTypeParser,
        buildInfoParser,
        bfsInitDoneParser,
        bfsDnldCrashParser,
        bfsBrokenPipeParser,
        bfsEPGDataDownloadFailureParser,
        ipAddressParser,
        macAddressParser,
        recordingStartedParser,
        recordingStarted2Parser,
        recordingStoppedParser,
        recordingStopped2Parser,
        recordingDeletedParser,
        recordingDeleted2Parser,
        recordingPlaybackStartedParser,
        recordingPlaybackStarted2Parser,
        recordingFailureParser,
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
        certInfoParser,
        uiExceptionParser,
        notStagedParser,
        grpDefParser,
        bootUpSequenceParser,
        network2WayReadyParser,
        maintSequenceParser,
        vodSessionSetUpFailureParser,
        vodSessionSetUpFailure2Parser,
        vodSessionTearDownParser,
        vodPlaybackInitParser,
        vodPlaybackParser,
        tunedProgramParser,
        tunedChannelParser,
        tunedChannelNumberParser,
        docsisParser
        # davicParser,
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

ap = argparse.ArgumentParser(description="RTN Log Parser", formatter_class=argparse.RawTextHelpFormatter)
ap.add_argument('log', nargs='+', help="logs (normal/zipped) to parse :\ndir/log1 dir/log2 ... dir/logn\ndir/log*\ndir/*\nuse -u option to parse zipped log")
ag = ap.add_mutually_exclusive_group()
ag.add_argument("-v", "--verbose", action="store_true", help = "all parser logs - for script debugging")
ag.add_argument("-q", "--quiet", action="store_true", help = "no parser logs - for script debugging")
ap.add_argument("-u", "--unzip", action="store_true", help = "gunzip log")
args = ap.parse_args()

if args.verbose:
    loggingMode = VERBOSE
elif args.quiet:
    loggingMode = QUIET


logIt("",LB_N)
logIt("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", LB_Y)
for log in args.log:
    logIt("Processing file : " + log)
    
    try:
        inFile = log
        f = open(inFile, "r")
    except:
        logIt("ERR : invalid log file: " + inFile, LB_Y, FORCE)
        logIt("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", LB_Y)
        continue

    if args.unzip:
        logName, logExtension = os.path.splitext(log)
        if (logExtension == ".gz"):
            logIt("Unzipping log : " + log)
            subprocess.call(["gunzip", logName])
            f.close()
            inFile = logName
            f = open(inFile, "r")

    contents = f.readlines()
    f.close()
    logHighlights = ""

    with open(inFile, 'r') as file:
        for lineCount, line in enumerate(file):
            lineParser(line)

# post process

    if logHighlights:

        try:
            outFile = inFile+"_changed"
            f = open(outFile, "w")
        except:
            logIt("ERR: cannot write to file, no permissions : " + outFile, LB_N, FORCE)
            quit()

        contents = "".join(contents)
        f.write(contents)
        f.close()
        
        logIt(inFile + " processed successfully.", LB_N)
        logIt("Following are highlights in " + inFile + ":")
        
        logIt(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", LB_N)
        logIt(logHighlights.strip(),0)
        logIt(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", LB_Y)
        
        logIt("Log highlights are also embedded in output file : " + outFile, LB_N)
        logIt("Look for " + logSearchInfo + " in " + outFile)
        
        logIt("To compare files:", LB_N)
        logIt("vimdiff " + outFile + " " + inFile)
        
        logIt("To use changed file:", LB_N)
        logIt("mv " + outFile + " " + inFile)
    else:
        logIt("WARN: nothing to parse: " + inFile, LB_Y, FORCE)
    
    logIt("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", LB_Y)
#-----------------------------------------------------------------------------#
