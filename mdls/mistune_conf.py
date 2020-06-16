# Copyright 2017 Palantir Technologies, Inc.
import logging
import os
from mdls._utils import find_parents
from .source import ConfigSource

log = logging.getLogger(__name__)

CONFIG_KEY = 'mistune'
PROJECT_CONFIGS = []

OPTIONS = [
    ('mathjax', 'plugins.mistune.mathjax.enabled', bool),
    #('wikilink', 'plugins.pycodestyle.exclude', bool),
]


class MistuneConfig(ConfigSource):
    """Parse Mistune configurations."""

    def user_config(self):
        config_file = self._user_config_file()
        config = self.read_config_from_files([config_file])
        return self.parse_config(config, CONFIG_KEY, OPTIONS)

    def _user_config_file(self):
        if self.is_windows:
            return os.path.expanduser('~\\.markdown_mistune')
        return os.path.join(self.xdg_home, '.markdown_mistune')

    def project_config(self, document_path):
        files = find_parents(self.root_path, document_path, PROJECT_CONFIGS)
        config = self.read_config_from_files(files)
        return self.parse_config(config, CONFIG_KEY, OPTIONS)
