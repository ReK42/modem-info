"""Driver for the Hitron CODA-45."""

from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from time import time, time_ns
from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel

from modem_info.drivers.hitron.coda45 import export, models
from modem_info.drivers.utils import HTTPModemDriver

if TYPE_CHECKING:
    from httpx import Response

U = TypeVar("U", bound=BaseModel)


@export
class HitronCoda45(HTTPModemDriver):
    """Driver for the Hitron CODA-45."""

    _base = "/data"

    @staticmethod
    def _params(params: dict[str, str] | None = None) -> dict[str, str]:
        """Build the HTTP request parameters."""
        if params is None:
            params = {}
        return params | {"_": f"{time():.3f}".replace(".", "")}

    def _get(self, path: str, model: type[U]) -> U:
        """Request info from the modem and validate it against a data model."""
        ts = time_ns()
        response: Response = self._client.get(path, params=self._params())
        return model(timestamp=ts, data=response.json())

    @property
    def system_info(self) -> models.SystemInfo:
        """Get basic system information from the modem."""
        return self._get(self._base + "/getSysInfo.asp", models.SystemInfo)

    @property
    def link_status(self) -> models.LinkStatus:
        """Get link status from the modem."""
        return self._get(self._base + "/getLinkStatus.asp", models.LinkStatus)

    @property
    def docsis_provisioning(self) -> models.DOCSISProvisioning:
        """Get DOCSIS provisioning status from the modem."""
        return self._get(self._base + "/getCMInit.asp", models.DOCSISProvisioning)

    @property
    def docsis_overview(self) -> models.DOCSISOverview:
        """Get DOCSIS overview information from the modem."""
        return self._get(self._base + "/getCmDocsisWan.asp", models.DOCSISOverview)

    @property
    def docsis_downstream(self) -> models.DOCSISDownstream:
        """Get DOCSIS downstream information from the modem."""
        return self._get(self._base + "/dsinfo.asp", models.DOCSISDownstream)

    @property
    def docsis_downstream_flattened(self) -> models.DOCSISDownstreamFlattened:
        """Get flattened DOCSIS downstream information from the modem."""
        data = self.docsis_downstream
        signal_strengths = [channel.signal_strength for channel in data.data if channel.signal_strength is not None]
        snrs = [channel.snr for channel in data.data if channel.snr is not None]
        octets = [channel.octets for channel in data.data if channel.octets is not None]
        correcteds = [channel.corrected for channel in data.data if channel.corrected is not None]
        uncorrecteds = [channel.uncorrected for channel in data.data if channel.uncorrected is not None]

        return models.DOCSISDownstreamFlattened(
            timestamp=data.timestamp,
            num_channels=len(signal_strengths),
            signal_strength_min=min(signal_strengths),
            signal_strength_mean=mean(signal_strengths),
            signal_strength_max=max(signal_strengths),
            snr_min=min(snrs),
            snr_mean=mean(snrs),
            snr_max=max(snrs),
            octets_total=sum(octets),
            corrected_total=sum(correcteds),
            corrected_min=min(correcteds),
            corrected_mean=int(mean(correcteds)),
            corrected_max=max(correcteds),
            uncorrected_total=sum(uncorrecteds),
            uncorrected_min=min(uncorrecteds),
            uncorrected_mean=int(mean(uncorrecteds)),
            uncorrected_max=max(uncorrecteds),
        )

    @property
    def docsis_downstream_ofdm(self) -> models.DOCSISDownstreamOFDM:
        """Get DOCSIS downstream OFDM information from the modem."""
        return self._get(self._base + "/dsofdminfo.asp", models.DOCSISDownstreamOFDM)

    @property
    def docsis_downstream_ofdm_flattened(self) -> models.DOCSISDownstreamOFDMFlattened | None:
        """Get flattened DOCSIS downstream OFDM information from the modem."""
        data = self.docsis_downstream_ofdm
        num_channels = len([channel for channel in data.data if channel.plc_lock])
        if not num_channels:
            return None
        plc_powers = [channel.plc_power for channel in data.data if channel.plc_lock and channel.plc_power is not None]
        snrs = [channel.snr for channel in data.data if channel.plc_lock and channel.snr is not None]
        octets = [channel.octets for channel in data.data if channel.plc_lock and channel.octets is not None]
        correcteds = [channel.corrected for channel in data.data if channel.plc_lock and channel.corrected is not None]
        uncorrecteds = [
            channel.uncorrected for channel in data.data if channel.plc_lock and channel.uncorrected is not None
        ]

        return models.DOCSISDownstreamOFDMFlattened(
            timestamp=data.timestamp,
            num_channels=num_channels,
            plc_power_min=min(plc_powers),
            plc_power_mean=mean(plc_powers),
            plc_power_max=max(plc_powers),
            snr_min=min(snrs),
            snr_mean=mean(snrs),
            snr_max=max(snrs),
            octets_total=sum(octets),
            corrected_total=sum(correcteds),
            corrected_min=min(correcteds),
            corrected_mean=int(mean(correcteds)),
            corrected_max=max(correcteds),
            uncorrected_total=sum(uncorrecteds),
            uncorrected_min=min(uncorrecteds),
            uncorrected_mean=int(mean(uncorrecteds)),
            uncorrected_max=max(uncorrecteds),
        )

    @property
    def docsis_upstream(self) -> models.DOCSISUpstream:
        """Get DOCSIS upstream information from the modem."""
        return self._get(self._base + "/usinfo.asp", models.DOCSISUpstream)

    @property
    def docsis_upstream_flattened(self) -> models.DOCSISUpstreamFlattened:
        """Get flattened DOCSIS upstream information from the modem."""
        data = self.docsis_upstream
        signal_strengths = [channel.signal_strength for channel in data.data if channel.signal_strength is not None]

        return models.DOCSISUpstreamFlattened(
            timestamp=data.timestamp,
            num_channels=len(signal_strengths),
            signal_strength_min=min(signal_strengths),
            signal_strength_mean=mean(signal_strengths),
            signal_strength_max=max(signal_strengths),
        )

    @property
    def docsis_upstream_ofdm(self) -> models.DOCSISUpstreamOFDM:
        """Get DOCSIS upstream OFDM information from the modem."""
        return self._get(self._base + "/usofdminfo.asp", models.DOCSISUpstreamOFDM)

    @property
    def docsis_upstream_ofdm_flattened(self) -> models.DOCSISUpstreamOFDMFlattened | None:
        """Get flattened DOCSIS upstream OFDM information from the modem."""
        data = self.docsis_upstream_ofdm
        num_channels = len([channel for channel in data.data if channel.state])
        if not num_channels:
            return None
        line_digital_attenuations = [
            channel.line_digital_attenuation
            for channel in data.data
            if channel.state and channel.line_digital_attenuation is not None
        ]
        digital_attenuations = [
            channel.digital_attenuation
            for channel in data.data
            if channel.state and channel.digital_attenuation is not None
        ]
        report_powers = [
            channel.report_power for channel in data.data if channel.state and channel.report_power is not None
        ]
        report_power1_6s = [
            channel.report_power1_6 for channel in data.data if channel.state and channel.report_power1_6 is not None
        ]

        return models.DOCSISUpstreamOFDMFlattened(
            timestamp=data.timestamp,
            num_channels=num_channels,
            line_digital_attenuation_min=min(line_digital_attenuations),
            line_digital_attenuation_mean=mean(line_digital_attenuations),
            line_digital_attenuation_max=max(line_digital_attenuations),
            digital_attenuation_min=min(digital_attenuations),
            digital_attenuation_mean=mean(digital_attenuations),
            digital_attenuation_max=max(digital_attenuations),
            report_power_min=min(report_powers),
            report_power_mean=mean(report_powers),
            report_power_max=max(report_powers),
            report_power1_6_min=min(report_power1_6s),
            report_power1_6_mean=mean(report_power1_6s),
            report_power1_6_max=max(report_power1_6s),
        )

    @property
    def docsis_events(self) -> None:
        """Get DOCSIS events from the modem."""
        raise NotImplementedError  # TODO: Implement when we have example data

    @property
    def docsis_statistics(self) -> models.DOCSISStatistics:
        """Get DOCSIS statistics from the modem."""
        return models.DOCSISStatistics(
            timestamp=time_ns(),
            docsis_provisioning=self.docsis_provisioning.data[0],
            docsis_overview=self.docsis_overview.data[0],
            docsis_downstream=self.docsis_downstream.data,
            docsis_downstream_ofdm=self.docsis_downstream_ofdm.data,
            docsis_upstream=self.docsis_upstream.data,
            docsis_upstream_ofdm=self.docsis_upstream_ofdm.data,
        )

    @property
    def docsis_statistics_flattened(self) -> dict[str, Any]:
        """Get flattened DOCSIS statistics from the modem."""
        downstream = self.docsis_downstream_flattened
        downstream_ofdm = self.docsis_downstream_ofdm_flattened
        upstream = self.docsis_upstream_flattened

        if downstream_ofdm is not None:
            plc_power_mean = downstream_ofdm.plc_power_mean
            octets_total = downstream_ofdm.octets_total
            corrected_total = downstream_ofdm.corrected_total
            uncorrected_total = downstream_ofdm.uncorrected_total
        else:
            plc_power_mean = 0.0
            octets_total = 0
            corrected_total = 0
            uncorrected_total = 0

        return {
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "down_signal_min": f"{downstream.signal_strength_min:.3f}",
            "down_signal_mean": f"{downstream.signal_strength_mean:.3f}",
            "down_signal_max": f"{downstream.signal_strength_max:.3f}",
            "down_snr_min": f"{downstream.snr_min:.3f}",
            "down_snr_mean": f"{downstream.snr_mean:.3f}",
            "down_snr_max": f"{downstream.snr_max:.3f}",
            "down_plc_power": f"{plc_power_mean:.3f}",
            "down_octets_total": octets_total,
            "down_correcteds_total": corrected_total,
            "down_uncorrectables_total": uncorrected_total,
            "up_signal_mean": f"{upstream.signal_strength_mean:.3f}",
        }
