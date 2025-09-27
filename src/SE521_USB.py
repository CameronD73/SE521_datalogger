# python3 code using the HIDapi interface to read thermocouple data
# from the SE521 hardware and save it to database

import hidapi
import time
import logging

VERSION = "0.4"

log = logging.getLogger( "SE521_log.SE521_usb" )
    
class SE521_usb_Error( Exception ):
    """ general exception for errors in this driver"""

class SE521_usb:

    # enumerate USB devices
    VENDOR=0x04D9
    PRODUCT=0xE000

    def __init__( self ):

        self.counter = 0
        self.cmdpkt  = bytearray(b'\2\x41\0\0\0\0\3')

        # try opening a device, then perform write and read
        self.hiddev = None
        
        self.open( )


    def open( self ):
        """ open the connection to the logger.
        This opens the USB device connection, plus
        sends some initialisation code
        """
        try:
            self.hiddev = hidapi.Device( vendor_id=SE521_usb.VENDOR, product_id=SE521_usb.PRODUCT )

        except IOError as ex:
            log.exception("SE521-USB device not found: {}".format(ex))
            raise

        try:
            self.manufacturer = self.hiddev.get_manufacturer_string()
            self.product = self.hiddev.get_product_string()
            self.serial = self.hiddev.get_serial_number_string()

            # write some data to the device
            self.hiddev.send_feature_report( b'\1\7\0\0\0\0\0', b'\x43' )
            time.sleep(0.05)
            self.hiddev.write( b'\2\x4b\0\0\0\0\3', b'\x07')

            time.sleep(0.05)
            self.hiddev.send_feature_report( b'\4\x20\0\0\0\0\0', b'\x43' )

            # wait a bit more
            time.sleep(0.05)

            # read back the answer, 32 bytes at a time
            for pktcount in range( 2 ):
                d = self.hiddev.read(32, timeout_ms=200, blocking=True)
                if d:
                    if d[0] == 0x1f:
                        model = d[24:27].decode()
                        self.hiddev.model = model
                    elif d[0] == 0x01:
                        pass
                    else:
                        log.error("SE521_usb.open: Unexpected: {}".format( d ))
                else:
                    log.error( "SE521_usb.open: nothing else returned" )
                    break

        except IOError as ex:

            log.exception("SE521-found device but IO failed:{}".format(ex))
            self.hiddev.close()
            raise
            
    def close( self ):
        if self.hiddev is not None:
            self.hiddev.close()
            self.hiddev = None
        
    def getTC( self, tcnum, flag, bstr ):
        """extract a single TC value.
        The high and low bytes return a signed integer to tenths of
        a degree Fahrenheit. Always F, no matter what is displayed.
        The flag is a duplicated nibble where a bit is zero if a tc channel 
        is detected to be open circuit.
        In that case the temperature value is meaningless,
        but not always constant. 
        LSB is assigned to TC channel 4, then channel 3, etc.
        The high 4 bits duplicate the low 4, as far as I have observed so far.
        """
        if (flag & 0x0f) & (8 >> tcnum) == 1:
            return None

        tempFalt = int.from_bytes( bstr, byteorder="big", signed=True ) 
        tempFalt *= 0.1
        if tempFalt < -200:
            return None
            
        tempC = (tempFalt - 32) * 5.0 / 9
        return tempC

    def is_open( self ):
        """ checks if the device channel is open, and tries to open it if not
        Returns: True or False according to result.
        """
        openfailed = 1
        while self.hiddev is None:
            time.sleep( openfailed )
            self.open()
            openfailed += 1
            if openfailed > 6:
                log.error( "Too many failures to open usb port" )
                return False
        return True

    
    def read_next_set( self ):
        """ take a single set of readings from the thermocouple logger
        Return:
        A dict with the following fields:
        time:       a timestamp at which the reading was taken
        TC0 to TC3: (float)the temperature of each channel in deg C, or None
        """
        
        try:

            # write some data to the device
            self.hiddev.send_feature_report( b'\1\7\0\0\0\0\0', b'\x43' )

            self.counter = (self.counter+1) & 0xff
            time.sleep(0.05)
            self.cmdpkt[5] = self.counter
            self.hiddev.write( self.cmdpkt, b'\x07')

            time.sleep(0.05)
            self.hiddev.send_feature_report( b'\4\x40\0\0\0\0\0', b'\x43' )

            # wait
            #time.sleep(0.05)

            # read back the answer
            #print("-- Read the TC data (32 bytes at a time)")
            pkt = dict()
            for pktcount in range( 3 ):
                d = self.hiddev.read(32, timeout_ms=1200, blocking=True)
                if d:
                    if pktcount == 0:
                        if d[0] == 0x1f:
                            # ocflag has bits set if t/c is valid (not open cct.)
                            ocflag = d[7]
                            measuretime = time.time()
                            pkt["time"] = measuretime
                            for tcnum in range( 4 ):
                                tcname= "TC%d" %  tcnum
                                offset = 10 + tcnum * 2
                                pkt[tcname] = self.getTC( tcnum, ocflag, d[offset:offset+2] )
                        else:
                            log.error( "Pkt {} unexpected: {}".format(pktcount, d ))
                    elif d[0] == 0x02:
                        pass
                    elif d[0] == 0x1f:
                        rcvcount = d[31]
                        if rcvcount != self.counter:
                            log.error( "inpkt 2, counter mismatch: {} vs {}".format( rcvcount, self.counter ) )
                    else:
                        log.error("Unexpected: {}".format( d ))
                else:
                    log.info( "nothing else returned" )
                    return None
             
            if "time" in pkt:
                return pkt
        except IOError as ex:
            log.exception("read tc data failed: %s" % ex )
            self.close()
            return None
        return None


    def loop_one_reading( self ):
        """ generator function to repeatedly return a single set of
        readings from the hardware
        Return:
        A dict with the following fields:
        time:       a timestamp at which the reading was taken
        TC0 to TC3: (float)the temperature of each channel in deg C, or None
        """
        while True:
            if not self.is_open:
                return          # failed to keep usb interface open
            pkt = self.read_next_set()
            if pkt is not None:
                yield pkt

    def loop_average( self, nsamples = 20, interval=1 ):
        """ generator function to repeatedly return a  set of readings
        from the hardware that is an average of results over some time.
        Input:
        nsamples:   the number of samples to read
        interval:   the delay in seconds between each reading
        Return:
        A dict with the following fields:
        time:       a timestamp of the middle of the readings
        TC0 to TC3: (float)the mean temperature of each channel in deg C, or None
        """
        while True:
            if not self.is_open:
                return          # failed to keep usb interface open
            sumpkts = 4 * [0]
            pktcount = 4 * [0]
            starttime = time.time()
            validpackets = 0
            for i in range( 4 ):
                sumpkts[i] = 0
                pktcount[i] = 0

            for i in range( nsamples ):
                pkt0 = self.read_next_set()
                if pkt0 is not None:
                    validpackets += 1
                    for i in range( 4 ):
                        tcname= "TC%d" %  i
                        if pkt0[tcname] is not None:
                            sumpkts[i] += pkt0[tcname]
                            pktcount[i] += 1
                time.sleep( interval )
            pkt = dict()
            timedelta = time.time() - starttime
            meantime = starttime + timedelta * 0.5
            if validpackets > 0:
                pkt["time"] = meantime
                for i in range( 4 ):
                    tcname= "TC%d" %  i
                    if pktcount[i] > 0:
                        pkt[tcname] = sumpkts[i] / pktcount[i]
                    else:
                        pkt[tcname] = None
                        
                yield pkt

    def read_one_reading( self ):
        """ See generator equivalent"""

    def read_average( self, nsamples = 20, interval=1 ):
        """ See generator equivalent"""

