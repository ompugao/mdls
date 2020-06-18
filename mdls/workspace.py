# Copyright 2017 Palantir Technologies, Inc.
import io
import logging
import os
import re

try:
    from re import Scanner
except ImportError:
    from sre import Scanner

from . import lsp, uris, _utils
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

log = logging.getLogger(__name__)

MARKDOWN_FILE_EXTENSIONS = ('.md', '.markdown')

# TODO: this is not the best e.g. we capture numbers
RE_START_WORD = re.compile('[A-Za-z_0-9]*$')
RE_END_WORD = re.compile('^[A-Za-z_0-9]*')
RE_PAGELINK = re.compile(r"\[\[\s*(.*?)\s*\]\]")

class PageLink(object):
    def __init__(self, name, line, start, end):
        self.name = name
        self.line = line
        self.start = start
        self.end = end
    def __str__(self):
        return f"PageLink: {self.name} at line: {self.line} ({self.start}-{self.end})"

class MarkdownFileEventHandler(PatternMatchingEventHandler):
    def __init__(self, workspace):
        super(MarkdownFileEventHandler, self).__init__(patterns=set(['*'+e for e in MARKDOWN_FILE_EXTENSIONS]))
        self.workspace = workspace

        for ext in MARKDOWN_FILE_EXTENSIONS:
            for filename in _utils.find_files(workspace._root_path, '*' + ext):
                doc_uri = uris.from_fs_path(filename)
                # file will be read inside Document class if needed
                self.workspace._docs_scanned[doc_uri] = self.workspace._create_document(doc_uri, source=None, version=None)

    def on_moved(self, event):
        if event.is_directory:
            return
        doc_uri_src = uris.from_fs_path(event.src_path)
        doc_uri_dest = uris.from_fs_path(event.dest_path)
        self.workspace._docs_scanned.pop(doc_uri_src, None)
        self.workspace._docs_scanned[doc_uri_dest] = self.workspace._create_document(doc_uri_dest, source=None, version=None)

    def on_created(self, event):
        if event.is_directory:
            return
        doc_uri = uris.from_fs_path(event.src_path)
        if not doc_uri in self.workspace._docs_scanned:
            # file will be read inside Document class if needed
            self.workspace._docs_scanned[doc_uri] = self.workspace._create_document(doc_uri, source=None, version=None)


    def on_deleted(self, event):
        if event.is_directory:
            return
        doc_uri = uris.from_fs_path(event.src_path)
        self.workspace._docs_scanned.pop(doc_uri, None)

    def on_modified(self, event):
        if not event.is_directory:
            doc_uri = uris.from_fs_path(event.src_path)
            if doc_uri in self.workspace._docs_scanned:
                # file will be read inside Document class if needed
                self.workspace._docs_scanned[doc_uri]._source = None

class Workspace(object):

    M_PUBLISH_DIAGNOSTICS = 'textDocument/publishDiagnostics'
    M_APPLY_EDIT = 'workspace/applyEdit'
    M_SHOW_MESSAGE = 'window/showMessage'

    def __init__(self, root_uri, endpoint, config=None):
        self._config = config
        self._root_uri = root_uri
        self._endpoint = endpoint
        self._root_uri_scheme = uris.urlparse(self._root_uri)[0]
        self._root_path = uris.to_fs_path(self._root_uri)
        self._docs = {} # uri -> Document
        self._docs_scanned = {} # uri -> Document
        self._observer = None
        self.update_config(self._config)

    def __del__(self, ):
        self.finalize()

    def finalize(self, ):
        if self._observer:
            self._observer.stop()
            #self._observer.join() #TODO should we wait?
        self._observer = None

    @property
    def documents(self):
        return self._docs

    @property
    def root_path(self):
        return self._root_path

    @property
    def root_uri(self):
        return self._root_uri

    def is_local(self):
        return (self._root_uri_scheme == '' or self._root_uri_scheme == 'file') and os.path.exists(self._root_path)

    def get_document(self, doc_uri):
        """Return a managed document if-present, else create one pointing at disk.

        See https://github.com/Microsoft/language-server-protocol/issues/177
        """
        return self._docs.get(doc_uri) or self._create_document(doc_uri)

    def put_document(self, doc_uri, source, version=None):
        self._docs[doc_uri] = self._create_document(doc_uri, source=source, version=version)

    def rm_document(self, doc_uri):
        self._docs.pop(doc_uri)

    def update_document(self, doc_uri, change, version=None):
        self._docs[doc_uri].apply_change(change)
        self._docs[doc_uri].version = version

    def update_config(self, config):
        self._config = config
        cap_client_workspaceedit = self._config.capabilities.get('workspace', {}).get('workspaceEdit', None) #'didChangeWatchedFiles'?
        #if not cap_client_workspaceedit and self.is_local():
        if self.is_local():
            if self._observer is not None:
                self._observer.stop()
                self._observer.join(1.0)
            event_handler = MarkdownFileEventHandler(self)
            self._observer = Observer()
            self._observer.schedule(event_handler, self._root_path, recursive=True)
            self._observer.start()

        for doc_uri in self.documents:
            self.get_document(doc_uri).update_config(config)

    def apply_edit(self, edit):
        return self._endpoint.request(self.M_APPLY_EDIT, {'edit': edit})

    def publish_diagnostics(self, doc_uri, diagnostics):
        self._endpoint.notify(self.M_PUBLISH_DIAGNOSTICS, params={'uri': doc_uri, 'diagnostics': diagnostics})

    def show_message(self, message, msg_type=lsp.MessageType.Info):
        self._endpoint.notify(self.M_SHOW_MESSAGE, params={'type': msg_type, 'message': message})

    def _create_document(self, doc_uri, source=None, version=None):
        return Document(
            doc_uri, self, source=source, version=version,
            local=self.is_local(),
            config=self._config,
        )


