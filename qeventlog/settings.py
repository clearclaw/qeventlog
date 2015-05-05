#! /usr/bin/env python

import logging, logtool, sys

LOG = logging.getLogger (__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname (os.path.dirname (__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "DisprovedOptimizingConvertibleDehumidifyAllotmentMucilagesSacks"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []
APPEND_SLASH = False

# Application definition
INSTALLED_APPS = (
  "raven.contrib.django.raven_compat",
  "qeventlog",
)
MIDDLEWARE_CLASSES = ()

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = None
USE_I18N = False
USE_L10N = False
USE_TZ = False

LOGGING = "/etc/qeventlog/logging.conf"
LOGGING_CONFIG = "qeventlog.logs.logging_loader"

EXTERNAL_CONFIG = "/etc/qeventlog/qeventlog.conf"
execfile (EXTERNAL_CONFIG)

DESIRED_VARIABLES = [
  "LOGGING",
]
REQUIRED_VARIABLES = [
  "DATABASES",
  "RAVEN_CONFIG",
]

@logtool.log_call
def check_vars (wanted, provided):
  return [var for var in wanted if var not in provided]

missing = check_vars (DESIRED_VARIABLES, vars ())
if missing:
  print >> sys.stderr, "Missing desired configurations: %s" % missing
missing = check_vars (REQUIRED_VARIABLES, vars ())
if missing:
  print >> sys.stderr, "Missing required configurations: %s" % missing
  sys.exit (1)
