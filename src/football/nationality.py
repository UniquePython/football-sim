from enum import Enum


class Nationality(Enum):
    UK = ("United Kingdom", "en_GB")

    def __init__(self, display_name: str, locale: str):
        self.display_name = display_name
        self.locale = locale
