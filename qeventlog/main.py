#! /usr/bin/env python

import logging, logging.config, os, raven, raven.contrib.celery
from celery import Celery
from celery.signals import setup_logging
from django.conf import settings

from ._version import get_versions
__version__ = get_versions ()['version']
del get_versions

LOG = logging.getLogger (__name__)
DEFAULT_LOGCONF = "/etc/qeventlog/logging.conf"

os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "qeventlog.settings")
app = Celery ("qeventlog", include = ["qeventlog.tasks",])
app.config_from_object ("django.conf:settings")
app.autodiscover_tasks (lambda: settings.INSTALLED_APPS)
app_name = "qeventlog"
app_ver = __version__
sentry_dsn = settings.RAVEN_CONFIG["dsn"]
SENTRY = raven.Client (sentry_dsn,
                       auto_log_stacks = True,
                       release = "%s: %s" % (app_name, app_ver),
                       transport = raven.transport.http.HTTPTransport)
app.set_current ()

@setup_logging.connect
# @logtool.log_call
def setup_logging_handler (**kwargs): # pylint: disable=W0613
  logging.config.fileConfig (DEFAULT_LOGCONF,
                               disable_existing_loggers = False)
  raven.contrib.celery.register_logger_signal (SENTRY)
  raven.contrib.celery.register_signal (SENTRY)

if __name__ == "__main__":
  app.start()
