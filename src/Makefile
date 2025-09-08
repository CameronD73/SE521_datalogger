
DESTLOGS = /var/log/SE521
DEST = /usr/local/SE521
DESTBIN = $(DEST)/bin
DESTETC = $(DEST)/etc
DESTAWK = $(DEST)/scripts

PHP_MODE = 640
SH_MODE = 750
GROUPNAME=logfiles
USER=solar

install: installpy  

installpy: \
	$(DESTBIN)/SE521-logger.py \
	$(DESTBIN)/SE521_USB.py \
	$(DESTBIN)/DB_rooftemp.py


$(DEST):
	install --owner=$(USER) -g $(GROUPNAME) -m $(PHP_MODE) -d $@

$(DESTBIN):  $(DEST)
	install --owner=$(USER) -g $(GROUPNAME) -m $(PHP_MODE) -d $@


$(DESTBIN)/SE521-logger.py:	SE521-logger.py
	install --owner=$(USER) -g $(GROUPNAME) -m $(SH_MODE) -p $< $@

$(DESTBIN)/SE521_USB.py:	SE521_USB.py
	install --owner=$(USER) -g $(GROUPNAME) -m $(PHP_MODE) -p $< $@

$(DESTBIN)/DB_rooftemp.py:	DB_rooftemp.py
	install --owner=$(USER) -g $(GROUPNAME) -m $(PHP_MODE) -p $< $@

