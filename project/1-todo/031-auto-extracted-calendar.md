# Use Auto-Extracted Calendar

## Abstract

Write events to a dedicated "Auto-Extracted" calendar instead of the primary calendar.

## Priority: 40

- Value: 7/10 — Prevents cluttering the user's primary calendar with auto-extracted events. Key usability feature.
- Momentum: 3/10 — Calendar-writer service exists and works. Small extension to existing code.
- Effort: 3/10 — Add env var, thread a parameter through two files, update docker-compose.
- Risk: 3/10 — Straightforward change. Calendar must exist on the Google account beforehand.

## Timeline

- Captured: 2026-04-27

## Details

### Research findings

- `services/calendar-writer/calendar_writer.py`: `write_event` hardcodes `calendars/primary/events` in the API URL
- `services/calendar-writer/app.py`: accepts no `calendar_id` in request body
- Google Calendar API supports any calendar ID in the URL path: `calendars/{calendarId}/events`
- The "Auto-Extracted" calendar must be created manually in Google Calendar first (one-time setup)

### Implementation plan (TDD)

1. **Tests first** in `services/calendar-writer/tests/`:
   - Test that `write_event` uses `CALENDAR_ID` env var when set
   - Test that `write_event` defaults to `primary` when env var is absent
   - Test that `app.py` endpoint passes calendar_id through
2. **calendar_writer.py**: Read `CALENDAR_ID` from env (default `primary`). Use it in the API URL: `calendars/{calendar_id}/events`
3. **app.py**: No change needed — calendar_id comes from env, not request body
4. **docker-compose.yml**: Add `CALENDAR_ID` env var to calendar-writer service, set to the Auto-Extracted calendar's ID
5. **Browser step**: Create "Auto-Extracted" calendar in Google Calendar, copy its calendar ID
6. **UAT**: Run orchestrator pipeline, verify event appears in Auto-Extracted calendar (not primary)

## Verification

- Tests pass with calendar ID override
- Pipeline creates event in Auto-Extracted calendar
- Primary calendar unchanged
