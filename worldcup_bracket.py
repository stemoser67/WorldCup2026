#!/usr/bin/env python3
"""
World Cup 2026 Tracker - Day 2: Bracket Printer
Same live data source as Day 1 (openfootball/worldcup.json), but now we use
the `rich` library to render the knockout bracket as a proper terminal
visual: color-coded rounds, winners highlighted, upcoming matches dimmed,
and today's matches highlighted in yellow.
"""

from datetime import date

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

DATA_URL = ("https://raw.githubusercontent.com/openfootball/worldcup.json"
            "/master/2026/worldcup.json")

# Round names in bracket order, paired with the color rich should use.
ROUNDS = [
    ("Round of 32",            "bright_blue"),
    ("Round of 16",            "cyan"),
    ("Quarter-final",          "magenta"),
    ("Semi-final",             "yellow"),
    ("Match for third place",  "bright_black"),
    ("Final",                  "gold1"),
]

console = Console()


# ---------------------------------------------------------------------------
# FETCH
# ---------------------------------------------------------------------------

def fetch_data():
    response = requests.get(DATA_URL, timeout=10)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# FORMATTING HELPERS (same as Day 1)
# ---------------------------------------------------------------------------

def pretty_team(name):
    if name.startswith("W") and name[1:].isdigit():
        return f"Winner of #{name[1:]}"
    if name.startswith("L") and name[1:].isdigit():
        return f"Loser of #{name[1:]}"
    if len(name) == 2 and name[0].isdigit() and name[1].isalpha():
        position = "winner" if name[0] == "1" else "runner-up"
        return f"Group {name[1]} {position}"
    if "/" in name:
        return f"Best 3rd ({name})"
    return name


def is_placeholder(name):
    """True if the name is still an unresolved placeholder code."""
    if name.startswith("W") and name[1:].isdigit():
        return True
    if name.startswith("L") and name[1:].isdigit():
        return True
    if len(name) == 2 and name[0].isdigit() and name[1].isalpha():
        return True
    if "/" in name:
        return True
    return False


def format_score(score):
    g1, g2 = score["ft"]
    if "p" in score:
        p1, p2 = score["p"]
        if "et" in score:
            g1, g2 = score["et"]
        return f"{g1}\u2013{g2} ({p1}-{p2} pens)"
    if "et" in score:
        g1, g2 = score["et"]
        return f"{g1}\u2013{g2} (a.e.t.)"
    return f"{g1}\u2013{g2}"


def winner_of(match):
    """Return 1 if team1 won, 2 if team2 won, or 0 for a draw / unplayed."""
    if "score" not in match:
        return 0
    score = match["score"]

    if "p" in score:
        p1, p2 = score["p"]
        return 1 if p1 > p2 else 2 if p2 > p1 else 0

    if "et" in score:
        g1, g2 = score["et"]
        if g1 != g2:
            return 1 if g1 > g2 else 2

    g1, g2 = score["ft"]
    if g1 != g2:
        return 1 if g1 > g2 else 2
    return 0


# ---------------------------------------------------------------------------
# STYLING A MATCH
# ---------------------------------------------------------------------------

def styled_team(name, is_winner, is_placeholder_name):
    """Return a rich Text object with the right style for this team."""
    text = Text(pretty_team(name))
    if is_placeholder_name:
        text.stylize("dim italic")
    elif is_winner:
        text.stylize("bold bright_green")
    else:
        text.stylize("white")
    return text


def build_match_row(match, today_str):
    """Return a tuple of rich Text objects for one row in the round's table."""
    t1_name = match["team1"]
    t2_name = match["team2"]
    num = f"#{match.get('num', '?')}"
    date_str = match.get("date", "")
    played = "score" in match
    is_today = date_str == today_str

    w = winner_of(match)  # 0, 1, or 2

    num_text = Text(num, style="bold")
    date_text = Text(date_str)
    if is_today and not played:
        date_text.stylize("bold yellow")

    t1_text = styled_team(t1_name, is_winner=(w == 1),
                          is_placeholder_name=is_placeholder(t1_name))
    t2_text = styled_team(t2_name, is_winner=(w == 2),
                          is_placeholder_name=is_placeholder(t2_name))

    if played:
        score_text = Text(format_score(match["score"]), style="bold white")
    elif is_today:
        score_text = Text("TODAY", style="bold yellow")
    else:
        score_text = Text("vs", style="dim")

    return num_text, date_text, t1_text, score_text, t2_text


# ---------------------------------------------------------------------------
# ROUND PANEL
# ---------------------------------------------------------------------------

def build_round_panel(round_name, matches, color, today_str):
    """Return a rich Panel containing the styled table for this round."""
    table = Table.grid(padding=(0, 1), expand=False)
    table.add_column(justify="left")   # match number
    table.add_column(justify="left")   # date
    table.add_column(justify="right")  # team1
    table.add_column(justify="center") # score / vs
    table.add_column(justify="left")   # team2

    for match in matches:
        table.add_row(*build_match_row(match, today_str))

    played_count = sum(1 for m in matches if "score" in m)
    subtitle = f"{played_count} / {len(matches)} played"

    return Panel(
        table,
        title=f"[bold {color}]{round_name}[/]",
        subtitle=f"[{color}]{subtitle}[/]",
        border_style=color,
        padding=(1, 2),
    )


# ---------------------------------------------------------------------------
# MAIN DISPLAY
# ---------------------------------------------------------------------------

def show_bracket(matches):
    """Print the whole knockout bracket, round by round, with rich styling."""
    today_str = date.today().isoformat()

    # Big header
    header = Text("WORLD CUP 2026 \u2014 KNOCKOUT BRACKET",
                  style="bold gold1 on grey11", justify="center")
    console.print(Panel(header, border_style="gold1", padding=(1, 4)))
    console.print()

    for round_name, color in ROUNDS:
        round_matches = [m for m in matches if m["round"] == round_name]
        if not round_matches:
            continue
        round_matches.sort(key=lambda m: m.get("num", 0))
        console.print(build_round_panel(round_name, round_matches,
                                         color, today_str))
        console.print()

    # Legend
    legend = Table.grid(padding=(0, 2))
    legend.add_column()
    legend.add_column()
    legend.add_column()
    legend.add_row(
        Text("Legend:", style="bold"),
        Text("winner", style="bold bright_green"),
        Text("upcoming placeholder", style="dim italic"),
    )
    legend.add_row(
        Text(""),
        Text("today's match", style="bold yellow"),
        Text("score / result", style="bold white"),
    )
    console.print(legend)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    data = fetch_data()
    show_bracket(data["matches"])


if __name__ == "__main__":
    main()