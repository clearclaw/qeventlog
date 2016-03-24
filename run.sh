#! /bin/bash

export DJANGO_SETTINGS_MODULE=qeventlog.settings
celery -A qeventlog.main worker -Q qeventlog -l debug -c 1

