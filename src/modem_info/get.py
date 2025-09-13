"""Get detailed information and statistics from your modem."""

from __future__ import annotations

from csv import DictWriter
from ipaddress import IPv4Address, IPv6Address, ip_address
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Any

import click

from modem_info.__main__ import main
from modem_info.drivers.hitron.coda45 import HitronCoda45

if TYPE_CHECKING:
    from rich.console import Console

    from modem_info.drivers import HTTPDOCSISModemDriverProtocol


CSV_HEADERS = (
    "timestamp",
    "down_signal_min",
    "down_signal_max",
    "down_signal_mean",
    "down_signal_med",
    "down_snr_min",
    "down_snr_max",
    "down_snr_mean",
    "down_snr_med",
    "down_plc_power",
    "down_octets",
    "down_correcteds",
    "down_uncorrectables",
    "up_signal",
)


class IPAddressParamType(click.ParamType):
    """Represents a valid IPv4 or IPv6 address."""

    name = "ip address"

    def convert(
        self,
        value: Any,  # noqa: ANN401
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> IPv4Address | IPv6Address:
        """Convert the value to an IPv4/IPv6Address object."""
        try:
            return ip_address(value)
        except (TypeError, ValueError):
            self.fail(f"{value!r} is not a valid IP address", param, ctx)


def write_csv_docsis(modem: HitronCoda45, path: Path) -> None:
    """Write flattened statistics from your DOCSIS modem to CSV."""
    data = modem.docsis_statistics_flattened
    with Path(path / f"{modem.address}.csv").open("a") as f:
        writer = DictWriter(f, fieldnames=data.keys(), lineterminator="\n")
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(data)
        f.flush()


def write_jsonl_docsis(modem: HTTPDOCSISModemDriverProtocol, path: Path) -> None:
    """Write detailed statistics from your DOCSIS modem to JSONL."""
    models = {
        Path(path / f"{modem.address}_system_info.jsonl"): modem.system_info,
        Path(path / f"{modem.address}_link_status.jsonl"): modem.link_status,
        Path(path / f"{modem.address}_docsis_statistics.jsonl"): modem.docsis_statistics,
    }
    for file, model in models.items():
        with file.open("a") as f:
            f.write(model.model_dump_json() + "\n")
            f.flush()


@main.command()  # type: ignore[has-type]
@click.argument("address", type=IPAddressParamType())
@click.option(
    "-p",
    "--path",
    type=click.Path(exists=True, file_okay=False, writable=True, path_type=Path),
    default=Path("data"),
    show_default=True,
    help="Path to output files.",
)
@click.option(
    "-i",
    "--interval",
    type=click.FloatRange(min=5.0),
    default=60.0,
    show_default=True,
    help="Interval to record data on.",
)
@click.option(
    "-c",
    "--csv",
    is_flag=True,
    default=False,
    show_default=True,
    help="Write DOCSIS statistics to CSV.",
)
@click.option(
    "-j",
    "--json",
    is_flag=True,
    default=False,
    show_default=True,
    help="Write DOCSIS statistics to JSONL.",
)
@click.help_option("-h", "--help")
@click.pass_context
def get(  # noqa: PLR0913
    ctx: click.Context,
    address: IPv4Address | IPv6Address,
    path: Path,
    interval: float = 60.0,
    csv: bool = False,  # noqa: FBT001 FBT002
    json: bool = False,  # noqa: FBT001 FBT002
) -> int:
    """Get detailed information and statistics from a modem at ADDRESS."""
    stdout: Console = ctx.obj["stdout"]
    stderr: Console = ctx.obj["stdout"]

    if True not in (csv, json):
        stderr.log("[red bold]ERROR:[/red bold] Must select at least one output format: --csv, --json")

    try:
        modem = HitronCoda45(address)
    except BaseException:  # noqa: BLE001
        stderr.print_exception()
        stderr.log(f"[red bold]ERROR:[/red bold] Unable to connect to modem at {address}")
        return 1

    if csv:
        stdout.log(f"Beginning CSV output to {path}")
    if json:
        stdout.log(f"Beginning JSONL output to {path}")

    try:
        with stdout.status("Writing to file(s)..."):
            while True:
                if csv:
                    write_csv_docsis(modem, path)
                if json:
                    write_jsonl_docsis(modem, path)
                sleep(interval)
    except KeyboardInterrupt:
        stderr.log("Aborted by user")
    except BaseException:  # noqa: BLE001
        stderr.print_exception()
        stderr.log("[red bold]ERROR:[/red bold] Unknown exception")
        return 1

    return 0
