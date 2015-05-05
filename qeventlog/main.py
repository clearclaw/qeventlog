#! /usr/bin/env python

import django, logging, logtool, multiprocessing, raven, setproctitle, sys
from django.conf import settings
from .qeventlog import QEventLog

LOG = logging.getLogger (__name__)
DEFAULT_PROCNAME = "qeventlog"

@logtool.log_call
def main ():
  try:
    django.setup ()
    multiprocessing.current_process ().name = DEFAULT_PROCNAME
    setproctitle.setproctitle (DEFAULT_PROCNAME)
    sentry = raven.Client (settings.RAVEN_CONFIG["dsn"])
    QEventLog (sentry).run ()
    sys.exit (0)
  except KeyboardInterrupt:
    LOG.info ("KeyboardInterrupt: exiting...")
    sys.exit (0)
  except Exception as e:
    logtool.log_fault (e)
    exc_info = None
    try:
      exc_info = sys.exc_info ()
      sentry = raven.Client (settings.RAVEN_CONFIG["dsn"])
      sentry.captureException (exc_info)
    finally:
      del exc_info
    raise
  sys.exit (1)

if __name__ == "__main__":
  main ()
