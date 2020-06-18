# Copyright 2017 Palantir Technologies, Inc.
import logging
from mdls import hookimpl
from mdls.lsp import SymbolKind

log = logging.getLogger(__name__)


@hookimpl
def mdls_document_symbols(config, workspace, document):
    if document is None:
        return []
    return [{
        'name': l.name,
        #'containerName': '',
        'location': {
            'uri': document.uri,
            'range': _range(l),
        },
        'kind': SymbolKind.String,
    } for l in document.pagelinks]

@hookimpl
def mdls_workspace_symbols(config, workspace, query):
    # TODO pick up documents only outside of workspace.documents from workspace._docs_scanned
    return [{
        'name': pagelink.name,
        #'containerName': '',
        'location': {
            'uri': doc.uri,
            'range': _range(pagelink),
        },
        'kind': SymbolKind.String,
    } for doc in workspace._docs_scanned.values() for pagelink in doc.pagelinks if query.lower() in pagelink.name.lower()]

def _range(pagelink):
    return {
        'start': {'line': pagelink.line, 'character': pagelink.start},
        'end': {'line': pagelink.line, 'character': pagelink.end}
    }
