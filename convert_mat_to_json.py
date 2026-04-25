"""
Convert covid_data.mat (MATLAB format) to covid_data.json for the Python app.

The MATLAB cell array structure:
- Row 1: [empty, empty, date1, date2, ...] (header row with dates)
- Row 2+: [country_name, state_name_or_empty, [cases,deaths], [cases,deaths], ...]
  - If state_name is empty, this row is the country aggregate
  - If state_name is present, this row is a state within the preceding country
"""

import json
import sys
import numpy as np
from scipy.io import loadmat


def convert():
    print("Loading covid_data.mat...")
    mat = loadmat("covid_data.mat", squeeze_me=False)

    # The main variable is typically named 'covid_data' inside the .mat file
    # Find the right key (skip __header__, __version__, __globals__)
    data_key = None
    for key in mat:
        if not key.startswith("__"):
            data_key = key
            break

    if data_key is None:
        print("ERROR: No data variable found in .mat file")
        sys.exit(1)

    print(f"Found data variable: '{data_key}'")
    raw = mat[data_key]
    print(f"Shape: {raw.shape}")

    n_rows, n_cols = raw.shape

    # Extract dates from row 0, columns 2+
    dates = []
    for j in range(2, n_cols):
        cell = raw[0, j]
        # Cell might be a numpy array containing a string
        if hasattr(cell, 'flat'):
            val = cell.flat[0] if cell.size > 0 else str(cell)
        else:
            val = cell
        # Convert to string
        date_str = str(val).strip()
        dates.append(date_str)

    print(f"Found {len(dates)} dates: {dates[0]} ... {dates[-1]}")

    # Parse country/state rows
    countries = []
    current_country = None
    i = 1  # skip header row

    while i < n_rows:
        # Get country name
        country_cell = raw[i, 0]
        if hasattr(country_cell, 'flat'):
            country_name = str(country_cell.flat[0]).strip() if country_cell.size > 0 else ""
        else:
            country_name = str(country_cell).strip()

        # Get state name
        state_cell = raw[i, 1]
        if hasattr(state_cell, 'flat'):
            state_name = str(state_cell.flat[0]).strip() if state_cell.size > 0 else ""
        else:
            state_name = str(state_cell).strip()

        # Extract cases and deaths for this row
        cumulative_cases = []
        cumulative_deaths = []
        for j in range(2, n_cols):
            cell = raw[i, j]
            if hasattr(cell, 'flat') and cell.size >= 2:
                arr = cell.flatten()
                cumulative_cases.append(int(arr[0]))
                cumulative_deaths.append(int(arr[1]))
            elif hasattr(cell, '__len__') and len(cell) >= 2:
                cumulative_cases.append(int(cell[0]))
                cumulative_deaths.append(int(cell[1]))
            else:
                # Try to handle scalar or other format
                val = int(cell) if cell is not None else 0
                cumulative_cases.append(val)
                cumulative_deaths.append(0)

        # Determine if this is a country-aggregate row or a state row
        # The first occurrence of a country name is the aggregate
        # Subsequent rows with the same country name are states
        if current_country is None or country_name != current_country["name"]:
            # New country
            current_country = {
                "name": country_name,
                "cumulative_cases": cumulative_cases,
                "cumulative_deaths": cumulative_deaths,
                "states": []
            }
            countries.append(current_country)
        else:
            # This is a state within the current country
            current_country["states"].append({
                "name": state_name if state_name else country_name,
                "cumulative_cases": cumulative_cases,
                "cumulative_deaths": cumulative_deaths,
            })

        i += 1

    print(f"Parsed {len(countries)} countries")
    countries_with_states = [c for c in countries if len(c["states"]) > 0]
    print(f"  {len(countries_with_states)} countries have state-level data")

    # Build output
    output = {
        "dates": dates,
        "countries": countries
    }

    out_path = "covid_data.json"
    print(f"Writing {out_path}...")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    file_size_mb = len(json.dumps(output)) / (1024 * 1024)
    print(f"Done! Output: {out_path} ({file_size_mb:.1f} MB)")


if __name__ == "__main__":
    convert()
