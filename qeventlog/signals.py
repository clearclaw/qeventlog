#! /usr/bin/env python

import logging, logging.config, logtool, os
from celery import Celery
from celery.signals import setup_logging
from django.conf import settings

LOG = logging.getLogger (__name__)
DEFAULT_LOGCONF = "/etc/qeventlog/logging.conf"

@setup_logging.connect
@logtool.log_call
def setup_logging_handler (**kwargs): # pylint: disable=W0613
  logging.config.fileConfig (DEFAULT_LOGCONF,
                             disable_existing_loggers = False)
