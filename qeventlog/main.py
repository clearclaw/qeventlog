#! /usr/bin/env python

import logging, logging.config, os
from celery import Celery
from celery.signals import setup_logging
from django.conf import settings

LOG = logging.getLogger (__name__)
DEFAULT_LOGCONF = "/etc/qeventlog/logging.conf"

os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "qeventlog.settings")
app = Celery ("qeventlog", include = ["qeventlog.tasks",])
app.config_from_object ("django.conf:settings")
app.autodiscover_tasks (lambda: settings.INSTALLED_APPS)
app.set_current ()

@setup_logging.connect
# @logtool.log_call
def setup_logging_handler (**kwargs): # pylint: disable=W0613
  logging.config.fileConfig (DEFAULT_LOGCONF,
                               disable_existing_loggers = False)

if __name__ == "__main__":
  app.start()
