# Copyright 2017 Palantir Technologies, Inc.

import logging

from mdls import hookimpl, _utils

log = logging.getLogger(__name__)


@hookimpl
def mdls_hover(document, position):
    word = document.word_at_position(position)

    contents.append(word)

    if not contents:
        return {'contents': ''}

    return {'contents': contents}
