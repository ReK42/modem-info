"""Drivers for the modem vendor Hitron."""

from typing import Any

__all__ = []


def export(defn: Any) -> None:  # noqa: ANN401
    """Module-level export decorator."""
    globals()[defn.__name__] = defn
    __all__.append(defn.__name__)  # noqa: PYI056
    return defn


from modem_info.drivers.hitron import coda45
