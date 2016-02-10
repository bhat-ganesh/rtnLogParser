#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Ganesh Bhat <ganesbha@cisco.com>"
__version__ = "1.0"
__date__ = "2016-Feb-11"

import sys
import re
import argparse
import textwrap
import os
import subprocess

#-----------------------------------------------------------------------------#

# globals

parserInfo ="\t\t\t--------------\n" + \
            "\t\t\tRTN Log Parser\n" + \
            "\t\t\t--------------\n" + \
            "\n  version\t    " + __version__ + \
            "\n  date\t\t    " + __date__ + \
            "\n  author\t    " + __author__

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
    '27' : '27 - what is this key',
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
    '5k'  : 'G10 5K'
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
    try:
        dateTime = matchDateTime.group()
        # logIt("sys._getframe().f_code.co_name: " + dateTime, LB_N, VERBOSE)
        return dateTime
    except:
        return ""

#.............................................................................#

def updateLog(line, parserName, message, lb):
    global logHighlights

    logIt(parserName + message, lb, VERBOSE)
    line = line.rstrip('\n')
    contents[lineCount] = line + " " + logSearchInfo + message + "\n"
    logHighlights += "line " + str(lineCount+1) + " : " + dateTimeParser(line) + " : " + message + "\n"
    return

#.............................................................................#

def keyPressParser( line ):
    #Jan 27 16:53:41 powertv syslog: DLOG|GALIO|NORMAL| -- sending key 462 --
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
        logStr = "Key Press : "
        updateLog(line, sys._getframe().f_code.co_name, logStr + val, LB_N)
        return True
    return False

#.............................................................................#

def buildInfoParser( line ):
    
    return False

#.............................................................................#

def bfsInitDoneParser( line ):
    #Jan 25 10:47:55 powertv syslog: DLOG|BFSUTILITY|EMERGENCY|BFS Init Done!
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
        logStr = ""
        updateLog(line, sys._getframe().f_code.co_name, logStr + val, LB_N)
        return True
    return False

#.............................................................................#

def recordingFailureParser( line ):
    # Dec 29 10:09:33 powertv syslog: DLOG|DVR|Recording Failure|FDR_log: DVRTXN080030: 1006|Liberty's Kids|17|1450921500|RECORDING DELETED:DISK SPACE CRITICAL 95%
    # Jan 25 06:00:04 powertv csp_CPERP: DLOG|DVR|Recording Failure|TimerHandler: Failure not enough disk space to record Breakfast Television AID 113
    # Jan 13 21:19:16 powertv csp_CPERP: DLOG|DVR|Recording Failure|FDR_log: DVRTXN050030: CLM UPDATE START
    # Jan 13 21:19:38 powertv csp_CPERP: DLOG|DVR|Recording Failure|FDR_log: DVRTXN050040: CLM UPDATE SUCCESS
    
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
        
        logStr = "recording failed : "
        updateLog(line, sys._getframe().f_code.co_name, logStr + val, LB_N)
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
    
    pattern = re.compile("^.*OnDemand.*HandleCallback.*Speed:.*$")
    match = re.search(pattern, line)
    
    if match:
        val = re.sub(' ####.*$', '', re.sub('^.*OnDemand.*HandleCallback.*Speed:', '', match.group()))
        val = val.strip()

        try:
            val = vodPlaybackSpeedMap[val]
        except:
            val = val

        logStr = "vod playback ongoing at "
        updateLog(line, sys._getframe().f_code.co_name, logStr + val, LB_N)
        return True
    return False

#.............................................................................#
  
def regexParser( regexList ):
    pattern = re.compile("^.*" + regexList[0][0] + ".*$")
    match = re.search(pattern, line)

    if match:
        logStr = match.group()
        
        for regex in regexList:
            val = re.sub(regex[0], regex[1], logStr)
            val = val.strip()
            logStr = val

        updateLog(line, sys._getframe().f_code.co_name, logStr, LB_N)
        return True

    return False

