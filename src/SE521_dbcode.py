"""
SE521_DB
Python class to handling data transfer between SE521 logger and mysql database
vim: sw=4 ts=4 expandtab
"""

import sys

try:
    # first try using the python-mysqldb
    import MySQLdb as mysqlconn
    from MySQLdb import DatabaseError as MySQLDatabaseError
except ImportError:
    # if that failed, try MySQL's connector...
    import mysql.connector
    # from mysql.connector import errorcode as msqlerrcode
    from mysql import connector as mysqlconn
    from _mysql_exceptions import DatabaseError as MySQLDatabaseError
import logging

log = logging.getLogger( "SE521_log.DBmodule" )

DRIVER_NAME = "DB_temperature"
DRIVER_VERSION = "0.05"
# get the site-specific settings
import SE521_dbsettings
from SE521_dbsettings import DB_settings

debug=1

if sys.version_info[0] != 3:
    log.error("This script requires Python version 3")
    sys.exit(1)

class SE521DBError( Exception ):
    """ base class for exceptions that might occur here """


class temperatureDB( ):

    insert_stmt = f"INSERT IGNORE into {DB_settings.tableName} ( \
            DateTm, {DB_settings.tc1Name}, {DB_settings.tc2Name},{DB_settings.tc3Name},{DB_settings.tc4Name} ) \
            VALUES (%(DateTm)s, %(tc1)s, %(tc2)s, %(tc3)s, %(tc4)s)"
 
    def __init__( self, mode = "ro" ):
        if mode == "ro":
            self.dbuser="readmany"
            self.dbpw = ""
        elif mode == "rw":
            self.dbuser=DB_settings.user
            self.dbpw = DB_settings.password
        else:
            raise SE521DBError( "Invalid DB mode: " + mode )

        self.iomode = mode
        self.cnx = None
        self.cursor_temps = None
        self.errorcount = 0
        log.info( "Opening DB, {} mode".format( self.iomode ) )
        
        self.open()
        
    def open( self ):
    
        try:
            self.cnx = mysqlconn.connect( user=self.dbuser, password=self.dbpw,
                    host=DB_settings.dbHost, port=DB_settings.dbPort, database=DB_settings.dbName)

        except mysqlconn.Error as err:
            # this is ugly - the mysqldb and mysql.connector have very different exception structures
            # so try with lowest common denominator...
            log.exception(f"Error connecting to database: {err}")
            raise SE521DBError( f"Error connecting to database: {err}")
            
        self.cursor_temps= self.cnx.cursor(  )


    def add_data( self, data ):
        if self.cnx is None:
            self.open()
        try:
            self.cursor_temps.execute( temperatureDB.insert_stmt, data )
            
        except mysqlconn.Error as err:
            log.exception( "adding MySQL data: %s" % err )
            self.errorcount += 1
            self.cnx = None         # force reopen attempt
            if self.errorcount > 10:
                raise  SE521DBError( "too many failures writing DB" )

    def close( self ):
        self.close_cursor()
        if self.cnx is not None:
            self.cnx.commit()
            self.cnx.close()  
            self.cnx = None
                
    def close_cursor( self ):
        if self.cursor_temps is not None:
            self.cursor_temps.close()
            self.cursor_temps = None       

    
    
    

