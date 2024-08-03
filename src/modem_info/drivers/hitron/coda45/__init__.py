"""Driver for the Hitron CODA-45."""

from typing import Any

__all__ = []


def export(defn: Any) -> None:  # noqa: ANN401
    """Module-level export decorator."""
    globals()[defn.__name__] = defn
    __all__.append(defn.__name__)  # noqa: PYI056
    return defn


from modem_info.drivers.hitron.coda45 import models
from modem_info.drivers.hitron.coda45.driver import HitronCoda45
