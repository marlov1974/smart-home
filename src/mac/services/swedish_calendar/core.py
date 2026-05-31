"""Deterministic Swedish special-day calendar for P0035."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path


CALENDAR_COLUMNS = (
    "date",
    "year",
    "month",
    "day",
    "weekday",
    "weekday_name",
    "iso_year",
    "iso_week",
    "iso_weekday",
    "day_of_year",
    "is_leap_day",
    "base_day_type",
    "special_day_type",
    "special_day_name",
    "special_day_group",
    "holiday_strength",
    "is_public_holiday",
    "is_fixed_date_holiday",
    "is_movable_holiday",
    "is_major_social_holiday",
    "is_holiday_eve",
    "is_bridge_day",
    "bridge_strength",
    "bridge_direction",
    "bridge_anchor",
    "is_holiday_period_day",
    "period_name",
    "period_day_index",
    "is_pre_holiday_transition",
    "is_post_holiday_recovery",
    "normal_weekday_override",
    "notes",
)

WEEKDAY_NAMES = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

FIXED_PUBLIC_HOLIDAYS = {
    (1, 1): ("new_years_day", "New Year's Day"),
    (1, 6): ("epiphany", "Epiphany"),
    (5, 1): ("first_may", "First May"),
    (6, 6): ("national_day", "National Day"),
    (12, 25): ("christmas_day", "Christmas Day"),
    (12, 26): ("boxing_day", "Boxing Day"),
}


def easter_sunday(year: int) -> date:
    """Return Gregorian Easter Sunday for a year."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def midsummer_eve(year: int) -> date:
    day = date(year, 6, 19)
    while day.weekday() != 4:
        day += timedelta(days=1)
    return day


def all_saints_day(year: int) -> date:
    day = date(year, 10, 31)
    while day.weekday() != 5:
        day += timedelta(days=1)
    return day


def generate_calendar(start_year: int = 2022, end_year: int = 2035) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    current = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    while current <= end:
        rows.append(classify_special_day(current))
        current += timedelta(days=1)
    return rows


def classify_special_day(day: date) -> dict[str, object]:
    year = day.year
    easter = easter_sunday(year)
    movable = {
        easter - timedelta(days=3): ("maundy_thursday", "Maundy Thursday", False),
        easter - timedelta(days=2): ("good_friday", "Good Friday", True),
        easter - timedelta(days=1): ("easter_saturday", "Easter Saturday", False),
        easter: ("easter_sunday", "Easter Sunday", True),
        easter + timedelta(days=1): ("easter_monday", "Easter Monday", True),
        easter + timedelta(days=39): ("ascension_day", "Ascension Day", True),
        easter + timedelta(days=49): ("pentecost_sunday", "Pentecost Sunday", True),
    }
    midsummer = midsummer_eve(year)
    midsummer_day = midsummer + timedelta(days=1)
    all_saints = all_saints_day(year)

    iso = day.isocalendar()
    base = "normal_weekday" if day.weekday() < 5 else "normal_saturday" if day.weekday() == 5 else "normal_sunday"
    row = {
        "date": day.isoformat(),
        "year": year,
        "month": day.month,
        "day": day.day,
        "weekday": day.weekday(),
        "weekday_name": WEEKDAY_NAMES[day.weekday()],
        "iso_year": iso.year,
        "iso_week": iso.week,
        "iso_weekday": iso.weekday,
        "day_of_year": day.timetuple().tm_yday,
        "is_leap_day": day.month == 2 and day.day == 29,
        "base_day_type": base,
        "special_day_type": "",
        "special_day_name": "",
        "special_day_group": "",
        "holiday_strength": 0.0,
        "is_public_holiday": False,
        "is_fixed_date_holiday": False,
        "is_movable_holiday": False,
        "is_major_social_holiday": False,
        "is_holiday_eve": False,
        "is_bridge_day": False,
        "bridge_strength": "",
        "bridge_direction": "",
        "bridge_anchor": "",
        "is_holiday_period_day": False,
        "period_name": "",
        "period_day_index": "",
        "is_pre_holiday_transition": False,
        "is_post_holiday_recovery": False,
        "normal_weekday_override": False,
        "notes": "",
    }

    _apply_period(row, day)
    _apply_bridges(row, day)

    if (day.month, day.day) in FIXED_PUBLIC_HOLIDAYS:
        slug, name = FIXED_PUBLIC_HOLIDAYS[(day.month, day.day)]
        _set_special(row, "fixed_public_holiday", slug, name, "fixed_public_holiday", 1.0)
        row["is_public_holiday"] = True
        row["is_fixed_date_holiday"] = True

    if day in movable:
        slug, name, public = movable[day]
        day_type = "movable_public_holiday" if public else "holiday_eve" if slug == "maundy_thursday" else "special_weekend_day"
        _set_special(row, day_type, slug, name, "easter_period", 1.0 if public else 0.75)
        row["is_public_holiday"] = public
        row["is_movable_holiday"] = True
        row["is_holiday_eve"] = slug == "maundy_thursday"

    if day == midsummer:
        _set_special(row, "major_social_holiday", "midsummer_eve", "Midsummer Eve", "midsummer", 1.0)
        row["is_major_social_holiday"] = True
        row["is_holiday_eve"] = True
    elif day == midsummer_day:
        _set_special(row, "major_social_holiday", "midsummer_day", "Midsummer Day", "midsummer", 1.0)
        row["is_major_social_holiday"] = True
        row["normal_weekday_override"] = True
    elif day == midsummer_day + timedelta(days=1):
        _set_special(row, "special_weekend_day", "midsummer_sunday", "Midsummer Sunday", "midsummer", 0.5)

    if day == all_saints:
        _set_special(row, "special_weekend_day", "all_saints_day", "All Saints Day", "all_saints", 0.75)
        row["normal_weekday_override"] = True
    elif day == all_saints - timedelta(days=1):
        _set_special(row, "pre_holiday_transition_day", "all_saints_friday", "All Saints Friday", "all_saints", 0.35)
        row["is_pre_holiday_transition"] = True

    if (day.month, day.day) == (12, 24):
        _set_special(row, "major_social_holiday", "christmas_eve", "Christmas Eve", "christmas_new_year", 1.0)
        row["is_major_social_holiday"] = True
        row["is_holiday_eve"] = True
    elif (day.month, day.day) == (12, 31):
        _set_special(row, "major_social_holiday", "new_years_eve", "New Year's Eve", "christmas_new_year", 1.0)
        row["is_major_social_holiday"] = True
        row["is_holiday_eve"] = True

    if not row["special_day_type"]:
        row["special_day_type"] = row["base_day_type"]
        row["special_day_name"] = row["base_day_type"]
        row["special_day_group"] = "normal"
    return row


