"""Tests for the Hitron CODA-45 modem driver."""

import os.path
from importlib import import_module
from json import loads
from pathlib import Path
from time import time_ns

from pydantic import BaseModel

BASE: Path = Path(os.path.realpath(__file__)).parent / Path("test_data")
MODULE: str = "modem_info.drivers.hitron.coda45.models"
MODELS: dict[str, Path] = {
    "SystemInfo": Path(BASE / "getSysInfo.json"),
    "DOCSISProvisioning": Path(BASE / "getCMInit.json"),
    "LinkStatus": Path(BASE / "getLinkStatus.json"),
    "DOCSISOverview": Path(BASE / "getCmDocsisWan.json"),
    "DOCSISDownstream": Path(BASE / "dsinfo.json"),
    "DOCSISDownstreamOFDM": Path(BASE / "dsofdminfo.json"),
    "DOCSISUpstream": Path(BASE / "usinfo.json"),
    "DOCSISUpstreamOFDM": Path(BASE / "usofdminfo.json"),
}


def import_model(model: str) -> type[BaseModel]:
    """Dynamically import a data model."""
    return getattr(import_module(MODULE), model)


def run_model_tests() -> dict[str, BaseModel]:
    """Run data model validation tests."""
    ts: int = time_ns()
    results: dict[str, BaseModel] = {}
    for model, path in MODELS.items():
        data = None
        with path.open() as f:
            data = loads(f.read())
        results[model] = import_model(model)(timestamp=ts, data=data)
    return results


if __name__ == "__main__":
    from rich.pretty import pprint

    for result in run_model_tests().values():
        pprint(result, expand_all=True)
