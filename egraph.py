from __future__ import annotations

from typing import NamedTuple, FrozenSet


class EClass(NamedTuple):
    members: FrozenSet[EClass]
