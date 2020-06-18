# Copyright 2017 Palantir Technologies, Inc.
import logging
from mdls import hookimpl, uris, _utils

log = logging.getLogger(__name__)


@hookimpl
def mdls_definitions(config, document, position):

    return [
        {
            'uri': uris.uri_with(document.uri, path=d.module_path),
            'range': {
                'start': {'line': d.line - 1, 'character': d.column},
                'end': {'line': d.line - 1, 'character': d.column + len(d.name)},
            }
        }
        for d in definitions if d.is_definition() and _not_internal_definition(d)
    ]


def _not_internal_definition(definition):
    return (
        definition.line is not None and
        definition.column is not None and
        definition.module_path is not None and
        not definition.in_builtin_module()
    )
