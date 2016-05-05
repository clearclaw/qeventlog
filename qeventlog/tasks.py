#!/usr/bin/env python

from __future__ import absolute_import
import logging, logtool, sys
from celery import current_app
from celery.exceptions import Retry
from django.conf import settings
import qeventlog.main # pylint: disable=unused-import
from .main import SENTRY
from .models import QEvent
from .qetask import QETask

from ._version import get_versions
__version__ = get_versions ()['version']
del get_versions

LOG = logging.getLogger (__name__)

@logtool.log_call
def sentry_exception (e, request, message = None):
  """Yes, this eats exceptions"""
  try:
    logtool.log_fault (e, message = message, level = logging.INFO)
    data = {
      "job": request,
    }
    if message:
      data["message"] = message
    SENTRY.extra_context (data)
    einfo = sys.exc_info ()
    rc = SENTRY.captureException (einfo)
    del einfo
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
    LOG.info ("Received: %s for task: %s",
              kwargs.get ("event"), kwargs.get("task_id"))
    QEvent.record (time_t, **kwargs)
  except Exception as e:
    retry_handler (self, e)
