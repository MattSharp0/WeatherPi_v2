# ARMv6 / Raspberry Pi Zero (1st gen) + `uv` build notes

Notes from getting a Python project running on a first-generation Raspberry Pi Zero via `uv`. Written up after fighting a Rust-extension package (`pydantic-core`); the same root causes almost certainly apply to `numpy` or any other package with compiled (C/Fortran/Rust) extensions.

## The core problem

The original Raspberry Pi Zero (not the Zero 2 W) uses **ARMv6**, an older architecture that most of the modern Python packaging ecosystem doesn't build for. Two separate tools fall short of it:

- **`uv`'s managed Python downloads** (`uv python install`) — no ARMv6 build exists at all. Fix: don't let `uv` try to fetch a Python; relax `requires-python` in `pyproject.toml` to match whatever's actually on the system (e.g. `>=3.11` instead of a tighter/exact pin) so `uv` uses the system-installed interpreter instead.
- **PyPI wheel coverage for ARMv6 is thin-to-nonexistent** for any package with compiled extensions. PyPI's official wheels typically only target `armv7l`/`aarch64`, not `armv6l`. Without a prebuilt wheel, `pip`/`uv` falls back to compiling from source — slow and memory-risky on 512MB, single-core hardware, sometimes taking a very long time or failing outright.

## The fix: piwheels.org

The standard, well-established answer to exactly this problem — a community project that builds and hosts prebuilt wheels specifically for Raspberry Pi hardware (including `armv6l`), covering the large majority of popular PyPI packages. **numpy specifically has been one of piwheels' flagship-supported packages for years** — it's a big part of why the project exists in the first place.

Raspberry Pi OS's system `pip` is pre-configured to use piwheels automatically (via `/etc/pip.conf`). `uv` is not — you have to point it there explicitly.

## `uv`-specific gotchas

1. **`uv sync` installs from whatever's already pinned in `uv.lock` — it doesn't re-resolve.** Pointing `--default-index` at piwheels only affects `uv lock` (resolution). If you just run `uv sync --default-index ...` against an existing lock with no piwheels entries, nothing changes. You need to re-lock first:

   ```bash
   uv lock --default-index https://www.piwheels.org/simple
   uv sync
   ```

2. **`--default-index` replaces the index globally, for every package** — not just the one that needs it. This breaks lockfile portability to other machines (it drops the PyPI/macOS wheel entries for every package, not just the ARM-only one). If you need one shared lockfile that works across dev machine + Pi, this is a real problem, not a cosmetic one.

3. **Scoping to a single package via `[tool.uv.sources]` + an `explicit = true` index** (the documented way to pin one package to an alternate index without affecting the rest of resolution) did **not** take effect in practice, despite matching the documented syntax exactly:

   ```toml
   [tool.uv.sources]
   numpy = { index = "piwheels" }

   [[tool.uv.index]]
   name = "piwheels"
   url = "https://www.piwheels.org/simple"
   explicit = true
   ```

   Worth trying, but don't assume it works — verify by grepping the regenerated `uv.lock` for the expected wheel entry (`linux_armv6l`) before trusting it.

4. **What actually worked**: treat it as a manual, device-local step rather than something baked into the shared repo/lockfile.

   ```bash
   uv lock --default-index https://www.piwheels.org/simple
   uv sync
   ```

   Run directly on the Pi whenever a fresh venv build is needed there. Don't commit the regenerated lockfile back to the shared repo — it's not valid for other platforms.

5. **⚠️ Most likely to explain a confusing/inconsistent hang**: a `uv sync`/`uv lock` can behave bizarrely — seemingly hanging, or ignoring correct config — if **a different project's hung `uv` process (also compiling something from source) is holding a lock on the shared `~/.cache/uv` directory**. If you have multiple `uv`-managed projects on the same Pi, a stuck compile in _any_ of them can silently block `uv` operations in _all_ of them via that shared cache. Check before assuming a fresh hang is a fresh problem:

   ```bash
   ps aux | grep -i "uv\|cargo\|rustc\|cc1"
   uv cache clean --force
   ```

6. **`uv run` re-syncs the venv against `uv.lock` on every single invocation.** If any long-running/repeated process uses `uv run` as its entry point (e.g. a systemd `ExecStart`), every restart re-validates dependencies — and if the lock ever points at something needing a source build, every restart risks retriggering it. Fix: point production invocations at the venv's binary directly instead of going through `uv run`:
   ```
   ExecStart=/path/to/.venv/bin/python ...
   ```
   instead of
   ```
   ExecStart=/path/to/.local/bin/uv run ...
   ```

## Before reaching for piwheels at all

Confirm you actually need whatever's forcing the compile in the first place. Sometimes a dependency pulls in optional/compiled extras that aren't functionally necessary (e.g. `uvicorn[standard]`'s `uvloop`/`httptools` — performance conveniences, not requirements at low traffic volumes). Dropping unused extras can eliminate the compile problem entirely, no workaround needed. If you genuinely need the real package (as with numpy, most likely), piwheels is the right answer, not avoidance.
