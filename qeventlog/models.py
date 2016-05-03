#! /usr/bin/env python

import architect, datetime, logging, logtool, retryp, uuid
from django.db import models, transaction
from django.contrib.postgres.fields import JSONField
from model_utils import Choices
from model_utils.fields import StatusField

LOG = logging.getLogger (__name__)
DEFAULT_RETRY = 20
TASKNAME_LEN = 128

@architect.install ("partition", type = "range", subtype = "date",
                    constraint = "month", column = "created")
class QEvent (models.Model):
  created = models.DateTimeField (db_index = True)
  timestamp = models.DecimalField (
    max_digits = 30, decimal_places = 6, null = True, blank = True,
    db_index = True)
  event = models.CharField (max_length = 64, db_index = True)
  task_id = models.UUIDField (db_index = True)
  data = JSONField (db_index = True, null = True, blank = True)

  # Because there's not a clear way to have pre and post-save hooks on
  # save() execute in the same transaction.
  @retryp.retryp (count = 5, delay = 0, expose_last_exc = True)
  @logtool.log_call
  @classmethod
  def record (cls, time_t, **kwargs): # pylint: disable=unused-argument
    with transaction.atomic ():
      now = datetime.datetime.utcnow ()
      QEvent (created = now,
              timestamp = time_t,
              event = kwargs["event"],
              task_id = kwargs["uuid"],
              data = kwargs,
            ).save ()
      if kwargs["event"] == "after_task_publish" and kwargs.get ("parent_id"):
        QChildTask (created = now,
                    timestamp = kwargs["timestamp"],
                    parent = kwargs.get ("parent_id"),
                    child = kwargs.get ("uuid")).save ()
      QTaskState.record (now, **kwargs)

  class Meta: # pylint: disable=no-init,too-few-public-methods,old-style-class
    ordering = ["created",]
    index_together = ("event", "task_id", "timestamp")

@architect.install ("partition", type = "range", subtype = "date",
                    constraint = "month", column = "created")
class QChildTask (models.Model):
  created = models.DateTimeField (db_index = True)
  timestamp = models.DecimalField (
    max_digits = 30, decimal_places = 6, null = True, blank = True,
    db_index = True)
  parent = models.UUIDField (db_index = True)
  child = models.UUIDField (db_index = True)

  class Meta: # pylint: disable=no-init,too-few-public-methods,old-style-class
    ordering = ["created", "timestamp"]
    index_together = ("parent", "child")

class QTaskName (models.Model):
  name = models.CharField (unique = True, max_length = TASKNAME_LEN,
                           db_index = True)

  class Meta: # pylint: disable=no-init,too-few-public-methods,old-style-class
    ordering = ["name",]

@architect.install ("partition", type = "range", subtype = "date",
                    constraint = "month", column = "created")
class QTaskState (models.Model):
  # Sorted by their expected order of arrival
  _task_states = ["before_task_publish", "after_task_publish",
                  "task_prerun", "task_retry", "task_postrun",
                  "task_success", "task_failure", "task_revoked",]
  STATUS = Choices (*_task_states)
  task_id = models.UUIDField (db_index = True, primary_key = True)
  created = models.DateTimeField (db_index = True)
  timestamp = models.DecimalField (
    max_digits = 30, decimal_places = 6, null = True, blank = True,
    db_index = True)
  task = models.ForeignKey (QTaskName)
  retries = models.IntegerField (db_index = True, null = True, blank = True)
  status = StatusField (db_index = True)

  @logtool.log_call
  @classmethod
  def record (cls, now, **kwargs):
    name, created = ( # pylint: disable=W0612
            QTaskName.objects.get_or_create ( # pylint: disable=no-member
            name = kwargs["task"]))
    o, created = QTaskState.objects.get_or_create ( # pylint: disable=no-member
      task_id = uuid.UUID (kwargs["uuid"]),
      defaults = {
        "created": now,
        "timestamp": kwargs["timestamp"],
        "task": name,
        "retries": kwargs.get ("retries", 0),
        "status": kwargs["event"],
      })
    if created or ((kwargs.get ("retries", 0) > o.retries)
                   or (cls._task_states.index (kwargs["event"])
                       > cls._task_states.index (o.status))):
      o.timestamp = kwargs["timestamp"]
      o.retries = kwargs.get ("retries", 0)
      o.status = kwargs["event"]
      o.save ()

  class Meta: # pylint: disable=no-init,too-few-public-methods,old-style-class
    ordering = ["created",]
    index_together = ("created", "timestamp", "status")
