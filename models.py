"""
Python OOP data models — direct port of the MATLAB class hierarchy.

Statistics (base) → CovidCountryData / CovidStateData
"""

import json
import numpy as np
from typing import List, Optional


class Statistics:
    """Base class holding time-series COVID data (port of Statistics.m)."""

    def __init__(self, dates: List[str], cumulative_cases: List[int], cumulative_deaths: List[int]):
        self.dates = dates
        self.cumulative_cases = np.array(cumulative_cases, dtype=np.float64)
        self.cumulative_deaths = np.array(cumulative_deaths, dtype=np.float64)

        # Daily = diff of cumulative, with first element = cumulative[0]
        self.daily_cases = np.concatenate(([self.cumulative_cases[0]], np.diff(self.cumulative_cases)))
        self.daily_cases[self.daily_cases < 0] = 0

        self.daily_deaths = np.concatenate(([self.cumulative_deaths[0]], np.diff(self.cumulative_deaths)))
        self.daily_deaths[self.daily_deaths < 0] = 0


class CovidStateData(Statistics):
    """Data for a single state/region within a country (port of CovidStateData.m)."""

    def __init__(self, name: str, dates: List[str], cumulative_cases: List[int], cumulative_deaths: List[int]):
        super().__init__(dates, cumulative_cases, cumulative_deaths)
        self.name = name


class CovidCountryData(Statistics):
    """Data for a country, possibly containing states (port of CovidCountryData.m)."""

    def __init__(self, name: str, dates: List[str],
                 cumulative_cases: List[int], cumulative_deaths: List[int],
                 states_data: Optional[List[dict]] = None):
        super().__init__(dates, cumulative_cases, cumulative_deaths)
        self.name = name
        self.list_of_states: List[CovidStateData] = []
        self.list_of_state_names: List[str] = []

        if states_data:
            for s in states_data:
                state = CovidStateData(
                    name=s["name"],
                    dates=dates,
                    cumulative_cases=s["cumulative_cases"],
                    cumulative_deaths=s["cumulative_deaths"],
                )
                self.list_of_states.append(state)
                self.list_of_state_names.append(s["name"])

        self.number_of_states = len(self.list_of_states)


class DataLoader:
    """Loads covid_data.json and builds the object hierarchy."""

    def __init__(self, json_path: str = "covid_data.json"):
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self.dates = raw["dates"]
        self.countries: List[CovidCountryData] = []
        self.country_names: List[str] = []

        for c in raw["countries"]:
            country = CovidCountryData(
                name=c["name"],
                dates=self.dates,
                cumulative_cases=c["cumulative_cases"],
                cumulative_deaths=c["cumulative_deaths"],
                states_data=c.get("states", []),
            )
            self.countries.append(country)
            self.country_names.append(c["name"])

    def get_country(self, name: str) -> Optional[CovidCountryData]:
        for c in self.countries:
            if c.name == name:
                return c
        return None

    def search_countries(self, query: str) -> List[str]:
        q = query.lower()
        return [n for n in self.country_names if q in n.lower()]
