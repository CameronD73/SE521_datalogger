#! /usr/bin/python3
# python3 main code for reading thermocouple data
# from the SE521 hardware and save it to database

import argparse
import time
import datetime

import math
import logging
import logging.handlers

log = logging.getLogger( "SE521_log" )

VERSION = "0.4"


def printpkt( pkt ):
    """ A routine for pretty-printing the data packet returned from
    the USB-reading module.
    The pkt dictionary needs well-defined content (see SE521_USB module)
    """
    ts = time.localtime( pkt["time"] ) 
    print( "{:s}: ".format( time.strftime( "%H:%M:%S", ts )), end="" )
    for i in range( 4 ):
        tcname= "TC%d" %  i
        if pkt[tcname] is None:
            print( "   -----", end="" )
        else:
            print( "  {:6.2f}".format( pkt[tcname] ), end="" )
    print( "" )


DEBUG_CONSOLE = 0x10
debug = 1
avge_nsamples = 20
avge_interval = 1

parser = argparse.ArgumentParser( description="read thermocouple temperatures from SE521" )
modegroup = parser.add_mutually_exclusive_group( required=True )
modegroup.add_argument('-D', '--daemon', action='store_true',
                  help='run as a daemon - save to DB')
modegroup.add_argument('-l', '--live', action='store_true',
                  help='display live data')
parser.add_argument('-v', '--version', action='version', version="%(prog)s, Version: " + VERSION )
                  #help='display program version')
parser.add_argument('-s', '--single', action='store_true',
                  help='read single live data sample (default averages)')
args = parser.parse_args()


if args.live:
    debug |= DEBUG_CONSOLE
    
if debug & DEBUG_CONSOLE:
    log.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel( logging.DEBUG )
    log.addHandler( console )
    fileh = logging.FileHandler( "_local.log")
    filfmt = logging.Formatter('%(asctime)s: %(levelname)s  - %(message)s')
    fileh.setFormatter( filfmt )
    log.addHandler( fileh )

else:
    if debug > 0:
        log.setLevel( logging.DEBUG )
    else:
        log.setLevel( logging.INFO )
    sysh = logging.handlers.SysLogHandler( address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_USER )        
    sysh.ident = "SE521-logger: "
    log.addHandler( sysh )

# These modules are only loaded here, because they might trigger an error log message.
# So only load after logging has been set up.
import SE521_USB
import DB_rooftemp

log.info( "Starting SE521 logger, version {}, averaging {:d} samples, {:.1f} s apart.".format( VERSION, avge_nsamples, avge_interval ) )

stn = SE521_USB.SE521_usb(  )

log.info( "Station is  product: %s, by: %s; Ser num : %s" % (stn.product, stn.manufacturer, stn.serial) )

if args.daemon or args.live:
    if args.daemon:
        db = DB_rooftemp.roof_temp_DB( mode="rw")
    now = time.time()
    # work out the duration of the averaging process, including overheads
    avge_half_duration = 0.5 * avge_nsamples * (avge_interval + 0.11)
    next_save_minute = int( math.floor((now / 60 )) ) - 1
    start_time = 0
    # we want to allow min 5 seconds in order that sleep time is not too short
    # then add 4 sec as a first-time issue - not sure why it needs it.
    while start_time < (now + 5):
        next_save_minute += 1
        start_time = next_save_minute * 60 - avge_half_duration 
    start_delay = start_time - now
    log.info( "Sleeping for {:.1f} s to align to minute".format( start_delay ) )
    time.sleep( start_delay )
    data = dict()
    for packet in stn.loop_average( nsamples=avge_nsamples, interval=avge_interval ):
        midtime = packet["time"]
        expected_time = next_save_minute * 60
        timediff = midtime - expected_time
        if math.fabs( timediff ) > 1.0:
            log.error( " time offset: {:.2f}s".format( timediff ) )
            data["DateTm"] = datetime.datetime.fromtimestamp( midtime )
        else:
            # there seems to be some sort of rounding error/truncation converting
            # expected_time.   Somehow it seems to sometimes create a number fractionally below
            # the integer value, even though it should stay an integer!.
            data["DateTm"] = datetime.datetime.fromtimestamp( expected_time )
        data["panel_temp"] = packet["TC0"]
        data["air_under_panel"] = packet["TC1"] 
        data["tile_under"] = packet["TC2"]
        data["air_in_roof"] = packet["TC3"]
        data["tile_top"] = None
        
        if args.daemon:
            db.add_data( data )
        else:
            packet["time"] = expected_time
            printpkt( packet )
            print( "time difference = {:.3f}s".format(timediff ) )
        # now work out how long to sleep for to make next time
        # exact minute
        now = time.time()
        while start_time < (now + 2):
            next_save_minute += 1
            start_time = next_save_minute * 60 - avge_half_duration
        start_delay = start_time - now

        time.sleep( start_delay )

elif args.single:
    for packet in stn.loop_one_reading():
        printpkt(packet)
        time.sleep( 5 )
else:
    print ("oops, no command" )

log.info( "normal exit" )
