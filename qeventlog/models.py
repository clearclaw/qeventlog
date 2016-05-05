#! /usr/bin/env python

import architect, datetime, logging, logtool
from django.db import models, transaction
from django.contrib.postgres.fields import JSONField

LOG = logging.getLogger (__name__)
DEFAULT_RETRY = 20
TASKNAME_LEN = 128

class QTaskType (models.Model):
  type = models.CharField (unique = True, null = True, blank = True,
                           max_length = TASKNAME_LEN, db_index = True)

  class Meta: # pylint: disable=no-init,too-few-public-methods,old-style-class
    ordering = ["type",]

@architect.install ("partition", type = "range", subtype = "date",
                    constraint = "month", column = "created")
class QEvent (models.Model):
  created = models.DateTimeField (db_index = True)
  timestamp = models.DecimalField (
    max_digits = 30, decimal_places = 6, null = True, blank = True,
    db_index = True)
  event = models.CharField (max_length = 64, db_index = True)
  task_id = models.UUIDField (db_index = True)
  type = models.ForeignKey (QTaskType)
  data = JSONField (db_index = True, null = True, blank = True)

  @logtool.log_call
  @classmethod
  def record (cls, time_t, **kwargs): # pylint: disable=unused-argument
    with transaction.atomic ():
      now = datetime.datetime.utcnow ()
      name, created = ( # pylint: disable=unused-variable
        QTaskType.objects.get_or_create ( # pylint: disable=no-member
          type = kwargs["task"]))
      QEvent (created = now,
              timestamp = time_t,
              event = kwargs["event"],
              task_id = kwargs["task_id"],
              data = kwargs,
              type = name,
            ).save ()
      if kwargs["event"] == "after_task_publish" and kwargs.get ("parent_id"):
        QChildTask (created = now,
                    timestamp = kwargs["timestamp"],
                    parent = kwargs.get ("parent_id"),
                    child = kwargs.get ("task_id")).save ()

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
