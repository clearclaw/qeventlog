#! /bin/sh

install -D -g root -o root -p -t /etc/qeventlog configs/*.templ
install -D -g root -o root -p configs/qeventlog.cfgtool /etc/cfgtool/module.d/qeventlog
install -D -g root -o root -p configs/qeventlog.upstart.conf.templ /etc/init/qeventlog.conf