#.............................................................................#

parsers = [
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 27 16:53:41 powertv syslog: DLOG|GALIO|NORMAL| -- sending key 462 --
            [
                keyPressParser
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Image created for 9k box.
            [
                '',
                [
                    ['^Image created for ', 'Box type : '],
                    [' box.*$', '']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # [
            #     buildInfoParser
            # ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 25 10:47:55 powertv syslog: DLOG|BFSUTILITY|EMERGENCY|BFS Init Done!
            [
                bfsInitDoneParser    
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 27 11:23:28 powertv syslog: DLOG|BFS_GET_MODULE|EMERGENCY|get_filter_setting_for_module - 625 assertion failed
            [
                '',
                [
                    ['^.* - 625 assertion failed$', 'BFS dnld crash CSCux30595']    
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 20 12:28:14 powertv csp_CPERP: DLOG|BFS_GET_MODULE|ERROR|bool CSCI_BFS_API::ActiveContext::_serializeAndSendPacket(int, BfsIpc::PacketBuilder&) - 222 Error sending eIpc_BeginDownload packet to BFS server - send /tmp/bfs_server error Broken pipe
            [
                '',
                [
                    ['^.*BFS.* error Broken pipe$', 'BFS error broken pipe']    
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 28 11:17:18 powertv epg: DLOG|EPG_LOAD|SIGNIFICANT_EVENT|gi_load: GI for day 2 not found either in disk cache nor memory cache, check wheather it is loading
            [
                '',
                [
                    ['^.*gi_load: GI for day.*not found.*$', 'BFS is up but NOT able to download EPG data']    
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 28 12:20:13 powertv syslog: doc_StoreParameter: Host IPv4 address: 100.109.176.144.
            [
                '',
                [
                    ['^.*: Host IPv4 address: ', 'IP Address : ']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 28 12:19:15 powertv syslog: DLOG|MDA|ERROR|mda_network_init:336: MAC address = 68:EE:96:6F:15:B8
            [
                '',
                [
                    ['^.*mda_network_init.*MAC address = ', 'MAC Address : ']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 13:02:57 powertv syslog: DLOG|MSP_MPLAYER|EMERGENCY|IMediaPlayer:IMediaPlayerSession_PersistentRecord:685 sess: 0x3ab3ee0  recordUrl: sadvr://dElWnhPo  start: 0.000000   stop: -2.000000    **SAIL API**
            [
                '',
                [
                    ['^.*IMediaPlayer:IMediaPlayerSession_PersistentRecord.*recordUrl.*$', 'recording started']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 27 11:24:56 powertv syslog: DLOG|GALIO|NORMAL|SCHED: record added dvr://recording/00000000-0000-0000-0000-00000000000000000570 rec [@01a57220: dvr://recording/00000000-0000-0000-0000-00000000000000000570 play 1 state mom_recording_RECORDING rel @01a57ee0 The Price Is Right]
            [
                '',
                [
                    ['^.*GALIO\|NORMAL.*record added.*_RECORDING rel @........ ', 'start recording program : '],
                    ['].*$', '']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 13:04:28 powertv syslog: DLOG|MSP_MRDVR|ERROR|MRDvrServer:Csci_Msp_MrdvrSrv_NotifyRecordingStop:112 URL is : sctetv://003
            [
                '',
                [
                    ['^.*Csci_Msp_MrdvrSrv_NotifyRecordingStop.*$', 'recording stopped']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 15:12:42 powertv syslog: DLOG|GALIO|NORMAL|SCHED: record updated dvr://recording/00000000-0000-0000-0000-00000000000000000641 rec [@03989318: dvr://recording/00000000-0000-0000-0000-00000000000000000641 play 1 state mom_recording_STOPPED rel <NULL> Zooville]
            [
                '',
                [
                    ['^.*GALIO\|NORMAL.*record updated.*_STOPPED rel <NULL> ', 'stop recording program : '],
                    ['].*$', '']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 13:05:15 powertv syslog: DLOG|DVRUTIL|ERROR|Successfully Deleted file /mnt/dvr0/vNA4T1Rn
            [
                '',
                [
                    ['^.*DVRUTIL.*Successfully Deleted file.*$', 'recording deleted']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 15:19:06 powertv syslog: DLOG|GALIO|NORMAL|SCHED: record deleted (state != mom_recording_RECORDING) dvr://recording/00000000-0000-0000-0000-00000000000000000641 rec [@03989318: dvr://recording/00000000-0000-0000-0000-00000000000000000641 play 1 state mom_recording_STOPPED rel <NULL> Zooville]
            [
                '',
                [
                    ['^.*GALIO\|NORMAL.*record deleted.*_STOPPED rel <NULL> ', 'reording deleted : '],
                    ['].*$', '']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 13:11:57 powertv syslog: DLOG|MSP_MPLAYER|EMERGENCY|IMediaPlayer:IMediaPlayerSession_Load:434  URL: sadvr://mnt/dvr0/6oxGuu4M  session: 0x1b0a978     **SAIL API**
            [
                '',
                [
                    ['^.*IMediaPlayer:IMediaPlayerSession_Load.*URL: sadvr:.*$', 'recording playback started']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 15:14:01 powertv syslog: DLOG|GALIO|NORMAL|package://5415C3E6-8DBEB1FC/js/zapp_modes.js at line 375 ZapperModeVideo::Connect is now Playing [object MOMScheduledRecording] : Name : dvr://recording/00000000-0000-0000-0000-00000000000000000641 : Zooville
            [
                '',
                [
                    ['^.*GALIO\|NORMAL.*Connect is now Playing.*dvr.* : ', 'recording playback started = ']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Dec 29 10:09:33 powertv syslog: DLOG|DVR|Recording Failure|FDR_log: DVRTXN080030: 1006|Liberty's Kids|17|1450921500|RECORDING DELETED:DISK SPACE CRITICAL 95%
            # Jan 25 06:00:04 powertv csp_CPERP: DLOG|DVR|Recording Failure|TimerHandler: Failure not enough disk space to record Breakfast Television AID 113
            # Jan 13 21:19:16 powertv csp_CPERP: DLOG|DVR|Recording Failure|FDR_log: DVRTXN050030: CLM UPDATE START
            # Jan 13 21:19:38 powertv csp_CPERP: DLOG|DVR|Recording Failure|FDR_log: DVRTXN050040: CLM UPDATE SUCCESS
            [
                recordingFailureParser
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Dec 22 16:14:53 powertv syslog: DLOG|MSP_DVR|ERROR|RecSession:stopConvert:808 RecordSessionStateError: Error Bad state: 3
            [
                '',
                [
                    ['^.*RecordSessionStateError: Error Bad state: 3$', 'Recording not playable : Error Bad state: 3']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Nov 13 10:49:26 powertv csp_CPERP: DLOG|CA_CAK|NORMAL|****** ECM 16 Digital_Response, result 0xb
            [
                '',
                [
                    ['^.*ECM 16 Digital_Response, result 0xb$', 'Recording not playable : due to deauthorization']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 11 09:26:29 powertv csp_CPERP: DLOG|MSP_MPLAYER|ERROR|DisplaySession:stop:1352 cpe_media_Stop error -19
            [
                '',
                [
                    ['^.*cpe_media_Stop error -19$', 'Black Screen on all channels : due to cpe_media_Stop2 error -19 CSCup37738']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Dec 21 15:35:08 powertv csp_CPERP: DLOG|MSP_MPLAYER|ERROR|Zapper:handleEvent:225 PsiTimeOutError: Warning - PSI not available. DoCallback – ContentNotFound!!
            [
                '',
                [
                    ['^.*PSI not available.*$', 'VOD playback black screen : due to stream issue']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Dec 20 03:50:21 powertv csp_CPERP: DLOG|MSP_MPLAYER|EMERGENCY|Zapper:handleEvent:220 Warning - Tuner lock timeout.May be signal strength is low or no stream on tuned frequency!!
            [
                '',
                [
                    ['^.*signal strength is low or no stream.*$', 'Black screen : stream issue - low signal or no stream']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Dec 11 15:36:10 powertv syslog: DLOG|MSP_PSI|ERROR|Psi:dispatchEvent:125 PsiTimeOutError: Time out while waiting for PAT
            [
                '',
                [
                    ['^.*PsiTimeOutError: Time out while waiting for PAT$', 'Black screen : PAT timeout']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Nov 11 00:10:17 powertv csp_CPERP: DLOG|MSP_MPLAYER|ERROR|Zapper:GetComponents:1717 PSI/PMT Info Not found
            [
                '',
                [
                    ['^.*PMT Info Not found$', 'Black screen : stream issue - no pmt']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Dec 31 19:01:37 powertv csp_CPERP: DLOG|SAM|ERROR|Thread Setname Failed:threadRetValue:0
            [
                '',
                [
                    ['^.*SAM.*Thread Setname Failed.*$', 'Stuck at -04- : due to SAM not ready']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Nov 21 05:25:25 powertv csp_CPERP: DLOG|MSP_DVR|ERROR|dvr:dispatchEvent:1022 Service DeAuthorized by CAM
            [
                '',
                [
                    ['^.*Service DeAuthorized by CAM$', 'Service deauthorized']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Nov 21 05:25:25 powertv csp_CPERP: DLOG|CA_CAK|ERROR|PkCakDvrRecordSession_cronus.cpp:383 Async No authorized ECM in CA message
            [
                '',
                [
                    ['^.*No authorized ECM in CA message$', 'Black screen due to no authorized ECM in CA message']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Nov 13 01:43:41 powertv syslog: DLOG|SDV|ERROR|ccmisProtocol.cpp HandleProgramSelectIndication Channel is not available
            [
                '',
                [
                    ['^.*Channel is not available$', 'Channel is not available']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Nov 12 21:20:30 powertv bfsdnld: DLOG|BFS_GET_MODULE|ERROR|directory_update_timeout directory update taking more than 120 seconds
            [
                '',
                [
                    ['^.*directory update taking more than 120 seconds.*$', 'Stuck on -05- due to ui error loading']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Feb  1 10:04:55 powertv syslog:  Settop Extender Bridge: UpnPInitializeSSLContext - Retrying (# 182) to get DOCSIS cert info!
            [
                '',
                [
                    ['^.*Retrying .* to get DOCSIS cert info.*$', 'Stuck on -05- due to failure in getting docsis cert info']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Sep 11 15:08:44 powertv root: SCRIPT: unhandled exception: Attempt to convert null or undefined value recording to Object
            # Sep 11 19:08:52 powertv root: SCRIPT: unhandled exception: SETTINGS.CheckboxPane() is not defined
            [
                '',
                [
                    ['^.*SCRIPT: unhandled exception.*$', 'exception in rtnui !!!']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 28 12:47:57 powertv syslog: DLOG|DNCS_SETTINGS|EMERGENCY|SetStagingstatus:94 isStagingDefsApplied: 0 isHubSpecficStagingDefsApplied: 1 isAddressableStaged: 0
            [
                '',
                [
                    ['^.*SetStagingstatus.* isStagingDefsApplied: 0.*$', 'Stuck on -05- after Factory Restore due to not staged']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Feb  1 11:26:52 powertv csp_CPERP: DLOG|DLM|NORMAL|[downloadAppAndArtFile][96] Value of sam_isGrpDefParsed from BFS() = 0
            [
                '',
                [
                    ['^.*downloadAppAndArtFile.* Value of sam_isGrpDefParsed from.* = 0.*$', 'Stuck on -05- download manager is blocked on downloading grps_defs.txt']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Dec 31 19:01:13 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling:      Application started => Waiting for SessInit : 49.64 seconds, total time: 91.46 seconds (BUFFERED)
            # Dec 31 19:01:29 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -00- SessInit is ready => Waiting for Hub Id : 2.02 seconds, total time: 93.48 seconds (BUFFERED)
            # Dec 31 19:01:29 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -01- Hub Id is ready => Waiting for SI : 15.04 seconds, total time: 108.53 seconds (BUFFERED)
            # Jan 27 11:21:07 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -02- SI is ready => Waiting for BFS : 65.44 seconds, total time: 173.96 seconds (BUFFERED)
            # Jan 27 11:21:07 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -03- BFS is ready => Waiting for SAM : 0.02 seconds, total time: 173.99 seconds
            # Jan 27 11:21:09 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -04- SAM is ready => Waiting for global config : 2.03 seconds, total time: 176.01 seconds
            # Jan 27 11:21:16 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling: -05- Global config is ready => Launching UI : 2.02 seconds, total time: 178.03 seconds
            # Jan 27 11:24:50 powertv syslog: DLOG|SAILMSG|ERROR|Bootup profiling:      UI launched => System ready : 218.45 seconds, total time: 396.48 seconds
            [
                '',
                [
                    ['^.*Bootup profiling: ', 'Bootup step : '],
                    [' =>.*$', '']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 28 12:21:13 powertv syslog: DLOG|SPM_VODCTLG|ERROR|vod-internal.cpp:void* tr_VodInit(void*):959: Network is two way and System is Ready
            [
                '',
                [
                    ['^.*Network is two way and System is Ready.*$', 'Network is two way and System is Ready']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 28 12:22:01 powertv syslog: DLOG|DLM|EMERGENCY|[sendSailMessage][1517] dlmWarningType:MAINT_DOWNLOAD_WARNING
            # Jan 28 12:22:21 powertv syslog: DLOG|DLM|EMERGENCY|[sendSailMessage][1517] dlmWarningType:MAINT_DOWNLOAD_REQUEST
            # Jan 28 12:23:00 powertv syslog: DLOG|DLM|EMERGENCY|[sendSailMessage][1517] dlmWarningType:MAINT_DOWNLOAD_COMPLETE
            [
                '',
                [
                    ['^.*MAINT_DOWNLOAD_', 'Maintenance download : ']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 28 14:41:31 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|SeaChange_SessCntrl:HandleSessionConfirmResp:915 WARNING - SERVER NOT READY - Invalid DSMCC response received : 6 !!
            [
                '',
                [
                    ['^.*SERVER NOT READY - Invalid DSMCC response.*$', 'vod session setup failed - vod server not ready']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 10:55:23 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|VOD_SessCntl(TID:5470b340):ProcessTimeoutCallBack:415  NOT RECEIVED SERVER RESPONSE  - sending error to service layer !!
            [
                '',
                [
                    ['^.*VOD_SessCntl.* NOT RECEIVED SERVER RESPONSE.*$', 'vod session setup failed - no response from vod server']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 10:38:33 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|StreamTearDown:122 Closing the socket[400]
            [
                '',
                [
                    ['^.*StreamTearDown.*Closing the socket.*$', 'vod session torn down. It is normal if vod playback was stopped']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 10:53:52 powertv syslog: DLOG|MSP_MPLAYER|EMERGENCY|IMediaPlayer:IMediaPlayerSession_Load:434  URL: lscp://AssetId=1135&AppId=524289&BillingId=0&PurchaseTime=1454082831&RemainingTime=85482&EndPos=5635&srmManufacturer=Seachange&streamerManufacturer=Seachange&connectMgrIp=0x4161e479&Title=ForestGumpMultiTrick3 - 60x  session: 0x1b143b0     **SAIL API**
            # Feb  1 16:36:47 powertv syslog: DLOG|GALIO|NORMAL|package://5415C3E6-9E841FCC/js/zapp_modes.js at line 375 ZapperModeVideo::Connect is now Playing [object MOMVODAsset] : Name : undefined : ForestGumpMultiTrick3 - 60x
            [
                '',
                [
                    ['^.*IMediaPlayer:IMediaPlayerSession_Load.*AssetId.*Title=', 'vod playback of asset : '],
                    [' session.*$', '']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 11:12:30 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:1 Den:1 Speed:100.000000 #####
            # Jan 29 11:21:18 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:0 Den:0 Speed:0.000000 #####
            # Jan 29 11:22:26 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:15 Den:2 Speed:750.000000 ####
            # Jan 29 11:27:22 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:300 Den:10 Speed:3000.000000 #####
            # Jan 29 11:27:26 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:600 Den:10 Speed:6000.000000 #####
            # Jan 29 11:23:27 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:-15 Den:2 Speed:-750.000000 #####
            # Jan 29 11:27:56 powertv syslog: DLOG|MSP_ONDEMAND|ERROR|OnDemand(TID:5470b340):HandleCallback:1263 #### Ondemand ::Callback signal for Num:-300 Den:10 Speed:-3000.000000 #####
            [
                vodPlaybackParser
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 28 14:46:11 powertv syslog: DLOG|GALIO|NORMAL|antclient://library/js/gadget_baseinfo.js at line 99 In base info update Programme Name is : General Hosp. : CHANNEL NUMBER : 7
            [
                '',
                [
                    ['^.*gadget_baseinfo.* Programme Name is : ', 'Tuned to program : ']
                    # [':.*$', '']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 28 14:46:11 powertv syslog: DLOG|GALIO|NORMAL|antclient://library/js/gadget_baseinfo.js at line 340 RTNUI : gadget_baseinfo : reallyUpdate : 7 <span>CITYT</span>
            [
                '',
                [
                    ['^.*gadget_baseinfo : reallyUpdate : ', 'Tune to channel : '],
                    ['<\/?span>', '']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 29 12:54:18 powertv syslog: DLOG|MSP_MPLAYER|EMERGENCY|IMediaPlayer:IMediaPlayerSession_Load:434  URL: sctetv://022  session: 0x1c6f4f8     **SAIL API**
            [
                '',
                [
                    ['^.*IMediaPlayer:IMediaPlayerSession_Load.*sctetv:\/\/', 'Tuned to channel : '],
                    [' session.*$', '']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Jan 28 12:20:36 powertv syslog: DLOG|GALIO|NORMAL|antclient://library/js/config.js at line 2039 RTNUI : Communication mode has been updated to : docsis : new IP Address : 100.109.176.144
            [
                '',
                [
                    ['^.*Communication mode has been updated to : docsis.*$', 'Communication mode has been updated to : docsis']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Feb  1 10:04:31 powertv syslog: DLOG|DIAG_WS_PRIVATE|ERROR|(Not an Error) Informative: [UpdateLogFwdState][392]Box is either in davic mode or in one way!!!!! Disabling the log forwarding feature]
            # [
            #     '',
            #     [
            #         ['^.*Box is either in davic mode or in one way.*$', 'Box in DAVIC mode or in one way']
            #     ]
            # ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Feb  9 16:32:35 powertv syslog: DLOG|GALIO|NORMAL|package://5F2DD257-C79E59BB/js/debug.js at line 7 [] - 16:32:35.832 - [I]: logging for ZTAP turned off
            # Feb  9 16:32:36 powertv syslog: DLOG|GALIO|NORMAL|package://5F2DD257-C79E59BB/js/debug.js at line 7 [] - 16:32:36.666 - [I]: logging for ZTAP turned on
            [
                '',
                [
                    ['^.* logging for ZTAP turned ', 'Zodiac logging tunred ']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Feb  9 16:36:32 powertv syslog: DLOG|GALIO|NORMAL|package://5F2DD257-C79E59BB/js/debug.js at line 7 [ZSEA] - 16:36:32.648 - [D]: request(searchObjectOrText: ABC)
            [
                '',
                [
                    ['^.*ZSEA.*searchObjectOrText: ', 'Searching for : '],
                    ['\).*$', '']
                ]
            ],
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
            # Feb  9 16:35:34 powertv syslog: DLOG|GALIO|NORMAL|package://5F2DD257-C79E59BB/js/debug.js at line 7 [ZSEA] - 16:35:34.432 - [D]: onResultsEnter [PERSONALITY] [<em>A</em>ngela <em>B</em>assett]
            # Feb  9 16:37:50 powertv syslog: DLOG|GALIO|NORMAL|package://5F2DD257-C79E59BB/js/debug.js at line 7 [ZSEA] - 16:37:50.775 - [D]: onResultsEnter [PERSONALITY] [<em>A</em>lexander <em>B</em>.<em>C</em>ollett]
            [
                '',
                [
                    ['^.*ZSEA.*onResultsEnter \[PERSONALITY\] ', 'search asset selected : '],
                    ['\<em\>', ''],
                    ['\<\/em\>', '']
                ]
            ]
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
        ]
#. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#

def lineParser( line ):
    for parser in parsers:
        try:
            ret = parser[0](line);
        except:
            ret = regexParser(parser[1])

        if ret:
            break
    return

#-----------------------------------------------------------------------------#

# main

ap = argparse.ArgumentParser( formatter_class = argparse.RawTextHelpFormatter, description = parserInfo)
ap.add_argument( 'log', nargs = '+', help = "normal or compressed logs to parse. use -u option to uncompress.\n" +
                                            "dir/log1 dir/log2 dir/log3.gz ... dir/logn\n" + 
                                            "dir/log*\n" +
                                            "dir/*")
ag = ap.add_mutually_exclusive_group()
ag.add_argument( "-v", "--verbose",     action = "store_true", help = "all parser logs - for script debugging")
ag.add_argument( "-q", "--quiet",       action = "store_true", help = "no  parser logs")
ap.add_argument( "-u", "--uncompress",  action = "store_true", help = "uncompress logs")
ap.add_argument( "-o", "--overwrite",   action = "store_true", help = "overwrite original log with parsed log")
args = ap.parse_args()

if args.verbose:
    loggingMode = VERBOSE
elif args.quiet:
    loggingMode = QUIET

logIt("\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", LB_Y)
for log in args.log:
    logIt("Processing file : " + log)
    
    try:
        inFile = log
        f = open(inFile, "r")
    except:
        logIt("ERR : invalid log file: " + inFile, LB_Y, FORCE)
        logIt("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", LB_Y)
        continue

    if args.uncompress:
        logName, logExtension = os.path.splitext(log)
        if (logExtension == ".gz"):
            logIt("Uncompressing log : " + log)
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
            outFile = inFile+"_parsed"
            f = open(outFile, "wa")
        except:
            logIt("ERR: cannot write to file, no permissions : " + outFile, LB_N, FORCE)
            quit()

        contents = "".join(contents)
        f.write(contents)
        f.write(parserInfo + "\n")
        f.close()
        
        logIt(inFile + " processed successfully.", LB_N)
        logIt("Following are highlights in " + inFile + ":")
        
        logIt(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", LB_N)
        logIt(logHighlights.strip(), 0)
        logIt(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", LB_Y)
        
        logIt("Log highlights are embedded in outputfile : " + outFile, LB_N)
        logIt("Look for " + logSearchInfo + " in " + outFile)
        
        logIt("To compare :\nvimdiff " + outFile + " " + inFile)
        
        if args.overwrite:
            logIt("Overwriting " + inFile +" with " + outFile, LB_N)
            subprocess.call(["mv", outFile, inFile])
        else:
            logIt("To overwite :\nmv " + outFile + " " + inFile)
    else:
        logIt("WARN: nothing to parse: " + inFile, LB_Y, FORCE)
    
    logIt("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", LB_Y)
#-----------------------------------------------------------------------------#
