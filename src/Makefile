
DESTLOGS = /var/log/SE521
DEST = /usr/local/SE521
DESTBIN = $(DEST)/bin

MODULE_MODE = 640
SH_MODE = 750
GROUPNAME=logfiles
USER=solar

install: installpy  

installpy: \
	$(DESTBIN)/SE521-logger.py \
	$(DESTBIN)/SE521_USB.py \
	$(DESTBIN)/SE521_dbcode.py \
	$(DESTBIN)/SE521_dbsettings.py


$(DEST):
	install --owner=$(USER) -g $(GROUPNAME) -m $(MODULE_MODE) -d $@

$(DESTBIN):  $(DEST)
	install --owner=$(USER) -g $(GROUPNAME) -m $(MODULE_MODE) -d $@


$(DESTBIN)/SE521-logger.py:	SE521-logger.py
	install --owner=$(USER) -g $(GROUPNAME) -m $(SH_MODE) -p $< $@

$(DESTBIN)/SE521_USB.py:	SE521_USB.py
	install --owner=$(USER) -g $(GROUPNAME) -m $(MODULE_MODE) -p $< $@

$(DESTBIN)/SE521_dbcode.py:	SE521_dbcode.py
	install --owner=$(USER) -g $(GROUPNAME) -m $(MODULE_MODE) -p $< $@

$(DESTBIN)/SE521_dbsettings.py:	SE521_dbsettings.py
	install --owner=$(USER) -g $(GROUPNAME) -m $(MODULE_MODE) -p $< $@

