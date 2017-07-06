"""
Logging Classes for Papertrail SysLogHandler, Flask debug run and py.test logging.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.",
          file=sys.stderr)

import logging
import logging.handlers
import os
import socket


class RainbowLogFormatter(logging.Formatter):
    """ Adds a new key to the format string: %(colorlevelname)s. """
    # http://kishorelive.com/2011/12/05/printing-colors-in-the-terminal/
    levelcolors = {
        'CRITICAL' : '\033[4;31mCRITICAL\033[0m',  # Underlined Red Text
        'ERROR' : '\033[1;31mERROR\033[0m',        # Bold Red Text
        'WARN' : '\033[1;33mWARNING\033[0m',       # Bold Yellow Text
        'WARNING' : '\033[1;33mWARNING\033[0m',    # Bold Yellow Text
        'INFO' : '\033[0;32mINFO\033[0m',          # Light Green Text
        'DEBUG' : '\033[0;34mDEBUG\033[0m',        # Light Blue Text
        'NOTSET' : '\033[1:30mNOTSET\033[0m'       # Bold Black Text
    }

    def format(self, record):
        """ Adds the new colorlevelname to record and then calls the super. """
        record.colorlevelname = self.levelcolors[record.levelname]
        return super().format(record)


class ContextFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """ Add hostname and env-ironment attributes for logging. """
    hostname = socket.gethostname()
    env = os.environ.get('ENV', 'dev')
    app = 'backend'

    def filter(self, record):
        record.hostname = self.hostname
        record.env = self.env
        record.app = self.app
        return True


class PapertrailHandler(logging.handlers.SysLogHandler):
    """ Setup custom filter values and a formatter for logging to Papertrail. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addFilter(ContextFilter())


def init_logging(level=logging.INFO):
    """ Setup Logging For py.test, running in debug mode. """
    frmt = '%(colorlevelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s'
    formatter = RainbowLogFormatter(frmt)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.basicConfig(level=level, handlers=(handler,)) #, filename='out.log')
