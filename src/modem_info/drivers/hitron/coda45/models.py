"""Data models for the Hitron CODA-45 modem driver."""

from __future__ import annotations

import re
from datetime import timedelta
from ipaddress import IPv4Address, IPv6Address, ip_address

from pydantic import BaseModel, Field, field_validator
from pydantic_extra_types.mac_address import MacAddress  # noqa: TC002

from modem_info.drivers.hitron.coda45 import export


def normalize_str_to_bool(v: str) -> bool:
    """Normalize a string into a boolean."""
    return v.lower() in (
        "1",
        "true",
        "yes",
        "y",
        "on",
        "success",
        "permitted",
        "enabled",
        "enable",
    )


def normalize_str_to_str_or_none(v: str) -> str | None:
    """Normalize a string into a string or None."""
    if v.strip().lower() in ("", "na", "n/a"):
        return None
    return v


def normalize_str_to_int_or_zero(v: str) -> int:
    """Normalize a string into an integer or zero."""
    try:
        return int(v)
    except ValueError:
        return 0


def normalize_str_to_int_or_none(v: str) -> int | None:
    """Normalize a string into an integer or None."""
    try:
        return int(v)
    except ValueError:
        return None


def normalize_str_to_float_or_none(v: str) -> float | None:
    """Normalize a string into a float or None."""
    try:
        return float(v)
    except ValueError:
        return None


@export
class SystemInfoData(BaseModel):
    """Data element from /data/getSysInfo.asp."""

    hw_version: str = Field(validation_alias="hwVersion")
    sw_version: str = Field(validation_alias="swVersion")
    serial: str = Field(validation_alias="serialNumber")
    rf_mac: MacAddress = Field(validation_alias="rfMac")
    system_uptime: str = Field(validation_alias="systemUptime")
    system_time: str = Field(validation_alias="systemTime")


@export
class SystemInfo(BaseModel):
    """Data from /data/getSysInfo.asp."""

    timestamp: int
    data: list[SystemInfoData]


@export
class DOCSISProvisioningData(BaseModel):
    """Data element from /data/getCMInit.asp."""

    hw_init: bool = Field(validation_alias="hwInit")
    find_downstream: bool = Field(validation_alias="findDownstream")
    ranging: bool
    dhcp: bool
    time_of_day: bool = Field(validation_alias="timeOfday")
    download_config: bool = Field(validation_alias="downloadCfg")
    registration: bool
    eae_status: bool = Field(validation_alias="eaeStatus")
    bpi_status: str = Field(validation_alias="bpiStatus")
    network_access: bool = Field(validation_alias="networkAccess")
    traffic_status: bool = Field(validation_alias="trafficStatus")

    # Validators
    _normalize_str_to_bool = field_validator(
        "hw_init",
        "find_downstream",
        "ranging",
        "dhcp",
        "time_of_day",
        "download_config",
        "registration",
        "eae_status",
        "network_access",
        "traffic_status",
        mode="before",
    )(normalize_str_to_bool)


@export
class DOCSISProvisioning(BaseModel):
    """Data from /data/getCMInit.asp."""

    timestamp: int
    data: list[DOCSISProvisioningData]


@export
class LinkStatusData(BaseModel):
    """Data element from /data/getLinkStatus.asp."""

    status: bool = Field(validation_alias="LinkStatus")
    speed: str | None = Field(validation_alias="LinkSpeed")
    duplex: str | None = Field(validation_alias="LinkDuplex")

    # Validators
    @field_validator("status", mode="before")
    @classmethod
    def _normalize_link_status(cls, v: str) -> bool:
        return v.lower() == "up"

    @field_validator("speed", "duplex", mode="before")
    @classmethod
    def _normalize_str_or_none(cls, v: str) -> str | None:
        return None if v == "-" else v


@export
class LinkStatus(BaseModel):
    """Data from /data/getLinkStatus.asp."""

    timestamp: int
    data: list[LinkStatusData]


