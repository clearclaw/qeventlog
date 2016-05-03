#!/usr/bin/env python

from __future__ import absolute_import
import logging, logtool, raven, sys
from celery import current_app
from celery.exceptions import Retry
from django.conf import settings
import qeventlog.main # pylint: disable=unused-import
from .models import QEvent
from .qetask import QETask

from ._version import get_versions
__version__ = get_versions ()['version']
__version_info__ = get_versions ()
del get_versions

LOG = logging.getLogger (__name__)

@logtool.log_call
def sentry_exception (e, request, message = None):
  """Yes, this eats exceptions"""
  try:
    app_name = "qeventlog"
    app_ver = __version__
    sentry_dsn = settings.RAVEN_CONFIG["dsn"]
    sentry_tags = {"component": app_name,
                   "version": app_ver,}
    sentry = raven.Client (sentry_dsn,
                           auto_log_stacks = True,
                           release = "%s: %s" % (app_name, app_ver),
                           transport = raven.transport.http.HTTPTransport)
    logtool.log_fault (e, message = message, level = logging.INFO)
    data = {
      "job": request,
    }
    if message:
      data["message"] = message
    sentry.extra_context (data)
    if e is not None:
      einfo = sys.exc_info ()
      rc = sentry.captureException (einfo, **sentry_tags)
      del einfo
    else:
      rc = sentry.capture (**sentry_tags)
    LOG.error ("Sentry filed: %s", rc)
  except Exception as ee:
    logtool.log_fault (ee, message = "FAULT: Problem logging exception.",
                       level = logging.INFO)

@logtool.log_call
def retry_handler (task, e):
  try:
    LOG.info ("Retrying.  Attempt: #%s", task.request.retries)
    raise task.retry (exc = e, max_retries = settings.FAIL_RETRYCOUNT,
                      countdown = (settings.FAIL_WAITTIME
                                   * (task.request.retries + 1)))
  except Retry: # Why yes, we're retrying
    raise
  except: # pylint: disable=W0702
    LOG.error ("Max retries reached: %s  GIVING UP!", task.request.retries)
    sentry_exception (e, task.request)
    raise

#
# Tasks
#

@logtool.log_call
@current_app.task (bind = True, base = QETask)
def log (self, time_t, *args, **kwargs): # pylint: disable=unused-argument
  try:
    QEvent.record (time_t, **kwargs)
  except Exception as e:
    retry_handler (self, e)
