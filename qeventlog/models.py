#! /usr/bin/env python

import architect, logging, logtool
from django.db import models
from django_pgjsonb import JSONField

LOG = logging.getLogger (__name__)

@architect.install ("partition", type = "range", subtype = "date",
                    constraint = "month", column = "created")
class QEvent (models.Model):
  created = models.DateTimeField (db_index = True)
  timestamp = models.DecimalField (
    max_digits = 30, decimal_places = 6, null = True, blank = True,
    db_index = True)
  entity = models.CharField (max_length = 64, db_index = True)
  source = models.CharField (max_length = 64, db_index = True)
  data = JSONField (db_index = True, null = True, blank = True)

  @logtool.log_call
  @classmethod
  def bulk_import (cls, date_t, data):
    """WARNING: Do not call this with payloads of more than 10^3 key
    values, else you are likely to get timeouts.
    """
    dataset = []
    for entity in data:
      for source in data[entity]:
        for timestamp in data[entity][source]:
          record = {
            "created": date_t,
            "entity": entity,
            "source": source,
            "timestamp": timestamp,
            "data": data[entity][source][timestamp],
          }
          dataset.append (QEvent (**record))
    QEvent.objects.bulk_create (dataset) # pylint: disable = E1101

  class Meta: # pylint: disable=W0232,R0903,C1001
    ordering = ["created",]
    index_together = ("entity", "source", "timestamp")
