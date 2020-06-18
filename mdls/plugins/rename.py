# Copyright 2017 Palantir Technologies, Inc.
import logging
import os

from mdls import hookimpl, uris

log = logging.getLogger(__name__)

@hookimpl
def mdls_rename(config, workspace, document, position, new_name):
    original_pagename = document.pagelink_at_position(position)
    log.debug("Executing rename of %s to %s", original_pagename, new_name)
    for doc_uri in workspace._docs_scanned:
        if os.path.splitext(workspace._docs_scanned[doc_uri].filename)[0] == pagename:
            #TODO rename file
            pass
        if pagename in workspace._docs_scanned[doc_uri].pagelinks:
            #TODO
            pass

    return {
        'documentChanges': [{
            'textDocument': {
                'uri': uris.uri_with(
                    document.uri, path=os.path.join(workspace.root_path, change.resource.path)
                ),
                'version': workspace.get_document(document.uri).version
            },
            'edits': [{
                'range': {
                    'start': {'line': 0, 'character': 0},
                    'end': {'line': _num_lines(change.resource), 'character': 0},
                },
                'newText': change.new_contents
            }]
        } for change in changeset.changes]
    }


def _num_lines(resource):
    "Count the number of lines in a `File` resource."
    return len(resource.read().splitlines())
