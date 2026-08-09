"""
Offline filter tester — simulates showtime filtering logic without network calls.
Use this to verify your BMS_THEATRE, BMS_TIME, BMS_DATES, BMS_LANGUAGE filters work as expected.
"""

from dataclasses import dataclass, field

TIME_PERIODS = {
    "morning":   (600, 1200),
    "afternoon": (1200, 1600),
    "evening":   (1600, 1900),
    "night":     (1900, 2400),
}


@dataclass
class ShowInfo:
    venue_code: str
    venue_name: str
    session_id: str
    date_code: str
    time: str
    time_code: str
    screen_attr: str
    language: str = ""
    categories: list = field(default_factory=list)


# ── Sample data mimicking real BMS API responses for Spider-Man ────────
SAMPLE_SHOWS = [
    # PVR: Palazzo, The Nexus Vijaya Mall - English shows
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S1", "20260815", "10:30 AM", "1030", "EPIQ 3D", "English", []),
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S2", "20260815", "01:45 PM", "1345", "3D", "English", []),
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S3", "20260815", "04:30 PM", "1630", "2D", "English", []),
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S4", "20260815", "07:15 PM", "1915", "EPIQ 3D", "English", []),
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S5", "20260815", "10:00 PM", "2200", "3D", "English", []),
    # PVR: Palazzo - Tamil shows
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S6", "20260815", "11:00 AM", "1100", "3D", "Tamil", []),
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S7", "20260815", "02:30 PM", "1430", "2D", "Tamil", []),
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S8", "20260815", "06:00 PM", "1800", "3D", "Tamil", []),
    # PVR: Palazzo - Telugu shows
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S9", "20260815", "12:00 PM", "1200", "3D", "Telugu", []),
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S10", "20260815", "08:30 PM", "2030", "3D", "Telugu", []),

    # PVR: Heritage RSL ECR, Chennai - English
    ShowInfo("PVR001", "PVR: Heritage RSL ECR, Chennai", "S11", "20260815", "10:10 PM", "2210", "2D", "English", []),
    ShowInfo("PVR001", "PVR: Heritage RSL ECR, Chennai", "S12", "20260815", "10:40 PM", "2240", "2D", "English", []),

    # PVR: VR Chennai, Anna Nagar
    ShowInfo("PVR002", "PVR: VR Chennai, Anna Nagar", "S13", "20260815", "07:25 PM", "1925", "2D", "English", []),

    # PVR: Ampa Mall
    ShowInfo("PVR003", "PVR: Ampa Mall, Nelson Manickam Road", "S14", "20260815", "10:10 PM", "2210", "2D", "English", []),

    # Non-PVR venues
    ShowInfo("INOX01", "INOX: Phoenix Marketcity, Velachery", "S15", "20260815", "09:30 PM", "2130", "2D", "English", []),
    ShowInfo("CINE01", "Cinepolis: Express Avenue Mall", "S16", "20260815", "08:00 PM", "2000", "3D", "Tamil", []),
    ShowInfo("SPI001", "SPI: Sathyam Cinemas", "S17", "20260815", "06:30 PM", "1830", "IMAX", "English", []),

    # Next day shows
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S18", "20260816", "10:30 AM", "1030", "EPIQ 3D", "English", []),
    ShowInfo("PVR010", "PVR: Palazzo, The Nexus Vijaya Mall", "S19", "20260816", "07:15 PM", "1915", "EPIQ 3D", "English", []),
    ShowInfo("PVR001", "PVR: Heritage RSL ECR, Chennai", "S20", "20260816", "10:10 PM", "2210", "2D", "English", []),
]


def filter_shows(shows, theatre_filter, time_periods, date_codes, language_filter=""):
    """Exact copy of the filter logic from main.py."""
    result = []
    kws = [k.strip().lower() for k in theatre_filter.split(",")
           if k.strip()] if theatre_filter else []
    periods = [p.strip().lower() for p in time_periods.split(",")
               if p.strip()] if time_periods else []
    dates_set = set(d.strip() for d in date_codes.split(",")
                    if d.strip()) if date_codes else set()
    langs = [l.strip().lower() for l in language_filter.split(",")
             if l.strip()] if language_filter else []

    for s in shows:
        # Theatre filter (checks venue_name AND screen_attr)
        if kws:
            name_lower = s.venue_name.lower()
            attr_lower = s.screen_attr.lower()
            if not any(k in name_lower or k in attr_lower for k in kws):
                continue

        # Language filter
        if langs and s.language.lower() not in langs:
            continue

        # Date filter
        if dates_set and s.date_code and s.date_code not in dates_set:
            continue

        # Time period filter
        if periods:
            try:
                tc = int(s.time_code)
            except ValueError:
                tc = 0
            matched = False
            for p in periods:
                if p in TIME_PERIODS:
                    lo, hi = TIME_PERIODS[p]
                    if lo <= tc < hi:
                        matched = True
                        break
            if not matched:
                continue

        result.append(s)
    return result


