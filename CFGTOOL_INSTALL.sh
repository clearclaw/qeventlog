#! /bin/sh

install -D -g root -o root -p -t /etc/qeventlog configs/*.templ
install -D -g root -o root -p configs/qeventlog.cfgtool /etc/cfgtool/module.d/qeventlog
