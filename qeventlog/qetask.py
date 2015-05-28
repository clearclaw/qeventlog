#! /usr/bin/env python

import celery, json, logging, logtool, os, socket, time
from celery import signals

LOG = logging.getLogger (__name__)

@logtool.log_call (log_rc = False) # Too noisy
def send_event (event):
  # pylint: disable=E0611
  celery.execute.send_task (
    "qeventlog.tasks.log",
    kwargs = event,
    exchange = "qeventlog",
    queue = "qeventlog")

@logtool.log_call (log_exit = False)
def get_event (event):
  return {
    "event": event,
    "hostname": socket.gethostname (),
    "pid": os.getpid (),
    "timestamp": time.time (),
  }

@signals.before_task_publish.connect
@logtool.log_call (log_exit = False)
def qetask_before_task_publish (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  body = kwargs["body"]
  event = get_event ("before_task_publish")
  event.update ({
    "args": str (body["args"]),
    "eta": body["eta"],
    "expires": body["expires"],
    "exchange": kwargs["exchange"],
    "kwargs": json.dumps (body["kwargs"]),
    "task": body["task"],
    "retries": body["retries"],
    "uuid": body["id"],
  })
  send_event (event)

@signals.after_task_publish.connect
@logtool.log_call (log_exit = False)
def qetask_after_task_publish (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  body = kwargs["body"]
  event = get_event ("after_task_publish")
  event.update ({
    "args": str (body["args"]),
    "eta": body["eta"],
    "expires": body["expires"],
    "exchange": kwargs["exchange"],
    "kwargs": json.dumps (body["kwargs"]),
    "task": body["task"],
    "retries": body["retries"],
    "uuid": body["id"],
  })
  send_event (event)

@signals.task_prerun.connect
@logtool.log_call (log_exit = False)
def qetask_task_prerun (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_prerun")
  event.update ({
    "args": str (kwargs["args"]),
    "codepoint": str (kwargs["task"]),
    "kwargs": json.dumps (kwargs["kwargs"]),
    "uuid": kwargs["task_id"],
  })
  send_event (event)

@signals.task_postrun.connect
@logtool.log_call (log_exit = False)
def qetask_task_postrun (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_postrun")
  event.update ({
    "args": str (kwargs["args"]),
    "codepoint": str (kwargs["task"]),
    # Duration?
    "kwargs": json.dumps (kwargs["kwargs"]),
    "retval": str (kwargs["retval"]),
    "state": kwargs["state"],
    "uuid": kwargs["task_id"],
  })
  send_event (event)

@signals.task_retry.connect
@logtool.log_call (log_exit = False)
def qetask_task_retry (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_retry")
  request = kwargs["request"]
  event.update ({
    "args": str (request.args),
    "eta": request.eta,
    "exception": str (kwargs["reason"]),
    "kwargs": json.dumps (request.kwargs),
    "expires": request.expires,
    "retries": request.retries,
    "traceback": request.einfo.traceback,
    "uuid": request.id,
  })
  send_event (event)

# Not used as the signal hase ~no useful propertiy data, just the
# sender codepoint and the retval.
# @signals.task_success.connect
# @logtool.log_call (log_exit = False)
# def qetask_task_success (**kwargs):
#  pass

@signals.task_failure.connect
@logtool.log_call (log_exit = False)
def qetask_task_failure (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_failure")
  event.update ({
    "args": str (kwargs["args"]),
    "kwargs": json.dumps (kwargs["kwargs"]),
    "exception": str (kwargs["einfo"].exception),
    "traceback": kwargs["einfo"].traceback,
    "uuid": kwargs["task_id"],
  })
  send_event (event)

@signals.task_revoked.connect
@logtool.log_call (log_exit = False)
def qetask_task_revoked (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_revoked")
  event.update ({
    "expired": kwargs["expired"],
    "signum": kwargs["signum"],
    "terminated": kwargs["terminated"],
    "uuid": kwargs["task_id"],
  })
  send_event (event)