def print_results(shows, label):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    if not shows:
        print("  (no matches)")
        return
    for s in shows:
        fmt = f" [{s.screen_attr}]" if s.screen_attr else ""
        lang = f" ({s.language})" if s.language else ""
        print(f"  {s.venue_name} — {s.time}{fmt}{lang} [{s.date_code}]")


def main():
    print("=" * 60)
    print("  BMS Filter Logic — Offline Tester")
    print("=" * 60)

    total = len(SAMPLE_SHOWS)
    print(f"\n  Total sample shows: {total}")

    # Show all shows first
    print_results(SAMPLE_SHOWS, "ALL SHOWS (no filters)")

    # Test 1: Theatre filter — PVR only
    r1 = filter_shows(SAMPLE_SHOWS, "PVR", "", "")
    print_results(r1, f'THEATRE="PVR" -> {len(r1)} matches')

    # Test 2: Specific PVR venue
    r2 = filter_shows(SAMPLE_SHOWS, "Palazzo", "", "")
    print_results(r2, f'THEATRE="Palazzo" -> {len(r2)} matches')

    # Test 3: Theatre filter — IMAX only
    r3 = filter_shows(SAMPLE_SHOWS, "IMAX", "", "")
    print_results(r3, f'THEATRE="IMAX" -> {len(r3)} matches')

    # Test 4: Theatre filter — EPIQ
    r4 = filter_shows(SAMPLE_SHOWS, "EPIQ", "", "")
    print_results(r4, f'THEATRE="EPIQ" -> {len(r4)} matches')

    # Test 5: Language filter — English only
    r5 = filter_shows(SAMPLE_SHOWS, "", "", "", "English")
    print_results(r5, f'LANGUAGE="English" -> {len(r5)} matches')

    # Test 6: Language filter — Tamil only
    r6 = filter_shows(SAMPLE_SHOWS, "", "", "", "Tamil")
    print_results(r6, f'LANGUAGE="Tamil" -> {len(r6)} matches')

    # Test 7: Language filter — English,Tamil
    r7 = filter_shows(SAMPLE_SHOWS, "", "", "", "English,Tamil")
    print_results(r7, f'LANGUAGE="English,Tamil" -> {len(r7)} matches')

    # Test 8: Combined — PVR + English + night
    r8 = filter_shows(SAMPLE_SHOWS, "PVR", "night", "", "English")
    print_results(r8, f'THEATRE="PVR" + TIME="night" + LANGUAGE="English" -> {len(r8)} matches')

    # Test 9: Combined — Palazzo + English + night + dates
    r9 = filter_shows(SAMPLE_SHOWS, "Palazzo", "night", "20260815,20260816", "English")
    print_results(r9, f'THEATRE="Palazzo" + TIME="night" + DATES="20260815,20260816" + LANGUAGE="English" -> {len(r9)} matches')

    # Test 10: Format filter via THEATRE — 3D only
    r10 = filter_shows(SAMPLE_SHOWS, "3D", "", "", "")
    print_results(r10, f'THEATRE="3D" -> {len(r10)} matches')

    # Test 11: EPIQ 3D + English + night
    r11 = filter_shows(SAMPLE_SHOWS, "EPIQ", "night", "", "English")
    print_results(r11, f'THEATRE="EPIQ" + TIME="night" + LANGUAGE="English" -> {len(r11)} matches')

    # Explain logic
    print(f"\n{'='*60}")
    print("  HOW THE LOGIC WORKS")
    print(f"{'='*60}")
    print("""
  1. THEATRE filter uses OR logic:
     "PVR,IMAX" -> keeps shows where venue_name OR screen_attr contains "pvr" OR "imax"
     Case-insensitive substring match.

     Examples:
     - "PVR" matches "PVR: Palazzo..." (venue_name)
     - "Palazzo" matches "PVR: Palazzo..." (venue_name)
     - "IMAX" matches "... [IMAX]" (screen_attr)
     - "EPIQ" matches "... [EPIQ 3D]" (screen_attr)
     - "3D" matches "... [3D]" (screen_attr)

  2. LANGUAGE filter uses OR logic:
     "English,Tamil" -> keeps shows where language is "english" OR "tamil"
     Case-insensitive exact match.

  3. TIME filter:
     "night" -> keeps shows with time_code 1900-2400 (7 PM - 12 AM)
     "evening" -> 1600-1900 (4 PM - 7 PM)
     "afternoon" -> 1200-1600 (12 PM - 4 PM)
     "morning" -> 0600-1200 (6 AM - 12 PM)
     Multiple: "evening,night" -> 1600-2400

  4. DATE filter:
     "20260815,20260816" -> keeps only those exact dates
     Empty -> no date filtering

  5. All filters are ANDed together:
     A show must pass ALL active filters to be kept.

  6. Example configs:
     - All English shows at Palazzo: THEATRE="Palazzo" LANGUAGE="English"
     - All 3D shows: THEATRE="3D"
     - English EPIQ 3D at night: THEATRE="EPIQ" TIME="night" LANGUAGE="English"
""")


if __name__ == "__main__":
    main()
