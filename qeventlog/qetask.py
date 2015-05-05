#! /usr/bin/env python

import celery, logging, logtool, numbers, os, socket
from addict import Dict
from .models import QEvent

LOG = logging.getLogger (__name__)

class QETask (celery.Task):
  """Logs all local activity on the task.

  Note that this needs to be on both the sender and worker side as
  failures are processed on the sender and everything else on the
  worker.
  """

  @logtool.log_call (log_level = logging.INFO, log_exit = False,
                     log_rc = False)
  def record (self, typ, uuid = None, status = None, rc = None,
              args = None, kwargs = None, exc = None):
    record = Dict ()
    entity = "task-%s" % typ
    timestamp = logtool.now ()[0]
    record[entity][uuid][timestamp] = {
      "args": repr (args),
      "kwargs": repr (kwargs),
      "hostname": socket.gethostname (),
      "timestamp": timestamp,
      "pid": os.getpid (),
    }
    d = record[entity][uuid][timestamp]
    if status is not None:
      d["status"] = status
    if rc is not None:
      d["result"] = rc if isinstance (rc, numbers.Number) else str (rc)
    if exc:
      d["exception"] = repr (exc)
      d["traceback"] = logtool.log_fault_exc_str (exc, traceback = True)
    QEvent.bulk_import (record)

  @logtool.log_call (log_level = logging.INFO, log_exit = False,
                     log_rc = False)
  def after_return (self, status, rc, uuid, args, kwargs, einfo):
    self.record (typ = "after", uuid = uuid,
                 status = status, rc = rc,
                 args = args, kwargs = kwargs)
    super (QETask, self).after_return (status, rc, uuid, args,
                                       kwargs, einfo)

  @logtool.log_call (log_level = logging.ERROR, log_exit = False,
                     log_rc = False)
  def on_failure (self, exc, uuid, args, kwargs, einfo):
    self.record (typ = "failure", uuid = uuid,
                 args = args, kwargs = kwargs, exc = exc)
    super (QETask, self).on_failure (exc, uuid, args, kwargs, einfo)

  @logtool.log_call (log_level = logging.WARN, log_exit = False,
                     log_rc = False)
  def on_retry (self, exc, uuid, args, kwargs, einfo):
    self.record (typ = "retry", uuid = uuid,
                 args = args, kwargs = kwargs, exc = exc)
    super (QETask, self).on_retry (exc, uuid, args, kwargs, einfo)

  @logtool.log_call (log_level = logging.INFO, log_exit = False,
                     log_rc = False)
  def on_success (self, rc, uuid, args, kwargs):
    self.record (typ = "done", uuid = uuid, rc = rc,
                 args = args, kwargs = kwargs)
    super (QETask, self).on_success (rc, uuid, args, kwargs)
