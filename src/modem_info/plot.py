"""Plot statistics from your modem."""

from pathlib import Path
from typing import TYPE_CHECKING

import click
from pandas import read_csv
from plotly.graph_objects import Figure, Scatter

from modem_info.__main__ import main

if TYPE_CHECKING:
    from pandas import DataFrame
    from rich.console import Console


class COLORS:
    """Plotly colour theme."""

    NONE: str = "rgba(255, 255, 255, 0)"
    BLACK: str = "rgb(0, 0, 0)"
    WHITE: str = "rgb(255, 255, 255)"
    FORESTGREEN: str = "rgb(34, 139, 34)"
    FORESTGREEN_TRANS: str = "rgba(34, 139, 34, 0.2)"
    ROYALBLUE: str = "rgb(65, 105, 225)"
    ROYALBLUE_TRANS: str = "rgba(65, 105, 225, 0.2)"
    DARKORCHID: str = "rgb(153, 50, 204)"
    DARKORCHID_TRANS: str = "rgba(153, 50, 204, 0.2)"
    CRIMSON: str = "rgb(220, 20, 60)"
    CRIMSON_TRANS: str = "rgba(220, 20, 60, 0.2)"
    DARKORANGE: str = "rgb(255, 140, 0)"
    DARKORANGE_TRANS: str = "rgba(255, 140, 0, 0.2)"


@main.command()  # type: ignore[has-type]
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.help_option("-h", "--help")
@click.pass_context
def plot(ctx: click.Context, file: Path) -> None:
    """Plot statistics from your modem."""
    stdout: Console = ctx.obj["stdout"]  # noqa: F841
    stderr: Console = ctx.obj["stdout"]  # noqa: F841

    with file.open() as f:
        df: DataFrame = read_csv(f)

    data = [
        # Downstream Signal Min/Max/Avg (dBmV)
        Scatter(
            x=df["timestamp"],
            y=df["down_signal_max"],
            line_color=COLORS.FORESTGREEN,
            showlegend=False,
            hovertemplate=None,
            name="↓ Signal Max. (dBmV)",
            legendgroup="dsignal",
        ),
        Scatter(
            x=df["timestamp"],
            y=df["down_signal_min"],
            fill="tonexty",
            fillcolor=COLORS.FORESTGREEN_TRANS,
            line_color=COLORS.FORESTGREEN,
            showlegend=False,
            hovertemplate=None,
            name="↓ Signal Min. (dBmV)",
            legendgroup="dsignal",
        ),
        Scatter(
            x=df["timestamp"],
            y=df["down_signal_mean"],
            line_color=COLORS.FORESTGREEN,
            hovertemplate=None,
            name="↓ Signal Avg. (dBmV)",
            legendgroup="dsignal",
        ),
        # Downstream SNR Min/Max/Avg (dB)
        Scatter(
            x=df["timestamp"],
            y=df["down_snr_max"],
            line_color=COLORS.ROYALBLUE,
            showlegend=False,
            hovertemplate=None,
            name="↓ SNR Max. (dB)",
            legendgroup="dsnr",
        ),
        Scatter(
            x=df["timestamp"],
            y=df["down_snr_min"],
            fill="tonexty",
            fillcolor=COLORS.ROYALBLUE_TRANS,
            line_color=COLORS.ROYALBLUE,
            showlegend=False,
            hovertemplate=None,
            name="↓ SNR Min. (dB)",
            legendgroup="dsnr",
        ),
        Scatter(
            x=df["timestamp"],
            y=df["down_snr_mean"],
            line_color=COLORS.ROYALBLUE,
            hovertemplate=None,
            name="↓ SNR Avg. (dB)",
            legendgroup="dsnr",
        ),
        # Upstream Signal Min/Max/Avg (dB)
        Scatter(
            x=df["timestamp"],
            y=df["up_signal"],
            line_color=COLORS.DARKORCHID,
            hovertemplate=None,
            name="↑ Signal (dBmV)",
        ),
        # Downstream Octets
        Scatter(
            x=df["timestamp"],
            y=df["down_uncorrectables"],
            yaxis="y2",
            stackgroup="one",
            line_color=COLORS.CRIMSON,
            hovertemplate=None,
            name="↓ Uncorrectable",
            legend="legend2",
        ),
        Scatter(
            x=df["timestamp"],
            y=df["down_correcteds"],
            yaxis="y2",
            stackgroup="one",
            line_color=COLORS.DARKORANGE,
            hovertemplate=None,
            name="↓ Corrected",
            legend="legend2",
        ),
        Scatter(
            x=df["timestamp"],
            y=df["down_octets"],
            yaxis="y2",
            line_color=COLORS.ROYALBLUE,
            hovertemplate=None,
            stackgroup="one",
            name="↓ Total",
            legend="legend2",
        ),
        # Downstream Octets Δ
        Scatter(
            x=df["timestamp"],
            y=df["down_uncorrectables"].diff().shift(-1),
            yaxis="y3",
            stackgroup="one",
            line_color=COLORS.CRIMSON,
            hovertemplate=None,
            name="↓ Uncorrectable Δ",
            legend="legend3",
        ),
        # Scatter(
        #     x=df["timestamp"],
        #     y=df["down_correcteds"].diff().shift(-1),
        #     yaxis="y3",
        #     stackgroup="one",
        #     line_color=COLORS.DARKORANGE,
        #     hovertemplate=None,
        #     name="↓ Corrected Δ",
        #     legend="legend3",
        # ),
        Scatter(
            x=df["timestamp"],
            y=df["down_octets"].diff().shift(-1),
            yaxis="y3",
            stackgroup="one",
            line_color=COLORS.ROYALBLUE,
            hovertemplate=None,
            name="↓ Total Δ",
            legend="legend3",
        ),
    ]

    figure = Figure(
        data=data,
        layout=dict(
            title="Modem Statistics",
            hovermode="x",
            hoversubplots="axis",
            hoverlabel_namelength=30,
            showlegend=True,
            grid=dict(
                subplots=[["xy"], ["xy2"], ["xy3"]],
                xaxes=["x"],
                yaxes=["y", "y2", "y3"],
                ygap=0.05,
            ),
            yaxis=dict(
                title_text="dB",
                range=[0.0, 50.0],
            ),
            yaxis2=dict(
                title_text="Octets Total",
            ),
            yaxis3=dict(
                title_text="Octets Δ",
                range=[0, int(1e5)],
            ),
            legend=dict(
                title="Signal Levels",
            ),
            legend2=dict(
                title="Downstream Octets Total",
                y=0.65,
                yanchor="top",
            ),
            legend3=dict(
                title="Downstream Octets Δ",
                y=0.3,
                yanchor="top",
            ),
        ),
    )
    figure.show()
