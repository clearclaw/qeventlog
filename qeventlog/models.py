#! /usr/bin/env python

import architect, logging, logtool, uuid
from django.db import models, transaction, IntegrityError
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from model_utils import Choices
from model_utils.fields import StatusField

LOG = logging.getLogger (__name__)
DEFAULT_RETRY = 20

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
  @logtool.log_call
  @classmethod
  def record (cls, date_t, **kwargs):
    with transaction.atomic ():
      QEvent (created = date_t,
              timestamp = kwargs["timestamp"],
              event = kwargs["event"],
              task_id = kwargs["uuid"],
              data = kwargs,
            ).save ()
      if kwargs["event"] == "after_task_publish" and kwargs.get ("parent_id"):
        QChildTask (created = date_t,
                    timestamp = kwargs["timestamp"],
                    parent = kwargs.get ("parent_id"),
                    child = kwargs.get ("uuid")).save ()
      QTaskState.record (date_t, **kwargs)

  class Meta: # pylint: disable=W0232,R0903,C1001
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

  class Meta: # pylint: disable=W0232,R0903,C1001
    ordering = ["created", "timestamp"]
    index_together = ("parent", "child")

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
  retries = models.IntegerField (db_index = True, null = True, blank = True)
  status = StatusField (db_index = True)

  @logtool.log_call
  @classmethod
  def record (cls, date_t, **kwargs):
    for attempt in xrange (DEFAULT_RETRY):
      try:
        o = QTaskState.objects.get (task_id = uuid.UUID (kwargs["uuid"]))
        if ((kwargs.get ("retries", 0) > o.retries)
            or (cls._task_states.index (kwargs["event"])
                > cls._task_states.index (o.status))):
          o.timestamp = kwargs["timestamp"]
          o.retries = kwargs.get ("retries", 0)
          o.status = kwargs["event"]
          o.save ()
      except ObjectDoesNotExist:
        QTaskState (task_id = uuid.UUID (kwargs["uuid"]),
                    created = date_t,
                    timestamp = kwargs["timestamp"],
                    retries = kwargs.get ("retries", 0),
                    status = kwargs["event"],
                  ).save ()
      except IntegrityError:
        if attempt == DEFAULT_RETRY - 1:
          raise
        continue

  class Meta: # pylint: disable=W0232,R0903,C1001
    ordering = ["created",]
    index_together = ("created", "timestamp", "status")
