#! /usr/bin/env python

import architect, datetime, logging, logtool, numbers
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from model_utils.models import TimeStampedModel

LOG = logging.getLogger (__name__)
DEFAULT_STRLEN = 2048
DEFAULT_KEYLEN = 64

@architect.install ("partition", type = "range", subtype = "date", 
                    constraint = "month", column = "date")
class QEvent (TimeStampedModel):
  date = models.DateTimeField (auto_now = False, auto_now_add = False,
                               null = False, blank = False)
  entity = models.CharField (max_length = 64, db_index = True)
  source = models.CharField (max_length = 64, db_index = True)
  timestamp = models.DecimalField (
    max_digits = 30, decimal_places = 6, null = True, blank = True,
    db_index = True)
  keyname = models.CharField (max_length = DEFAULT_KEYLEN, db_index = True)
  value_num = models.DecimalField (
    max_digits = 30, decimal_places = 6, null = True, blank = True)
  value_str = models.CharField (
    max_length = DEFAULT_STRLEN, db_index = True, null = True, blank = True)

  @logtool.log_call
  @classmethod
  def bulk_import (cls, data):
    """WARNING: Do not call this with payloads of more than 10^3 key
    values, else you are likely to get timeouts.
    """
    for entity in data:
      for source in data[entity]:
        for timestamp in data[entity][source]:
          for k, v in (data[entity][source][timestamp]).items ():
            record = {
              "entity": entity,
              "source": source,
              "timestamp": timestamp,
              "keyname": str (k),
            }
            v_name = ("value_num" if isinstance (v, numbers.Number)
                      else "value_str")
            val = (v if isinstance (v, numbers.Number)
                   else str (v)[:DEFAULT_STRLEN])
            try:
              obj = QEvent.objects.get (**record)
              record [v_name] = val
              setattr (obj, v_name, val)
            except ObjectDoesNotExist:
              record[v_name] = val
              obj = QEvent (**record)
            obj.save ()
            # LOG.info ("Key values: %s", record)

  @logtool.log_call
  def save ():
    self.date = datetime.datetime.fromtimestamp (self.timestamp)
    super (QEvent, self).save ()
            
  class Meta:
    ordering = ["created",]
    index_together = ("entity", "source", "timestamp", "keyname")
