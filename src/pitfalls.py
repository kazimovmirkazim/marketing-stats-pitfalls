"""Five statistical traps in marketing and sales reporting, each as one chart.

All numbers are synthetic and chosen to make the point clear.
"""
from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

IMG_DIR = Path(__file__).resolve().parent.parent / "images"

SURFACE = "#fcfcfb"
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, NEUTRAL = "#2a78d6", "#eb6834", "#c3c2b7"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "Segoe UI", "font.size": 12, "text.color": INK,
    "axes.edgecolor": BASELINE, "axes.labelcolor": INK_2,
    "xtick.color": MUTED, "ytick.color": INK_2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
})


def headline(fig, title: str, subtitle: str) -> None:
    fig.text(0.05, 0.95, title, fontsize=18, fontweight="bold", va="top")
    fig.text(0.05, 0.885, subtitle, fontsize=12, color=INK_2, va="top")
    fig.text(0.05, 0.02, "Synthetic numbers for illustration.", fontsize=9, color=MUTED)


def save(fig, name: str) -> None:
    IMG_DIR.mkdir(exist_ok=True)
    fig.savefig(IMG_DIR / name, dpi=100)
    plt.close(fig)


def wilson(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson interval for a proportion. Behaves well for small n, unlike p ± 1.96·SE."""
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return centre - half, centre + half


def percent_vs_points() -> None:
    before, after = 2.0, 3.0
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(left=0.08, right=0.92, top=0.78, bottom=0.12)
    ax.bar(["Last month", "This month"], [before, after], color=[NEUTRAL, BLUE], width=0.45)
    for x, v in enumerate([before, after]):
        ax.text(x, v + 0.06, f"{v:.0f}%", ha="center", fontsize=20, fontweight="bold")
    ax.set_ylim(0, 4)
    ax.yaxis.set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", labelsize=14, colors=INK_2)
    ax.text(0.5, 3.55, f"+{after - before:.0f} percentage point", ha="center", fontsize=16, color=INK)
    ax.text(0.5, 3.25, f"= +{100 * (after / before - 1):.0f}% relative growth", ha="center", fontsize=16, color=BLUE)
    headline(fig, "Conversion grew by 1. Or by 50. Both are true.",
             "Percentage points measure the gap between two rates. Percent measures the change relative to the start.")
    save(fig, "01_percent_vs_points.png")


def small_samples() -> None:
    cases = [("New TikTok campaign\n1 sale / 10 leads", 1, 10), ("Website form\n10 sales / 100 leads", 10, 100),
             ("Instagram\n100 sales / 1,000 leads", 100, 1000)]
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(left=0.20, right=0.92, top=0.78, bottom=0.12)
    for i, (label, s, n) in enumerate(cases[::-1]):
        lo, hi = wilson(s, n)
        ax.plot([100 * lo, 100 * hi], [i, i], color=BLUE, lw=6, solid_capstyle="round", alpha=0.35)
        ax.plot(100 * s / n, i, "o", color=BLUE, ms=12, mec=SURFACE, mew=2)
        ax.text(100 * hi + 1.5, i, f"{100 * lo:.0f}% to {100 * hi:.0f}%", va="center", fontsize=12, color=INK_2)
    ax.set_yticks(range(3), [c[0] for c in cases[::-1]], fontsize=12)
    ax.set_xlim(0, 50)
    ax.set_xticks(range(0, 51, 10), [f"{t}%" for t in range(0, 51, 10)])
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    ax.set_xlabel("Lead-to-sale conversion with 95% interval (Wilson)")
    label, s, n = cases[0]
    lo, hi = wilson(s, n)
    headline(fig, f"All three convert at {100 * s / n:.0f}%. Only one of them tells you much.",
             f"With {n} leads the true rate could be anywhere from {100 * lo:.0f}% to {100 * hi:.0f}%. "
             "The interval shrinks as the sample grows.")
    save(fig, "02_small_samples.png")


def simpson() -> None:
    # (leads, sales) per brand, per period
    data = {"Instagram": [(1000, 50), (2000, 120)], "Call center": [(200, 30), (100, 16)]}
    total = [tuple(sum(v) for v in zip(*(d[p] for d in data.values()))) for p in (0, 1)]
    groups = {**data, "Total": total}
    fig, axes = plt.subplots(1, 3, figsize=(16, 9), sharey=True)
    fig.subplots_adjust(left=0.06, right=0.97, top=0.76, bottom=0.12, wspace=0.15)
    for ax, (name, periods) in zip(axes, groups.items()):
        rates = [100 * s / n for n, s in periods]
        up = rates[1] > rates[0]
        color = BLUE if name != "Total" else ORANGE
        ax.bar(["Q1", "Q2"], rates, color=[NEUTRAL, color], width=0.5)
        for x, ((n, s), r) in enumerate(zip(periods, rates)):
            ax.text(x, r + 0.3, f"{r:.1f}%", ha="center", fontsize=15, fontweight="bold")
            ax.text(x, -1.6, f"{s}/{n:,}", ha="center", fontsize=10, color=MUTED)
        ax.set_title(f"{name}  {'▲ up' if up else '▼ down'}", color=INK_2)
        ax.yaxis.set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.set_ylim(-2.2, 19)
        ax.tick_params(axis="x", labelsize=13)
    headline(fig, "Each channel converts better. The total converts worse.",
             "Simpson's paradox: the mix moved toward Instagram, which has a lower rate. Always check the segments.")
    save(fig, "03_simpson.png")


def mean_vs_median() -> None:
    rng = np.random.default_rng(7)
    minutes = rng.lognormal(mean=1.2, sigma=1.1, size=2000)
    mean, median = minutes.mean(), np.median(minutes)
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(left=0.08, right=0.95, top=0.78, bottom=0.12)
    counts, _, _ = ax.hist(minutes[minutes < 60], bins=60, color=NEUTRAL, edgecolor=SURFACE, linewidth=1)
    ax.set_ylim(0, counts.max() * 1.2)
    for value, label, color, ha, dx in ((median, "Median", BLUE, "right", -0.6), (mean, "Mean", ORANGE, "left", 0.6)):
        ax.axvline(value, color=color, lw=2)
        ax.text(value + dx, counts.max() * 1.1, f"{label}: {value:.1f} min", color=color,
                ha=ha, fontsize=14, fontweight="bold")
    ax.set_xlabel("Response time to a customer message, minutes (cut at 60)")
    ax.yaxis.set_visible(False)
    ax.spines["left"].set_visible(False)
    share_below_mean = 100 * (minutes < mean).mean()
    headline(fig, f"Average response: {mean:.0f} minutes. Half of customers wait less than {median:.0f}.",
             f"A few very slow replies pull the mean up. {share_below_mean:.0f}% of customers get an answer faster than the 'average'.")
    save(fig, "04_mean_vs_median.png")


def seasonality() -> None:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    last_year = [80, 84, 112, 118, 96, 88]
    this_year = [86, 90, 121, 126, 101, 93]
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(left=0.08, right=0.88, top=0.78, bottom=0.12)
    ax.axvspan(1.5, 3.5, color=BLUE, alpha=0.08, lw=0)
    ax.text(2.5, 132, "Campaign (this year only)", ha="center", color=BLUE, fontsize=12)
    ax.plot(months, last_year, color=NEUTRAL, lw=2, marker="o", ms=8, mec=SURFACE, mew=2)
    ax.plot(months, this_year, color=BLUE, lw=2, marker="o", ms=8, mec=SURFACE, mew=2)
    ax.text(5.15, last_year[-1], "Last year, no campaign", va="center", color=INK_2)
    ax.text(5.15, this_year[-1], "This year", va="center", color=BLUE)
    ax.set_ylim(60, 140)
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)
    ax.set_ylabel("Sales, units")
    jump_this = 100 * (this_year[2] / this_year[1] - 1)
    jump_last = 100 * (last_year[2] / last_year[1] - 1)
    headline(fig, f"Sales jumped {jump_this:.0f}% when the campaign started. Last year they jumped {jump_last:.0f}% without one.",
             "Compare the same period a year earlier before giving the campaign the credit.")
    save(fig, "05_seasonality.png")


def main() -> None:
    percent_vs_points()
    small_samples()
    simpson()
    mean_vs_median()
    seasonality()
    print("Saved:", ", ".join(p.name for p in sorted(IMG_DIR.glob("*.png"))))


if __name__ == "__main__":
    main()
