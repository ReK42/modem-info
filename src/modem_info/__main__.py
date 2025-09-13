"""Collect and plot detailed information and statistics from your modem."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

import click
from rich.console import Console

from modem_info import __copyright__, __name__, __version__  # noqa: A004

if TYPE_CHECKING:
    from collections.abc import Callable


_version: str = f"{__name__} v{__version__} -- {__copyright__}"


@click.group()
@click.help_option("-h", "--help")
@click.version_option(__version__, "-v", "--version", message=_version)
@click.pass_context
def main(ctx: click.Context) -> None:
    """
    Collect and plot detailed information and statistics from your modem.

    Run modem-info COMMAND --help for details on each command.
    """
    ctx.ensure_object(dict)

    log_time_format: str = "[%Y-%m-%dT%H:%M:%S.%f%z]"
    get_datetime: Callable = lambda: datetime.now(timezone.utc).astimezone()  # noqa: E731
    ctx.obj["stdout"] = Console(
        log_time_format=log_time_format,
        get_datetime=get_datetime,
    )
    ctx.obj["stderr"] = Console(
        log_time_format=log_time_format,
        get_datetime=get_datetime,
        stderr=True,
    )


if __name__ == "__main__":
    main(obj={})
