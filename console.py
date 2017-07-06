#! /usr/bin/env python -i
""" Load some useful stuff into the console when running python interactively. """
import os
import sys

from common import log

def _set_prompt():
    """ Color code the Python prompt based on environment. """
    env = os.environ.get('ENV', 'dev')
    color = {'dev': '32',  # Green
             'stage': '33',  # Yellow
             'prod': '31'}.get(env)  # Red
    sys.ps1 = '\001\033[1;%sm\002>>> \001\033[0m\002' % color
    sys.ps2 = '\001\033[1;%sm\002... \001\033[0m\002' % color

log.init_logging(log.logging.DEBUG)
_set_prompt()
del sys
del os
del _set_prompt

# Do this last so that logging is setup first.
import models  # pylint: disable=unused-import,wrong-import-position
print('import models')
