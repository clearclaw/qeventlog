#! /usr/bin/env python

import logging, logtool, numbers, os, sys
from retryp import retryp
from addict import Dict
from celery import Celery
from .models import QEvent

LOG = logging.getLogger (__name__)

class QEventLog (object):

  @logtool.log_call
  def __init__ (self, sentry):
    os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "qeventlog.settings")
    self.app = Celery ("qeventlog")
    self.app.config_from_object ("django.conf:settings")
    self.sentry = sentry
    self.state = self.app.events.State ()

  @logtool.log_call
  def sanitise_event (self, event):
    rc = dict ()
    for k, v in event.items ():
      rc[k] = v if isinstance (v, numbers.Number) else str (v)
    return rc

  @logtool.log_call ()
  def sentry_exception (self, e, event, message = None):
    try:
      logtool.log_fault (e, message = message)
      data = {
        "event": event,
        "message": message
      }
      self.sentry.extra_context (data)
      exc_info = None
      try:
        exc_info = sys.exc_info ()
        self.sentry.captureException (exc_info)
      finally:
        del exc_info
    except Exception as ee:
      logtool.log_fault (ee, message = "FAULT: Problem logging exception.")

  @logtool.log_call ()
  def sentry_event (self, event, message = None):
    try:
      LOG.error ("Recording failure event: %s", event)
      event = self.sanitise_event (event)
      data = {
        "event": event,
        "message": message,
      }
      self.sentry.extra_context (data)
      self.sentry.captureMessage (message, event = event, data = data)
    except Exception as e:
      logtool.log_fault (e, message = "FAULT: Problem logging failure.")

  @logtool.log_call
  def failed (self, event):
    try:
      self.state.event (event)
      event["mp_task"] = self.state.tasks.get (event["uuid"])
      event = self.sanitise_event (event)
    except Exception as e:
      self.sentry_exception (
        e, event, message = "Problem populating failure event.")
    self.sentry_event (event, message = "Failed task")
    self.record (event)

  @retryp (expose_last_exc = True, log_faults = True,
           log_faults_level = logging.ERROR)
  @logtool.log_call
  def save_event (self, data):
    QEvent.bulk_import (data)

  @logtool.log_call
  def record (self, event):
    self.state.event (event)
    event = self.sanitise_event (event)
    if event["type"] in {"task-retried", "task-revoked", "task-failed"}:
      LOG.error ("Task problem: %s for %s", event["type"], event)
    record = Dict ()
    record[event["type"]][event["uuid"]][event["timestamp"]] = event
    self.save_event (record)

  @logtool.log_call
  def run (self):
    while True:
      try:
        with self.app.connection () as connection:
          recv = self.app.events.Receiver (connection, handlers = {
            "task-failed": self.failed,
            "worker-heartbeat": self.state.event,
            "worker-online": self.state.event,
            "worker-offline": self.state.event,
            "*": self.record,
          })
          recv.capture (limit = None, timeout = None, wakeup = True)
      except Exception as e:
        self.sentry_exception (e, {}, message = "Problem recording events.")
