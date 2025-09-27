"""
SE521_DB
Python class to handling data xfer between SE521 logger and mysql database
vim: sw=4 ts=4 expandtab
    """

import sys

import mysql.connector
from mysql.connector import errorcode as msqlerrcode
import logging

log = logging.getLogger( "SE521_log.DBmodule" )

DRIVER_NAME = "DB_rooftemp"
DRIVER_VERSION = "0.04"

debug=1


if sys.version_info[0] != 3:
    log.error("This script requires Python version 3")
    sys.exit(1)

class SolarDBError( Exception ):
    """ base class for exceptions that might occur here """


class roof_temp_DB( ):

    roof_insert = """
        INSERT IGNORE into rooftemp ( DateTm, panel, air_under_panel, tile_top, tile_underneath, air_in_roof )
              VALUES 
            (%(DateTm)s, %(panel_temp)s, %(air_under_panel)s, %(tile_top)s, %(tile_under)s, %(air_in_roof)s)"""
 
    def __init__( self, mode = "ro" ):
        if mode == "ro":
            self.dbuser="readmany"
            self.dbpw = ""
        elif mode == "rw":
            self.dbuser="USER-NAME-HERE"
            self.dbpw = "USER-PASSWD-HERE"
        else:
            raise SolarDBError( "Invalid mode: " + mode )

        self.iomode = mode
        self.cnx = None
        self.cs_roof = None
        self.errorcount = 0
        log.info( "Opening DB, {} mode".format( self.iomode ) )
        
        self.open()
        
    def open( self ):
    
        try:
            self.cnx = mysql.connector.connect( user=self.dbuser, password=self.dbpw,
                    host='127.0.0.1', database='solar_roof')

        except mysql.connector.Error as err:
            if err.errno == msqlerrcode.ER_ACCESS_DENIED_ERROR:
                log.exception("Bad user name or password: %s" % self.user)
            elif err.errno == msqlerrcode.ER_BAD_DB_ERROR:
                log.exception("Database does not exist")
            else:
                raise SolarDBError( err )
            raise
            
        self.cs_roof= self.cnx.cursor( buffered=True )


    def add_data( self, data ):
        if self.cnx is None:
            self.open()
        try:
            self.cs_roof.execute( roof_temp_DB.roof_insert, data )
            
        except mysql.connector.Error as err:
            log.exception( "adding MySQL data: %s" % err )
            self.errorcount += 1
            self.cnx = None         # force reopen attempt
            if self.errorcount > 10:
                raise  SolarDBError( "too many failures writing DB" )

    def close( self ):
        self.close_cursor()
        if self.cnx is not None:
            self.cnx.commit()
            self.cnx.close()  
            self.cnx = None
                
    def close_cursor( self ):
        if self.cs_roof is not None:
            self.cs_roof.close()
            self.cs_roof = None       

    
    
    

