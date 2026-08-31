# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run (default weather display)
python main.py

# Run with flags
python main.py -I                    # display image
python main.py -T "some text"        # display text
python main.py -L DEBUG              # set log level (DEBUG | INFO | WARN | ERROR)

# Format
uv run black .

# Install dependencies (Mac/dev)
uv sync --group dev

# Install with Pi-specific packages (run on Raspberry Pi)
uv sync --group rpi
```

`dev` and `rpi` are not installed by default (`default-groups = []` in `pyproject.toml`) — each must be requested explicitly via `--group`, so a plain `uv sync` on either machine only installs the base dependencies.

No test suite exists.

## Architecture

The program renders weather data onto a Pillow palette-mode image, then pushes it to an Inky pHat e-ink display (Raspberry Pi only). When run without the Inky hardware, it falls back to opening the image locally — making local development possible without a Pi.

**Execution flow:**
1. `main.py` — parses CLI args, calls the appropriate draw function, then pushes to Inky or falls back to `img.show()`
2. `weatherpi/setup.py` — runs at import time; reads `.env` for credentials and display constants. Prompts interactively for missing values. Attempts `from inky.auto import auto`; on `ImportError`, uses hardcoded fallback dimensions (250×122)
3. `weatherpi/weather_data.py` — hits the Weather Underground API: `get_current_conditions()` (PWS observations endpoint, tries stations in order until one returns 200) and `get_forecast()` (5-day daily forecast endpoint). `generate_weather_data()` merges both into the dict consumed by draw functions
4. `weatherpi/draw_functions.py` — PIL-based rendering. Three functions: `draw_weather()`, `draw_text()`, `draw_image()`. Font sizes adjust dynamically based on text length
5. `weatherpi/log.py` — daily rotating log files in `logs/<YYYY-MM-DD>.log`. `clear_logs()` trims files older than 5 days; called from `main()` at 1:00–1:30 AM
6. `weatherpi/exceptions.py` — `DataError` is the single custom exception, raised on API failures and rendered as on-screen text

**Configuration (`.env`):**
- `WU_KEY` — Weather Underground API key
- `WU_STATIONS` — comma-separated PWS station IDs tried in order (first live station wins)
- `FORECAST_ZIPCODE` — US zip code for the 5-day forecast

On first run, `setup.py` interactively prompts for any missing `.env` values and writes them.

**Display constants** (`DISPLAY_BLACK`, `DISPLAY_WHITE`, `DISPLAY_YELLOW`, `DISPLAY_WIDTH`, `DISPLAY_HEIGHT`) are defined in `setup.py` and imported everywhere. The palette-mode image uses integer color indices on hardware; on non-Pi it uses RGB tuples.

**Crontab deployment:**
```
0,30 * * * * /full/path/to/python3 /full/path/to/main.py 2>&1 | logger -t mycmd
```
Full paths required. Add `SHELL=/bin/bash` at the top of crontab if the script fails to launch.

## Pi deployment: ARMv6 / `uv sync --group rpi` build issues

The target hardware is a first-gen Pi Zero W (ARMv6). PyPI has little-to-no wheel coverage for ARMv6 on packages with compiled extensions (`numpy`, pulled in transitively by `inky`, is the current offender) — `uv sync --group rpi` falls back to compiling from source and can hang or take a very long time on this hardware.

Full writeup and gotchas: [armv6-uv-build-notes.md](armv6-uv-build-notes.md). Short version, run **on the Pi**, not on the dev Mac:

```bash
uv lock --default-index https://www.piwheels.org/simple
uv sync --group rpi
```

Do not commit the regenerated `uv.lock` — it's resolved against piwheels and isn't valid for the Mac dev environment. If the relock still hangs, check for a stuck compile from another `uv` project holding the shared `~/.cache/uv` (`ps aux | grep -i "uv\|cargo\|rustc\|cc1"`) before running `uv cache clean --force`.

Keep `dev` (`black`) out of the Pi install entirely — `pyproject.toml` sets `default-groups = []` so a bare `uv sync`/`uv sync --group rpi` never pulls it in. This isn't just tidiness: `black`'s `pytokens` dependency only ships `cp313` wheels upstream, so on the Pi's `cp311` interpreter it can't be resolved at all, piwheels or not.
