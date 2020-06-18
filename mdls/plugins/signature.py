# Copyright 2017 Palantir Technologies, Inc.
import logging
import re
from mdls import hookimpl, _utils

log = logging.getLogger(__name__)

@hookimpl
def mdls_signature_help(document, position):
    signature = None
    #if not signatures:
    #    return {'signatures': []}
    return {'signatures': []}
