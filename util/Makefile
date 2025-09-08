# makefile for Debian 13 server running the main service
# talking to the TC logger and recording to DB
#
all:	\
	/etc/systemd/system/SE521.service \
	/etc/systemd/system/unit-status-email@.service \
	/etc/udev/rules.d/10-SE521.rules

/etc/udev/rules.d/10-SE521.rules:	10-SE521.rules
	install -p --owner=root --mode=740 --group=root $< $@

/etc/systemd/system/SE521.service: SE521.service
	install -p --owner=root --mode=640 --group=root $< $@
	/bin/systemctl daemon-reload

/etc/systemd/system/unit-status-email@.service: unit-status-email.service 
	install -p --owner=root --mode=640 --group=root $< $@
	/bin/systemctl daemon-reload

