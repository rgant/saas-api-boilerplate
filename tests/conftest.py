"""
Configuration for py.tests. Does things like setup the database and flask app for individual tests.
https://gist.github.com/alexmic/7857543
"""
import warnings

from common import log


warnings.simplefilter("error")  # Make All warnings errors while testing.

# Setup Stream logging for py.test so log messages get output on errors too.
# If something else sets up logging first then this won't trigger.
# For example: db.py calling logging.info() or such.
log.init_logging()