@export
class DOCSISOverviewData(BaseModel):
    """Data element from /data/getCmDocsisWan.asp."""

    config_name: str = Field(validation_alias="Configname")
    config_name_display: str = Field(validation_alias="ConfignameDisplay")
    network_access: bool = Field(validation_alias="NetworkAccess")
    ip_address: IPv4Address | IPv6Address | None = Field(validation_alias="CmIpAddress")
    netmask: IPv4Address | IPv6Address | None = Field(validation_alias="CmNetMask")
    gateway: IPv4Address | IPv6Address | None = Field(validation_alias="CmGateway")
    lease_duration: timedelta = Field(validation_alias="CmIpLeaseDuration")

    # Validators
    _normalize_str_to_bool = field_validator(
        "network_access",
        mode="before",
    )(normalize_str_to_bool)

    @field_validator("ip_address", "netmask", "gateway", mode="before")
    @classmethod
    def _normalize_ip_address(cls, v: str) -> IPv4Address | IPv6Address | None:
        try:
            return ip_address(v)
        except (TypeError, ValueError):
            return None

    @field_validator("lease_duration", mode="before")
    @classmethod
    def _normalize_lease_duration(cls, v: str) -> timedelta:
        re_lease_duration = re.compile(
            r"D: (?P<days>[0-9-]+) "
            r"H: (?P<hours>[0-9-]+) "
            r"M: (?P<minutes>[0-9-]+) "
            r"S: (?P<seconds>[0-9-]+)"
        )
        match = re_lease_duration.fullmatch(v)
        if not match:
            return timedelta()
        return timedelta(
            days=normalize_str_to_int_or_zero(match["days"]),
            hours=normalize_str_to_int_or_zero(match["hours"]),
            minutes=normalize_str_to_int_or_zero(match["minutes"]),
            seconds=normalize_str_to_int_or_zero(match["seconds"]),
        )


@export
class DOCSISOverview(BaseModel):
    """Data from /data/getCmDocsisWan.asp."""

    timestamp: int
    data: list[DOCSISOverviewData]


@export
class DOCSISDownstreamData(BaseModel):
    """Data element from /data/dsinfo.asp."""

    port_id: int = Field(validation_alias="portId")
    frequency: int | None
    modulation: int | None
    signal_strength: float | None = Field(validation_alias="signalStrength")
    snr: float | None
    octets: int | None = Field(validation_alias="dsoctets")
    corrected: int | None = Field(validation_alias="correcteds")
    uncorrected: int | None = Field(validation_alias="uncorrect")
    channel_id: int | None = Field(validation_alias="channelId")

    # Validators
    _normalize_str_to_int_or_none = field_validator(
        "frequency",
        "modulation",
        "octets",
        "corrected",
        "uncorrected",
        "channel_id",
        mode="before",
    )(normalize_str_to_int_or_none)
    _normalize_str_to_float_or_none = field_validator(
        "signal_strength",
        "snr",
        mode="before",
    )(normalize_str_to_float_or_none)

    @field_validator("octets", mode="before")
    @classmethod
    def _normalize_bigint(cls, v: str) -> int | None:
        if " " not in v:
            try:
                return int(v)
            except ValueError:
                return None
        parts = v.split(" ")
        result = int(float(parts.pop(0)))
        while len(parts) > 0:
            op, val = parts.pop(0), int(float(parts.pop(0)))
            if op == "+":
                result += val
            if op == "*":
                result *= val
        return result


@export
class DOCSISDownstream(BaseModel):
    """Data from /data/dsinfo.asp."""

    timestamp: int
    data: list[DOCSISDownstreamData]


@export
class DOCSISDownstreamFlattened(BaseModel):
    """Flattened data from /data/dsinfo.asp."""

    timestamp: int
    num_channels: int
    signal_strength_min: float
    signal_strength_mean: float
    signal_strength_max: float
    snr_min: float
    snr_mean: float
    snr_max: float
    octets_total: int
    corrected_total: int
    corrected_min: int
    corrected_mean: int
    corrected_max: int
    uncorrected_total: int
    uncorrected_min: int
    uncorrected_mean: int
    uncorrected_max: int


@export
class DOCSISDownstreamOFDMData(BaseModel):
    """Data element from /data/dsofdminfo.asp."""

    receiver: int = Field(validation_alias="receive")
    fft_type: str | None = Field(validation_alias="ffttype")
    subcarrier_0_frequency: int | None = Field(validation_alias="Subcarr0freqFreq")
    plc_lock: bool = Field(validation_alias="plclock")
    ncp_lock: bool = Field(validation_alias="ncplock")
    mdc1_lock: bool = Field(validation_alias="mdc1lock")
    plc_power: float | None = Field(validation_alias="plcpower")
    snr: float | None = Field(validation_alias="SNR")
    octets: int | None = Field(validation_alias="dsoctets")
    corrected: int | None = Field(validation_alias="correcteds")
    uncorrected: int | None = Field(validation_alias="uncorrect")

    # Validators
    _normalize_str_to_str_or_none = field_validator(
        "fft_type",
        mode="before",
    )(normalize_str_to_str_or_none)
    _normalize_str_to_float_or_none = field_validator(
        "subcarrier_0_frequency",
        "plc_power",
        "snr",
        mode="before",
    )(normalize_str_to_float_or_none)
    _normalize_str_to_bool = field_validator(
        "plc_lock",
        "ncp_lock",
        "mdc1_lock",
        mode="before",
    )(normalize_str_to_bool)
    _normalize_str_to_int_or_none = field_validator(
        "octets",
        "corrected",
        "uncorrected",
        mode="before",
    )(normalize_str_to_int_or_none)


