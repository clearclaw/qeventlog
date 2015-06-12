#! /usr/bin/env python

import logging, logging.config, logtool, os
from celery import Celery
from celery.signals import setup_logging
from django.conf import settings

LOG = logging.getLogger (__name__)

os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "qeventlog.settings")
app = Celery ("qeventlog", include = ["qeventlog.tasks",])
app.config_from_object ("django.conf:settings")
app.autodiscover_tasks (lambda: settings.INSTALLED_APPS)
app.set_current ()

if __name__ == "__main__":
  app.start()
