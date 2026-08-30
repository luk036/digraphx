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

# Public API re-exports (matching the README quick-start examples)
from .csr_digraph import CSRDiGraph  # noqa: E402
from .mcf import cycle_canceling_mcf  # noqa: E402
from .min_cycle_ratio import MinCycleRatioSolver  # noqa: E402
from .min_parametric_q import MinParametricSolver  # noqa: E402
from .neg_cycle import NegCycleFinder  # noqa: E402
from .neg_cycle_q import NegCycleFinderQ  # noqa: E402
from .parametric import MaxParametricSolver  # noqa: E402
from .tiny_digraph import DiGraphAdapter, TinyDiGraph  # noqa: E402

__all__ = [
    "CSRDiGraph",
    "DiGraphAdapter",
    "MaxParametricSolver",
    "MinCycleRatioSolver",
    "MinParametricSolver",
    "NegCycleFinder",
    "NegCycleFinderQ",
    "TinyDiGraph",
    "cycle_canceling_mcf",
]
