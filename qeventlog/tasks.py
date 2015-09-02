#!/usr/bin/env python

import logging, logtool, qeventlog.main # pylint disable=unused-import
from celery import current_app
from qeventlog.models import QEvent

LOG = logging.getLogger (__name__)

@logtool.log_call
@current_app.task
def log (date_t, **kwargs):
  try:
    data = {
      kwargs["event"]: {
        kwargs["uuid"]: {
          kwargs["timestamp"]: kwargs
        }
      }
    }
    QEvent.bulk_import (date_t, data)
  except Exception as e:
    logtool.log_fault (e)
    raise
