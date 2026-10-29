"""Public-shape compatibility objects for the local training environment."""
from __future__ import annotations

from .clients import ClientModel, HfResponse


class HedgeFund:
    """Class-level quote responder matching ``HedgeFund as hf; hf.show(...)``."""

    _model = ClientModel(seed=2026, buy_probability=0.5,
                         base_acceptance=0.96, sensitivity=8.0)

    @classmethod
    def reset(cls, seed: int = 2026) -> None:
        cls._model = ClientModel(seed=seed, buy_probability=0.5,
                                 base_acceptance=0.96, sensitivity=8.0)

    @classmethod
    def show(cls, trade) -> HfResponse:
        return cls._model.show(trade)
