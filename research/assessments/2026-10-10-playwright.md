# Source adoption assessment — Playwright Python 1.63.0

**Status:** Recorded. This comparison does not itself authorize a dependency.

## What this record does not own

| Question | Owner |
| --- | --- |
| Download behavior and usage | `scripts/download-knou.py`, `scripts/download-knou.README.md` |
| Dependency declaration | `scripts/requirements.txt` |
| Implementation result | Code diff and local verification |

## 1. Source and scope

**Source type:** PyPI package.

**Target:** `playwright` 1.63.0 Windows AMD64 wheel, SHA-256 `2f9a707a6c6c91157ed77bff2b8caeb04b3c8d46e70d585fc134298cbe4b5cc6`. Resolved from PyPI's version listing on 2026-10-10 with `python -m pip index versions playwright`; digest and dependencies came from `https://pypi.org/pypi/playwright/1.63.0/json`.

**Licence observed:** Apache-2.0 in PyPI metadata and [upstream package metadata](https://github.com/microsoft/playwright-python/blob/main/pyproject.toml).

**In scope:** [persistent Chrome contexts](https://playwright.dev/python/docs/api/class-browsertype), [context response events](https://playwright.dev/python/docs/api/class-browsercontext), [request header access](https://playwright.dev/python/docs/api/class-request), package metadata, and a local Chrome launch.

**Out of scope:** Full package source, bundled driver, upstream tests, KNOU's private login implementation, and a live authenticated lecture download.

## 2. Observed shape

Playwright can launch installed Chrome with a separate persistent profile, observe responses from pages and popups in one context, and read matching request headers. The wheel declares `pyee<14,>=13` and `greenlet<4.0.0,>=3.1.1`. This project already uses Python and FFmpeg in `scripts/`.

## 3. Candidate comparison

| Candidate | What this project has | Route | Grounds |
| --- | --- | --- | --- |
| Persistent browser profile and network event observation | Existing `yt-dlp` CLI and FFmpeg; `yt-dlp` rejected the KNOU page URL and could not copy the active Chrome cookie DB | Direct adoption | The requested page needs login and its short-lived playlist URL appears during playback. A separate visible Chrome session lets the user log in and the script capture the request without DevTools copying. |

## 4. Evidence and limits

`python -m pip install playwright==1.63.0` installed Playwright and `pyee`; `greenlet` was already present. A local smoke check launched and closed installed Chrome. Syntax and CLI help for `scripts/download-knou.py` passed. A real KNOU login and download were not run, so site-specific behavior remains unverified.

The user's request authorizes the new behavior. `scripts/download-knou.README.md` owns usage, `scripts/requirements.txt` pins the dependency, and a live login/playback check would refuse a site integration regression. The profile stays under `%LOCALAPPDATA%`, and the script does not print tokens.

## 5. Result and reconsideration condition

Direct adoption was implemented in `scripts/download-knou.py`. No general source-adoption rule was earned. Reconsider the dependency if KNOU exposes a native offline download or a supported direct extractor.