class Document(object):

    def __init__(self, uri, workspace, source=None, version=None, local=True, config=None):
        self.uri = uri
        self.version = version
        self.path = uris.to_fs_path(uri)
        self.filename = os.path.basename(self.path)
        self.relpath = os.path.relpath(self.path, workspace._root_path)
        self.relname = os.path.splitext(self.relpath)

        self._config = config
        self._workspace = workspace
        self._local = local
        self._source = source

        self._pagelinks = None #cache

    def __str__(self):
        return str(self.uri)

    @property
    def pagelinks(self):
        if self._pagelinks is not None:
            return self._pagelinks
        return self.scan_links()

    @property
    def lines(self):
        return self.source.splitlines(True)

    @property
    def source(self):
        if self._source is None:
            with io.open(self.path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._source

    def update_config(self, config):
        self._config = config

    def scan_links(self, ):
        self._pagelinks = []
        for il, l in enumerate(self.source.splitlines()):
            for itr in RE_PAGELINK.finditer(l):
                self._pagelinks.append(PageLink(itr.group(1), il, itr.start(1), itr.end(1)))
        return self._pagelinks

    def replace_links(self, oldname, newname):
        #TODO
        return

    def apply_change(self, change):
        """Apply a change to the document."""
        text = change['text']
        change_range = change.get('range')

        if not change_range:
            # The whole file has changed
            self._source = text
            return

        start_line = change_range['start']['line']
        start_col = change_range['start']['character']
        end_line = change_range['end']['line']
        end_col = change_range['end']['character']

        # Check for an edit occuring at the very end of the file
        if start_line == len(self.lines):
            self._source = self.source + text
            return

        new = io.StringIO()

        # Iterate over the existing document until we hit the edit range,
        # at which point we write the new text, then loop until we hit
        # the end of the range and continue writing.
        for i, line in enumerate(self.lines):
            if i < start_line:
                new.write(line)
                continue

            if i > end_line:
                new.write(line)
                continue

            if i == start_line:
                new.write(line[:start_col])
                new.write(text)

            if i == end_line:
                new.write(line[end_col:])

        self._source = new.getvalue()

    def offset_at_position(self, position):
        """Return the byte-offset pointed at by the given position."""
        return position['character'] + len(''.join(self.lines[:position['line']]))

    def word_at_position(self, position):
        """Get the word under the cursor returning the start and end positions."""
        if position['line'] >= len(self.lines):
            return ''

        line = self.lines[position['line']]
        i = position['character']
        # Split word in two
        start = line[:i]
        end = line[i:]

        # Take end of start and start of end to find word
        # These are guaranteed to match, even if they match the empty string
        m_start = RE_START_WORD.findall(start)
        m_end = RE_END_WORD.findall(end)

        return m_start[0] + m_end[-1]

    def pagelink_at_position(self, position):
        if position['line'] >= len(self.lines):
            return ''

        line = self.lines[position['line']]
        i = position['character']
        start = line.rfind('[[', 0, i)
        end = line.find(']]', i)

        page = s[line.rfind('[[', 0, i)+2:line.find(']]', i)].strip().rstrip()
        if '[[' in page or ']]' in page:
            return ''
        return page

