# Use Auto-Extracted Calendar

## Abstract

Write events to a dedicated "Auto-Extracted" calendar instead of the primary calendar.

## Priority: 31

- Value: 7/10 — Prevents cluttering the user's primary calendar with auto-extracted events.
- Momentum: 3/10 — Calendar-writer service existed, small extension.
- Effort: 3/10 — Add env var, thread parameter through two files, update docker-compose.
- Risk: 3/10 — Straightforward change.

## Timeline

- Captured: 2026-04-27
- Refined: 2026-04-27
- Started: 2026-04-27
- Verified: 2026-04-27
- Done: 2026-04-27

## Details

- `CalendarWriter.__init__` now accepts `calendar_id` param (default `"primary"`)
- `write_event` uses `self.calendar_id` in API URL instead of hardcoded `"primary"`
- `app.py` reads `CALENDAR_ID` env var
- `docker-compose.yml` passes `CALENDAR_ID=${CALENDAR_ID:-primary}` to calendar-writer
- `.env` file created with the Auto-Extracted calendar ID (gitignored)
- `.gitignore` updated to exclude `.env`

## Verification

UAT: `POST /write` returned event with `organizer.displayName: "Auto-Extracted"` and correct calendar email. Event confirmed on Auto-Extracted calendar, not primary.