def write_calendar_csv(rows: list[dict[str, object]], path: Path | str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CALENDAR_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row[key]) for key in CALENDAR_COLUMNS})


def _apply_period(row: dict[str, object], day: date) -> None:
    if day.month == 12 and 23 <= day.day <= 31:
        row["is_holiday_period_day"] = True
        row["period_name"] = "christmas_new_year"
        row["period_day_index"] = day.day - 22
        if day.day == 23:
            row["is_pre_holiday_transition"] = True
            _set_special(row, "pre_holiday_transition_day", "christmas_pre_transition", "Christmas pre-transition", "christmas_new_year", 0.35)
        elif 27 <= day.day <= 30:
            _set_special(row, "holiday_period_day", "christmas_between_days", "Christmas between-days", "christmas_new_year", 0.45)
    elif day.month == 1 and day.day == 1:
        row["is_holiday_period_day"] = True
        row["period_name"] = "christmas_new_year"
        row["period_day_index"] = 10
    elif day.month == 1 and day.day == 2:
        row["is_post_holiday_recovery"] = True
        _set_special(row, "post_holiday_recovery_day", "new_year_recovery", "New Year recovery", "christmas_new_year", 0.25)


def _apply_bridges(row: dict[str, object], day: date) -> None:
    for holiday, slug in _public_holidays(day.year).items():
        if holiday.weekday() == 1 and day == holiday - timedelta(days=1):
            _set_bridge(row, "bridge_day_strong", "strong", "before", slug, 0.65)
        elif holiday.weekday() == 3 and day == holiday + timedelta(days=1):
            _set_bridge(row, "bridge_day_strong", "strong", "after", slug, 0.65)
        elif holiday.weekday() == 2 and day in (holiday + timedelta(days=1), holiday + timedelta(days=2)):
            _set_bridge(row, "bridge_day_weak", "weak", "after", slug, 0.35)
        elif holiday.weekday() == 0 and day == holiday - timedelta(days=3):
            row["is_pre_holiday_transition"] = True
            if not row["special_day_type"]:
                _set_special(row, "pre_holiday_transition_day", f"pre_{slug}", f"Pre {slug}", "bridge", 0.25)


def _public_holidays(year: int) -> dict[date, str]:
    easter = easter_sunday(year)
    holidays = {date(year, month, day): slug for (month, day), (slug, _name) in FIXED_PUBLIC_HOLIDAYS.items()}
    holidays.update(
        {
            easter - timedelta(days=2): "good_friday",
            easter: "easter_sunday",
            easter + timedelta(days=1): "easter_monday",
            easter + timedelta(days=39): "ascension_day",
            easter + timedelta(days=49): "pentecost_sunday",
        }
    )
    return holidays


def _set_bridge(row: dict[str, object], day_type: str, strength: str, direction: str, anchor: str, holiday_strength: float) -> None:
    if row["special_day_type"]:
        return
    _set_special(row, day_type, day_type, day_type, "bridge", holiday_strength)
    row["is_bridge_day"] = True
    row["bridge_strength"] = strength
    row["bridge_direction"] = direction
    row["bridge_anchor"] = anchor


def _set_special(
    row: dict[str, object],
    day_type: str,
    slug: str,
    name: str,
    group: str,
    strength: float,
) -> None:
    row["special_day_type"] = day_type
    row["special_day_name"] = slug
    row["special_day_group"] = group
    row["holiday_strength"] = strength
    row["notes"] = name


def _csv_value(value: object) -> object:
    if isinstance(value, bool):
        return "true" if value else "false"
    return value
