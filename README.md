# SE521_datalogger
Simple code to collect live data from Center SE521 4-channel thermocouple and store in Mysql/MariaDB database.

[Center Technology](https://www.centertek.com/product_d.php?lang=en&tb=1&id=383) make a relatively low priced instrument to measure data from thermocouples.
They provide software for collecting data from MS-Windows systems, but nothing for Linux.

This software is designed for continual data collection from the instrument with DB storage.
It was written to run on Debian-based systems but should be readily adaptible for any Linux system with python, a database and a type-A USB socket.

# System Setup
## packages required
These will vary depending on your Linux distribution. You will need:
1. database server: Mysql or MariaDB
2. python3
3. mysql support for python, such as Debian package python3-mysqldb or mysql package mysql-connector-python-py3
## system support
You can choose which of these parts you implement.
* Choose what permissions you will give to the USB device - whether it will be globally readable or restricted to a single user or group
* adjust udev rules in file util/10-SE521.rules accordingly
* Create a local user and possibly group according to above policy. My system was used for logging data from solar panels, hence the user name I chose was solar
*  if you are going to use systemD:
    * assign user and group to the SE521.service file
    * edit *util/unit-status-email.service* and assign a recipient address for the warning email 
* edit *util/Makefile* to install whichever bits you will need.

## database
Using whatever db management software you prefer...
* examine  the script *util/create_DB_and_table.sql*. If you are setting this up for a specific situation, then you might want to edit the names of DB, table and columns first to more accurately reflect this situation.
* The table by default uses a MyISAM engine because the requirements are trivial.
* using  whatever client software you prefer and with admin permissions:
    * run the script *util/create_DB_and_table.sql* using. 
    * create DB user and password and assign suitable write access to the new DB.
 

## software
In the _src_ directory, 
* copy the configuration file *SE521_dbsettings_template.py*  to the working version *SE521_dbsettings.py*
    * edit  *SE521_dbsettings.py*  to assign appropriate names, passwords, etc.
* check the parameters near the start of the file *SE521_logger.py* - if you want to record data with significant changes much shorter than a 1-minute timescale then you will also need to modify the code itself.
* edit *Makefile* to assign user and group. You might want to install elsewhere - the default is under /usr/local/SE521. The subsidiary python files are loaded from the same directory as the main program.
* *Make install*

# Initialisation

# Operation
Once it is running in daemon mode then it should stay happy.

If the instrument loses USB power for a fairly short length of time then it will power off and not come on again automatically.  This is the reason for the messy systemd services, that create an email if the system repeatedly fails.