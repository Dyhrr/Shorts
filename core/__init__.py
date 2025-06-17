"""Public API for the :mod:`core` package.

Importing :mod:`shorts` pulls in heavy dependencies (``faster-whisper`` in
particular).  Tests in lightweight environments may not have these optional
packages installed, so ``generate_short`` is loaded lazily to avoid import
errors when the function is unused.  ``load_config`` and ``save_config`` are
cheap to import and exposed directly.
"""

from .utils import load_config, save_config
from .version import __version__


def generate_short(*args, **kwargs):
    """Import :func:`~core.shorts.generate_short` on demand and execute it."""

    from .shorts import generate_short as _generate_short

    return _generate_short(*args, **kwargs)

__all__ = ["generate_short", "load_config", "save_config", "__version__"]
