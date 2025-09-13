"""Collect and plot detailed information and statistics from your modem."""

from typing import Any

__all__ = []


def export(defn: Any) -> None:  # noqa: ANN401
    """Module-level export decorator."""
    globals()[defn.__name__] = defn
    __all__.append(defn.__name__)  # noqa: PYI056
    return defn


__copyright__ = "Copyright (c) 2025 Ryan Kozak"
from modem_info import drivers
from modem_info._version import __version__
from modem_info.get import get
from modem_info.plot import plot
