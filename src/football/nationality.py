from __future__ import annotations

from enum import Enum
from random import choice


class Nationality(Enum):
    UK = ("United Kingdom", "en_GB")

    def __init__(self, display_name: str, locale: str):
        self.display_name = display_name
        self.locale = locale

    @classmethod
    def random(cls) -> Nationality:
        return choice(list(cls))
