#! /bin/sh

install -g root -o root -p -m 0644 configs/qeventlog.cfgtool /etc/cfgtool/module.d/qeventlog
install -g root -o root -p -m 0755 -d /etc/qeventlog
install -g root -o root -p -m 0644 -t /etc/qeventlog configs/*.templ
install -D -g root -o root -p configs/qeventlog.upstart.conf.templ /etc/init/qeventlog.conf.templ
install -D -g root -o root -p -t /etc/qeventlog configs/*.templ
cfgtool write qeventlog -f
