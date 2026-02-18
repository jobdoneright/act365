# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`act365` is a Python client library and CLI for the [ACT365](https://www.act365.eu/) access control API. It is published to PyPI and managed with Poetry.

## Commands

### Setup
```bash
poetry install --with dev
```

### Run Tests
```bash
poetry run pytest
```

Tests that make real API calls are skipped unless `ACT365_USERNAME` and `ACT365_PASSWORD` env vars are set.

Run a single test:
```bash
poetry run pytest tests/test_client.py::TestBookingClient::test_get_booking
```

### Lint
```bash
flake8 .
isort .
```

Pre-commit hooks run black, isort, flake8, and poetry checks automatically.

### Run the CLI
```bash
act365 --username $ACT365_USERNAME --password $ACT365_PASSWORD --siteid $ACT365_SITEID bookings list
act365 bookings get --id <bookingid>
act365 bookings delete --id <bookingid>
act365 bookings delete --expired
```

CLI credentials can also be provided via `ACT365_USERNAME`, `ACT365_PASSWORD`, `ACT365_SITEID` env vars.

## Architecture

The package lives in `src/act365/` and has four main modules:

- **`client.py`** — `Act365Client` is the main entrypoint. It wraps `httpx.Client` with `Act365Auth` (a custom `httpx.Auth` subclass that handles bearer token login, automatic retry on 401, and rate-limit backoff on 429). Pagination is handled via the `_getAll()` helper which uses `skipover`/`maxlimit` params.

- **`booking.py`** — Dataclasses for `Booking`, `BookingSite`, `BookingDoor`, `BookingAddress`, `BookingContact`. `Booking` stores `StartValidity`/`EndValidity` internally as `datetime` and exposes them as strings in `DD/MM/YYYY HH:MM` format (`STRPTIME_FMT`). The `dict()` method on `Booking` serializes for the API, handling the quirk where a single door must be sent as `DoorID` (int) rather than `DoorIDs` (list).

- **`cardholder.py`** — `CardHolder` is a dict-to-object mapper that merges API responses with an `empty` template. Uses property setters for `StartValid`/`EndValid` date parsing.

- **`cli.py`** — Click-based CLI with a `cli` group and a `bookings` subgroup. The `cli` group initialises credentials and stores them in `ctx.obj`. Verbosity flag (`-v`/`-vv`/`-vvv`) maps to WARNING/INFO/DEBUG.

## API Notes

API documentation: https://act365api.docs.apiary.io/#


- Base URL: `https://userapi.act365.eu/api`
- Auth: POST to `/account/login` with form-encoded `grant_type`, `username`, `password` → returns `access_token`
- Date format throughout: `DD/MM/YYYY HH:MM` (defined as `STRPTIME_FMT` in `booking.py`)
- The ACT365 API returns `DoorID` (singular int) when a booking has only one door, and `DoorIDs` (list) otherwise — the `Booking` dataclass handles this via `InitVar[DoorID]`
- `deleteBooking` posts to `url + "2/Bookings"` (note the "2" suffix — this is intentional)

## Release Process

Releases are managed by [release-please](https://github.com/googleapis/release-please). Commits must follow [Conventional Commits](https://www.conventionalcommits.org/). Merging a release PR to `main` triggers the publish workflow to PyPI.
