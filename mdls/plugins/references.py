# Copyright 2017 Palantir Technologies, Inc.
import logging
from mdls import hookimpl, uris, _utils

log = logging.getLogger(__name__)


@hookimpl
def mdls_references(document, position, exclude_declaration=False):

    return []
    # Filter out builtin modules
    return [{
        'uri': uris.uri_with(document.uri, path=d.module_path) if d.module_path else document.uri,
        'range': {
            'start': {'line': d.line - 1, 'character': d.column},
            'end': {'line': d.line - 1, 'character': d.column + len(d.name)}
        }
    } for d in usages if not d.in_builtin_module()]
