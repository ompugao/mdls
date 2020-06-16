import os
import sys
import pluggy
from ._version import get_versions

if sys.version_info[0] < 3:
    from future.standard_library import install_aliases
    install_aliases()

__version__ = get_versions()['version']
del get_versions

MDLS = 'mdls'

hookspec = pluggy.HookspecMarker(MDLS)
hookimpl = pluggy.HookimplMarker(MDLS)

IS_WIN = os.name == 'nt'
