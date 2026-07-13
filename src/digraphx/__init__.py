import sys

if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from digraphx.spare_tsv import (  # noqa: F401
    formGraph,
    setup_network_flow,
    showPaths,
    solve_network_flow,
    vdc,
    vdcorput,
)