@export
class DOCSISDownstreamOFDM(BaseModel):
    """Data from /data/dsofdminfo.asp."""

    timestamp: int
    data: list[DOCSISDownstreamOFDMData]


@export
class DOCSISDownstreamOFDMFlattened(BaseModel):
    """Flattened data from /data/dsofdminfo.asp."""

    timestamp: int
    num_channels: int
    plc_power_min: float
    plc_power_mean: float
    plc_power_max: float
    snr_min: float
    snr_mean: float
    snr_max: float
    octets_total: int
    corrected_total: int
    corrected_min: int
    corrected_mean: int
    corrected_max: int
    uncorrected_total: int
    uncorrected_min: int
    uncorrected_mean: int
    uncorrected_max: int


@export
class DOCSISUpstreamData(BaseModel):
    """Data element from /data/usinfo.asp."""

    port_id: int = Field(validation_alias="portId")
    frequency: int | None
    bandwidth: int | None
    modulation: str | None = Field(validation_alias="modtype")
    docsis_mode: str | None = Field(validation_alias="scdmaMode")
    signal_strength: float | None = Field(validation_alias="signalStrength")
    channel_id: int | None = Field(validation_alias="channelId")

    # Validators
    _normalize_str_to_str_or_none = field_validator(
        "modulation",
        "docsis_mode",
        mode="before",
    )(normalize_str_to_str_or_none)
    _normalize_str_to_int_or_none = field_validator(
        "frequency",
        "bandwidth",
        "channel_id",
        mode="before",
    )(normalize_str_to_int_or_none)
    _normalize_str_to_float_or_none = field_validator(
        "signal_strength",
        mode="before",
    )(normalize_str_to_float_or_none)


@export
class DOCSISUpstream(BaseModel):
    """Data  from /data/usinfo.asp."""

    timestamp: int
    data: list[DOCSISUpstreamData]


@export
class DOCSISUpstreamFlattened(BaseModel):
    """Flattened data from /data/usinfo.asp."""

    timestamp: int
    num_channels: int
    signal_strength_min: float
    signal_strength_mean: float
    signal_strength_max: float


@export
class DOCSISUpstreamOFDMData(BaseModel):
    """Data element from /data/usofdminfo.asp."""

    channel_id: int = Field(validation_alias="uschindex")
    state: bool
    subcarrier_0_frequency: int | None = Field(validation_alias="frequency")
    line_digital_attenuation: float | None = Field(validation_alias="digAtten")
    digital_attenuation: float | None = Field(validation_alias="digAttenBo")
    bandwidth: float | None = Field(validation_alias="channelBw")
    report_power: float | None = Field(validation_alias="repPower")
    report_power1_6: float | None = Field(validation_alias="repPower1_6")
    fft_size: str | None = Field(validation_alias="fftVal")

    # Validators
    _normalize_str_to_bool = field_validator(
        "state",
        mode="before",
    )(normalize_str_to_bool)
    _normalize_str_to_str_or_none = field_validator(
        "fft_size",
        mode="before",
    )(normalize_str_to_str_or_none)
    _normalize_str_to_int_or_none = field_validator(
        "subcarrier_0_frequency",
        mode="before",
    )(normalize_str_to_int_or_none)
    _normalize_str_to_float_or_none = field_validator(
        "line_digital_attenuation",
        "digital_attenuation",
        "bandwidth",
        "report_power",
        "report_power1_6",
        mode="before",
    )(normalize_str_to_float_or_none)


@export
class DOCSISUpstreamOFDM(BaseModel):
    """Data from /data/usofdminfo.asp."""

    timestamp: int
    data: list[DOCSISUpstreamOFDMData]


@export
class DOCSISUpstreamOFDMFlattened(BaseModel):
    """Flattened data from /data/usofdminfo.asp."""

    timestamp: int
    num_channels: int
    line_digital_attenuation_min: float
    line_digital_attenuation_mean: float
    line_digital_attenuation_max: float
    digital_attenuation_min: float
    digital_attenuation_mean: float
    digital_attenuation_max: float
    report_power_min: float
    report_power_mean: float
    report_power_max: float
    report_power1_6_min: float
    report_power1_6_mean: float
    report_power1_6_max: float


@export
class DOCSISStatistics(BaseModel):
    """All data."""

    timestamp: int
    docsis_provisioning: DOCSISProvisioningData
    docsis_overview: DOCSISOverviewData
    docsis_downstream: list[DOCSISDownstreamData]
    docsis_downstream_ofdm: list[DOCSISDownstreamOFDMData]
    docsis_upstream: list[DOCSISUpstreamData]
    docsis_upstream_ofdm: list[DOCSISUpstreamOFDMData]
