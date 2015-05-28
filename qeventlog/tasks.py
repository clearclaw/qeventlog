#!/usr/bin/env python

import logging, logtool, qeventlog.main # pylint disable=W0611
from celery import current_app
from qeventlog.models import QEvent

LOG = logging.getLogger (__name__)

@logtool.log_call
@current_app.task
def log (**kwargs):
  try:
    data = {
      kwargs["event"]: {
        kwargs["uuid"]: {
          kwargs["timestamp"]: kwargs
        }
      }
    }
    QEvent.bulk_import (data)
  except Exception as e:
    logtool.log_fault (e)
    raise
