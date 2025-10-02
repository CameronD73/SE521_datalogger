"""
SE521_dbsettings
Python class to provide site configuration data for  mysql database
vim: sw=4 ts=4 expandtab
"""


class DB_settings( ):

    user = "USER-NAME-HERE"
    password = "USER-PASSWD-HERE"
 
    dbHost = "127.0.0.1"
    dbPort = 3306     # not a string
    dbName = "SE521"
    tableName = "temperatures"
    # column names assigned to DB ... for thermocouples 1 to 4 on unit
    tc1Name = "tc1"
    tc2Name = "tc2"
    tc3Name = "tc3"
    tc4Name = "tc4"

    

    
    
    

