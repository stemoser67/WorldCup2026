"""
World Cup 2026 Tracker - Day 1: Fetch and show the knockout phase
Fetches live match data from openfootball/worldcup.json (free, no API key)
and prints every knockout-stage match in the terminal.
"""

import requests

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

DATA_URL = ("https://raw.githubusercontent.com/openfootball/worldcup.json"
            "/master/2026/worldcup.json")

KNOCKOUT_ROUNDS = [
    "Round of 32",
    "Round of 16",
    "Quarter-final",
    "Semi-final",
    "Match for third place",
    "Final",
]

# ---------------------------------------------------------------------------
# FETCH
# ---------------------------------------------------------------------------

def fetch_data():
    """Download the JSON and return the parsed dict."""
    response = requests.get(DATA_URL, timeout=10)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# FORMATTING HELPERS
# ---------------------------------------------------------------------------

def pretty_team(name):
    """Make placeholder codes like 'W73' or '2A' readable."""
    if name.startswith("W") and name[1:].isdigit():
        return f"Winner of match {name[1:]}"
    if name.startswith("L") and name[1:].isdigit():
        return f"Loser of match {name[1:]}"
    if len(name) == 2 and name[0].isdigit() and name[1].isalpha():
        position = "winner" if name[0] == "1" else "runner-up"
        return f"Group {name[1]} {position}"
    if "/" in name:
        return f"Best 3rd place ({name})"
    return name


def format_score(score):
    """Build a score string that reflects regulation, extra time, and pens.

    Examples:
        '2 - 0'                regulation result
        '1 - 1 (a.e.t.)'      decided in extra time
        '1 - 1 (3-4 pens)'    drawn after extra time, decided on penalties
    """
    g1, g2 = score["ft"]

    if "p" in score:
        p1, p2 = score["p"]
        if "et" in score:
            g1, g2 = score["et"]
        return f"{g1} \u2014 {g2} ({p1}-{p2} pens)"

    if "et" in score:
        g1, g2 = score["et"]
        return f"{g1} \u2014 {g2} (a.e.t.)"

    return f"{g1} \u2014 {g2}"


# ---------------------------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------------------------

def show_knockout(matches):
    """Print every knockout match, grouped by round, in bracket order."""
    print("=" * 70)
    print("  WORLD CUP 2026 \u2014 KNOCKOUT STAGE")
    print("=" * 70)

    for round_name in KNOCKOUT_ROUNDS:
        round_matches = [m for m in matches if m["round"] == round_name]
        if not round_matches:
            continue

        # Sort by match number so the bracket reads in order.
        round_matches.sort(key=lambda m: m.get("num", 0))

        print(f"\n  {round_name}")
        print(f"  {'-' * len(round_name)}")

        for m in round_matches:
            num = f"#{m['num']}"
            t1 = pretty_team(m["team1"])
            t2 = pretty_team(m["team2"])
            date = m.get("date", "")

            if "score" in m:
                result = format_score(m["score"])
                print(f"    {num:<5} {date}   {t1:>22}  {result:^16}  {t2:<22}")
            else:
                print(f"    {num:<5} {date}   {t1:>22}      vs        {t2:<22}")



# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    data = fetch_data()
    show_knockout(data["matches"])


if __name__ == "__main__":
    main()