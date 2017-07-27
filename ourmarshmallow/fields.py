"""
Customized Fields for Our Marshmallow.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

from marshmallow.base import FieldABC
# Make marshmallow core and jsonapi fields importable from ourmarshmallow
from marshmallow_jsonapi.fields import *  # pylint: disable=wildcard-import,unused-wildcard-import


# Meta is part of marshmallow_jsonapi.fields
class MetaData(Meta):
    """ Per-field metadata wrapper. Turns another field into MetaData.
    Based on marshmallow.fields.List """
    def __init__(self, cls_or_instance, **kwargs):
        # Force dump_only=True.
        kwargs['dump_only'] = True

        super().__init__(**kwargs)

        if isinstance(cls_or_instance, type):
            if not issubclass(cls_or_instance, FieldABC):
                raise ValueError('The type of the metadata elements must be a subclass of '
                                 'marshmallow.base.FieldABC')
            self.container = cls_or_instance()
        else:
            if not isinstance(cls_or_instance, FieldABC):
                raise ValueError('The instances of the metadata elements must be of type '
                                 'marshmallow.base.FieldABC')
            self.container = cls_or_instance

    def _serialize(self, value, attr, obj):  # pylint: disable=arguments-differ
        return {attr: self.container._serialize(value, attr, obj)}  # pylint: disable=protected-access
