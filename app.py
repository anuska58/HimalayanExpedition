import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, ctx


URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRhwhH25KVPdQAPyBplWFgv5W9KKvLxvu-vY33e7tKFAc3YDYEfCPxzvh0LXxJQFPxhfCDGo6Iqbu_n/pub?gid=1676311418&single=true&output=csv"
VIDEO_URL = "https://indiana-my.sharepoint.com/:v:/g/personal/anuacha_iu_edu/IQABxSkmgTDBRpdGXvsxZKZSAf3B6xJLq4bQHNad7-3Q4y0?e=3xU7ms" 

df = pd.read_csv(URL)
df.columns = df.columns.str.strip()

required_cols = [
    "season", "year", "totmembers", "termreason", "expid",
    "mdeaths", "hdeaths", "success1", "highpoint", "peakid"
]

missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    print("WARNING: Missing columns:", missing_cols)

df["season"] = df["season"].astype(str).str.strip().str.title()

numeric_cols = ["year", "totmembers", "mdeaths", "hdeaths", "success1", "highpoint"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

for col in ["peakid", "termreason", "expid"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

df = df[df["season"].isin(["Spring", "Autumn", "Winter", "Summer"])].copy()

df["team_size"] = pd.cut(
    df["totmembers"],
    bins=[0, 3, 6, 12, 25, 100000],
    labels=["1-3", "4-6", "7-12", "13-25", "26+"],
    include_lowest=True,
)

TERM_MAP = {
    "Success (main peak)": "Success",
    "Success (subpeak, foresummit)": "Success",
    "Bad weather (storms, high winds)": "Weather",
    "Bad conditions (deep snow, avalanching, falling ice, or rock)": "Conditions",
    "Illness, AMS, exhaustion, or frostbite": "Illness / AMS",
    "Accident (death or serious injury)": "Accident",
    "Route technically too difficult, lack of experience, strength, or motivation": "Route difficulty",
    "Did not attempt climb": "Did not attempt",
    "Lack (or loss) of supplies, support or equipment": "Supplies",
    "Other": "Other",
}

df["term_simple"] = df["termreason"].map(TERM_MAP).fillna("Other")


SEASON_COLORS = {
    "Spring": "#0072B2",
    "Autumn": "#E69F00",
    "Winter": "#CC79A7",
    "Summer": "#009E73",
}

DANGER_COLOR = "#D55E00"
SUCCESS_COLOR = "#009E73"
ACCENT = "#0072B2"

BG = "#F5F4F0"
CARD_BG = "#FFFFFF"
CARD_BG2 = "#F9F8F5"
BORDER = "#E4E1D9"
BORDER_HI = "#B8B0A0"
TEXT_PRI = "#1C1A16"
TEXT_SEC = "#6B6560"
TEXT_TER = "#A09890"
GOLD = "#8B6914"

FONT_BODY = "'DM Sans', 'Helvetica Neue', sans-serif"
FONT_SERIF = "'DM Serif Display', Georgia, serif"
FONT_MONO = "'JetBrains Mono', 'Courier New', monospace"

ALL_SEASONS = ["Spring", "Autumn", "Winter", "Summer"]

TERM_ORDER = [
    "Success", "Weather", "Conditions", "Illness / AMS",
    "Route difficulty", "Accident", "Supplies", "Did not attempt", "Other"
]

TERM_COLORS = {
    "Success": "#009E73",
    "Weather": "#56B4E9",
    "Conditions": "#0072B2",
    "Illness / AMS": "#E69F00",
    "Route difficulty": "#CC79A7",
    "Accident": "#D55E00",
    "Supplies": "#F0E442",
    "Did not attempt": "#6B7394",
    "Other": "#3E4660",
}

BASE_LAYOUT = dict(
    font=dict(family=FONT_BODY, color=TEXT_PRI, size=12),
    plot_bgcolor=CARD_BG,
    paper_bgcolor=CARD_BG,
    margin=dict(t=56, b=52, l=56, r=28),
)


CHART_INFO = {
    "fig-season-bar": {
        "title": "Fatality Rate by Season",
        "subtitle": "Member and hired-staff deaths per 100 expeditions",
        "insight": "Key insight: Winter has the highest fatality rate for both expedition members and hired staff.",
        "description": [
            "This chart compares fatality rates across climbing seasons for expedition members and hired staff. The rates are shown as deaths per 100 expeditions, which makes the seasons easier to compare even when the number of expeditions differs.",
            "Winter has the highest member fatality rate, at about 9.4 deaths per 100 expeditions. Spring follows at about 7.8, Autumn at about 6.5, and Summer at about 1.0. This pattern suggests that seasonal conditions play an important role in expedition risk.",
            "Hired-staff fatality rates are lower than member fatality rates in most seasons, but they follow a similar seasonal pattern. Winter again has the highest hired-staff fatality rate, which suggests that severe conditions affect both climbers and support staff.",
            "Overall, the chart shows that Winter is the most hazardous season in the filtered dataset, while Summer has the lowest fatality rate. Summer values should still be interpreted carefully because Summer expeditions are much less common.",
        ],
    },
    "fig-teamsize-dual": {
        "title": "Per-member Fatality vs. Summit Success by Team Size",
        "subtitle": "Larger teams show higher summit success and lower individual fatality rates",
        "insight": "Key insight: Larger teams have higher summit success rates, while smaller teams show higher fatality rates per member.",
        "description": [
            "This dual-axis chart compares two outcomes by team size. The bars show the fatality rate per member, while the line shows summit success rate. This makes it possible to compare safety and success at the same time.",
            "The smallest teams, with 1 to 3 members, have the highest per-member fatality rate at about 1.49%. The largest teams, with 26 or more members, have the lowest per-member fatality rate at about 0.95%.",
            "Summit success increases as team size increases. Larger teams are more likely to have guides, fixed ropes, oxygen, support staff, better logistics, and stronger rescue capacity. These resources may help explain why large teams have higher success rates and lower individual fatality rates.",
            "The result is important because larger teams often attempt higher and more difficult peaks. Even with more demanding objectives, their greater support systems appear to reduce risk at the individual level.",
        ],
    },
    "fig-timeseries": {
        "title": "Expedition Volume and Deaths Over Time",
        "subtitle": "Long-term growth in Himalayan expeditions from 1950 to 2024",
        "insight": "Key insight: Expedition volume increased sharply after the 1990s, while deaths fluctuated around major disaster years.",
        "description": [
            "This time-series chart shows how Himalayan expedition activity and member deaths changed from 1950 to 2024. The blue area shows the number of expeditions per year, while the orange bars show annual member deaths.",
            "Expedition volume increased substantially after the 1990s. This growth reflects the expansion of commercial Himalayan climbing, especially on major peaks such as Everest.",
            "Deaths do not increase smoothly with expedition volume. Instead, they fluctuate year to year, with clear spikes around major events such as the 1996 Everest disaster, the 2014 Khumbu Icefall avalanche, the 2015 Nepal earthquake, and the 2020 COVID closure.",
            "The chart suggests that absolute deaths should be interpreted alongside expedition volume. More expeditions create more exposure to risk, but improvements in equipment, forecasting, communication, and rescue infrastructure may have helped reduce fatality rates relative to activity levels.",
        ],
    },
    "fig-heatmap": {
        "title": "Risk Matrix: Season and Team Size",
        "subtitle": "Fatality risk varies by both season and team size",
        "insight": "Key insight: The highest fatality rates appear when large teams operate during high-activity climbing seasons.",
        "description": [
            "This heatmap shows member fatality rate by season and team-size category. Darker cells indicate higher fatality rates, and each cell also displays the number of expeditions in that group.",
            "The highest-risk cell is Spring expeditions with 26 or more members, with a fatality rate of about 41.0% across 78 expeditions. This suggests that large Spring expeditions may be linked to high-risk objectives, likely including major commercial climbs on very high peaks.",
            "Spring shows a clear increase in fatality rate as team size grows. Autumn follows a similar pattern, although the rates are generally lower. Winter includes some high-risk cells, but several Winter categories have small sample sizes and should be interpreted cautiously.",
            "The main takeaway is that risk is not explained by season or team size alone. The most dangerous combinations occur when large teams, difficult objectives, and challenging seasonal conditions overlap.",
        ],
    },
    "fig-termreason": {
        "title": "Expedition Outcomes by Season",
        "subtitle": "Reasons expeditions end differ across climbing seasons",
        "insight": "Key insight: Winter has the lowest success share and the largest weather-related failure component.",
        "description": [
            "This stacked bar chart shows how expedition outcomes differ by season. Each bar represents a season, and each segment shows the share of expeditions ending for a particular reason.",
            "Success is the largest category in Spring, Autumn, and Winter. Spring has the highest success share, followed closely by Autumn. Winter has a noticeably lower success share, which is consistent with more difficult weather and shorter safe climbing windows.",
            "Weather is a larger reason for termination in Winter than in the other seasons. This suggests that storms, wind, and unstable weather windows are major constraints for Winter expeditions.",
            "The chart shows that expedition outcomes are shaped by different seasonal pressures. Spring and Autumn are more favorable for success, while Winter expeditions are more often limited by weather-related barriers.",
        ],
    },
    "fig-highpoint": {
        "title": "Altitude Reached by Team Size",
        "subtitle": "Larger teams tend to reach higher elevations",
        "insight": "Key insight: Larger teams tend to operate closer to or above 8,000 meters.",
        "description": [
            "This chart compares the average and median highest altitude reached by expeditions in each team-size category. The horizontal reference line marks 8,000 meters, a commonly used threshold for extreme-altitude climbing.",
            "Small teams, with 1 to 3 members, average about 7,369 meters. Teams with 26 or more members average about 8,122 meters, placing their average highpoint above the 8,000-meter threshold.",
            "The median highpoint also increases with team size. This suggests that large expeditions are more concentrated on very high peaks, including major 8,000-meter objectives.",
            "This chart helps explain the relationship between team size and risk. Larger teams may have more resources and lower per-member fatality rates, but they also tend to operate at higher altitudes where weather, oxygen availability, and rescue limitations create greater exposure.",
        ],
    },
    "fig-boxplot": {
        "title": "Team Size Distribution by Season",
        "subtitle": "Spring has the widest range of team sizes",
        "insight": "Key insight: Spring contains the largest expedition outliers, reflecting the scale of commercial climbing.",
        "description": [
            "This box plot shows how expedition team sizes vary across seasons. Each box represents the middle 50% of expedition sizes, while individual points show outliers.",
            "Spring has the widest spread and the largest outliers, including expeditions with more than 70 members. This reflects the scale of commercial expeditions during the main Himalayan climbing season.",
            "Autumn also includes large expeditions, although the distribution is less extreme than Spring. Winter and Summer generally have smaller teams and fewer large outliers.",
            "The chart shows that seasons differ not only in risk and success rates, but also in the type of expeditions they attract. Spring is associated with larger and more commercially organized expeditions, while Winter and Summer are more specialized and smaller in scale.",
        ],
    },
}


def hex_to_rgba(hex_color, alpha=0.2):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def empty_figure(message="No data for this filter."):
    fig = go.Figure()
    fig.update_layout(
        **BASE_LAYOUT,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                text=message,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color=TEXT_SEC),
            )
        ],
    )
    return fig


def build_figures(seasons, year_range, height=360, peak_filter="all"):
    try:
        y0, y1 = year_range
        seasons = seasons or ALL_SEASONS

        flt = df[
            df["season"].isin(seasons)
            & df["year"].between(y0, y1)
        ].copy()

        if peak_filter == "everest":
            flt = flt[flt["peakid"].str.upper() == "EVER"]
        elif peak_filter == "non_everest":
            flt = flt[flt["peakid"].str.upper() != "EVER"]

        total_exped = len(flt)
        total_deaths = int(flt["mdeaths"].sum()) if total_exped else 0
        death_rate = round(total_deaths / total_exped * 100, 2) if total_exped else 0
        avg_team = round(flt["totmembers"].mean(), 1) if total_exped else 0
        success_rate = round(flt["success1"].sum() / total_exped * 100, 1) if total_exped else 0

        if flt.empty:
            figs = [empty_figure() for _ in range(7)]
            return (total_exped, total_deaths, death_rate, avg_team, success_rate), *figs

        # F1: Season bar
        sg = (
            flt.groupby("season")
            .agg(
                exped=("expid", "count"),
                mdeaths=("mdeaths", "sum"),
                hdeaths=("hdeaths", "sum"),
            )
            .reset_index()
        )

        sg["mrate"] = (sg["mdeaths"] / sg["exped"] * 100).round(2)
        sg["hrate"] = (sg["hdeaths"] / sg["exped"] * 100).round(2)
        sg = sg.sort_values("mrate", ascending=False)

        f1 = go.Figure()

        for i, row in sg.iterrows():
            season_color = SEASON_COLORS.get(row["season"], "#999999")

            f1.add_trace(
                go.Bar(
                    x=[row["season"]],
                    y=[row["mrate"]],
                    name="Member deaths" if i == 0 else "",
                    showlegend=(i == 0),
                    marker_color=season_color,
                    marker_line=dict(color="rgba(255,255,255,0.25)", width=1),
                    text=[f"{row['mrate']:.1f}%"],
                    textposition="outside",
                    textfont=dict(size=11, color=TEXT_PRI),
                    hovertemplate=(
                        f"<b>{row['season']}</b><br>"
                        f"Member fatality rate: {row['mrate']:.2f}%<br>"
                        f"Expeditions: {int(row['exped'])}"
                        "<extra></extra>"
                    ),
                    width=0.35,
                    offset=-0.2,
                )
            )

            f1.add_trace(
                go.Bar(
                    x=[row["season"]],
                    y=[row["hrate"]],
                    name="Hired-staff deaths" if i == 0 else "",
                    showlegend=(i == 0),
                    marker_color=season_color,
                    marker_opacity=0.35,
                    marker_pattern_shape="/",
                    marker_line=dict(color=season_color, width=1),
                    text=[f"{row['hrate']:.1f}%"],
                    textposition="outside",
                    textfont=dict(size=10, color=TEXT_SEC),
                    hovertemplate=(
                        f"<b>{row['season']}</b><br>"
                        f"Hired-staff fatality rate: {row['hrate']:.2f}%<br>"
                        f"Expeditions: {int(row['exped'])}"
                        "<extra></extra>"
                    ),
                    width=0.35,
                    offset=0.2,
                )
            )

        max_y_f1 = max(sg["mrate"].max(), sg["hrate"].max()) if len(sg) else 10

        f1.update_layout(
            **{**BASE_LAYOUT, "margin": dict(t=62, b=96, l=70, r=30)},
            height=height,
            barmode="overlay",
            title=dict(
                text="Fatality Rate by Season",
                font=dict(size=13, color=TEXT_PRI),
                x=0.01,
                xanchor="left",
            ),
            xaxis=dict(
                title=dict(text="Season", standoff=10),
                showgrid=False,
                linecolor=BORDER,
            ),
            yaxis=dict(
                title="Deaths / 100 expeditions",
                gridcolor=BORDER,
                gridwidth=1,
                zeroline=True,
                zerolinecolor=BORDER,
                range=[0, max_y_f1 * 1.22],
            ),
            legend=dict(
                orientation="h",
                y=-0.28,
                x=0.5,
                xanchor="center",
                font=dict(size=11),
            ),
            bargap=0.3,
        )

        # F2: Team size dual axis
        ts = (
            flt.dropna(subset=["team_size"])
            .groupby("team_size", observed=True)
            .agg(
                exped=("expid", "count"),
                deaths=("mdeaths", "sum"),
                total_members=("totmembers", "sum"),
                success=("success1", "sum"),
            )
            .reset_index()
        )

        ts["drate"] = (
            ts["deaths"] / ts["total_members"].replace(0, pd.NA) * 100
        ).fillna(0).round(3)

        ts["srate"] = (
            ts["success"] / ts["exped"].replace(0, pd.NA) * 100
        ).fillna(0).round(2)

        ts["small_n"] = ts["exped"] < 30

        f2 = make_subplots(specs=[[{"secondary_y": True}]])

        for i, row in ts.iterrows():
            label = f"{row['drate']:.3f}%"
            if row["small_n"]:
                label += " (low n)"

            f2.add_trace(
                go.Bar(
                    x=[str(row["team_size"])],
                    y=[row["drate"]],
                    name="Fatality rate per member" if i == 0 else "",
                    showlegend=(i == 0),
                    marker_color=DANGER_COLOR,
                    marker_opacity=0.45 if row["small_n"] else 0.85,
                    marker_line=dict(color="rgba(255,255,255,0.2)", width=0.5),
                    text=[label],
                    textposition="outside",
                    textfont=dict(size=10, color=DANGER_COLOR if not row["small_n"] else TEXT_TER),
                    hovertemplate=(
                        f"Team size: <b>{row['team_size']}</b><br>"
                        f"Fatality rate per member: {row['drate']:.3f}%<br>"
                        f"Expeditions: {int(row['exped'])}"
                        + ("<br>Low sample size" if row["small_n"] else "")
                        + "<extra></extra>"
                    ),
                ),
                secondary_y=False,
            )

        f2.add_trace(
            go.Scatter(
                x=ts["team_size"].astype(str),
                y=ts["srate"],
                name="Summit success rate",
                mode="lines+markers",
                line=dict(color=SUCCESS_COLOR, width=3),
                marker=dict(
                    size=10,
                    color=SUCCESS_COLOR,
                    line=dict(color=CARD_BG, width=2),
                ),
                hovertemplate="Team size: <b>%{x}</b><br>Success rate: %{y:.1f}%<extra></extra>",
            ),
            secondary_y=True,
        )

        max_y_f2 = ts["drate"].max() if len(ts) else 1

        f2.update_layout(
            **{**BASE_LAYOUT, "margin": dict(t=62, b=96, l=72, r=72)},
            height=height,
            title=dict(
                text="Per-member Fatality vs. Summit Success by Team Size",
                font=dict(size=13, color=TEXT_PRI),
                x=0.01,
                xanchor="left",
            ),
            xaxis=dict(
                title=dict(text="Team size (members)", standoff=10),
                showgrid=False,
                linecolor=BORDER,
            ),
            yaxis=dict(
                title=dict(text="Fatality rate per member (%)", font=dict(color=DANGER_COLOR)),
                gridcolor=BORDER,
                zeroline=False,
                range=[0, max_y_f2 * 1.25],
                tickfont=dict(color=DANGER_COLOR),
            ),
            yaxis2=dict(
                title=dict(text="Summit success rate (%)", font=dict(color=SUCCESS_COLOR)),
                zeroline=False,
                tickfont=dict(color=SUCCESS_COLOR),
                range=[0, 100],
            ),
            legend=dict(
                orientation="h",
                y=-0.28,
                x=0.5,
                xanchor="center",
                font=dict(size=11),
            ),
        )

        # F3: Time series
        yr = (
            flt.groupby("year")
            .agg(exped=("expid", "count"), deaths=("mdeaths", "sum"))
            .reset_index()
            .sort_values("year")
        )

        yr["deaths_roll"] = yr["deaths"].rolling(5, center=True, min_periods=1).mean()

        f3 = make_subplots(specs=[[{"secondary_y": True}]])

        f3.add_trace(
            go.Scatter(
                x=yr["year"],
                y=yr["exped"],
                name="Expeditions per year",
                mode="lines",
                fill="tozeroy",
                line=dict(color=ACCENT, width=2),
                fillcolor="rgba(86,180,233,0.08)",
                hovertemplate="<b>%{x}</b><br>Expeditions: %{y}<extra></extra>",
            ),
            secondary_y=False,
        )

        f3.add_trace(
            go.Bar(
                x=yr["year"],
                y=yr["deaths"],
                name="Deaths per year",
                marker_color=DANGER_COLOR,
                opacity=0.45,
                hovertemplate="<b>%{x}</b><br>Deaths: %{y}<extra></extra>",
            ),
            secondary_y=True,
        )

        f3.add_trace(
            go.Scatter(
                x=yr["year"],
                y=yr["deaths_roll"],
                name="5-year average deaths",
                mode="lines",
                line=dict(color=GOLD, width=2, dash="dot"),
                hovertemplate="<b>%{x}</b><br>5-year average deaths: %{y:.1f}<extra></extra>",
            ),
            secondary_y=True,
        )

        events = {
            1996: ("1996 Everest disaster", 50),
            2014: ("2014 Khumbu avalanche", -55),
            2015: ("2015 Nepal earthquake", 50),
            2020: ("COVID closure", -55),
        }

        annots = []
        for year_event, (label, ay) in events.items():
            row = yr[yr["year"] == year_event]
            if len(row):
                annots.append(
                    dict(
                        x=year_event,
                        y=row["exped"].values[0],
                        text=f"<b>{label}</b>",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor=GOLD,
                        arrowwidth=1.5,
                        ax=0,
                        ay=ay,
                        font=dict(size=9, color=GOLD),
                        bgcolor=CARD_BG2,
                        bordercolor=GOLD,
                        borderwidth=1,
                        borderpad=3,
                    )
                )

        f3.update_layout(
            **BASE_LAYOUT,
            height=height,
            title=dict(
                text="Expedition Volume and Deaths Over Time",
                font=dict(size=13, color=TEXT_PRI),
                x=0.01,
                xanchor="left",
            ),
            xaxis=dict(title="Year", showgrid=False, linecolor=BORDER),
            yaxis=dict(
                title="Expeditions per year",
                gridcolor=BORDER,
                zeroline=False,
            ),
            yaxis2=dict(
                title=dict(text="Deaths per year", font=dict(color=DANGER_COLOR)),
                zeroline=False,
                tickfont=dict(color=DANGER_COLOR),
            ),
            legend=dict(
                orientation="h",
                y=-0.22,
                x=0.5,
                xanchor="center",
                font=dict(size=11),
            ),
            annotations=annots,
        )

        # F4: Heatmap
        hm_seasons = [s for s in ["Spring", "Autumn", "Winter"] if s in seasons]
        if not hm_seasons:
            hm_seasons = ["Spring", "Autumn", "Winter"]

        sizes_hm = ["1-3", "4-6", "7-12", "13-25", "26+"]

        cross = (
            flt[flt["season"].isin(hm_seasons)]
            .dropna(subset=["team_size"])
            .groupby(["season", "team_size"], observed=True)
            .agg(exped=("expid", "count"), deaths=("mdeaths", "sum"))
            .reset_index()
        )

        cross["drate"] = (
            cross["deaths"] / cross["exped"].replace(0, pd.NA) * 100
        ).fillna(0).round(2)

        z = []
        text_z = []

        for season in hm_seasons:
            row_vals = []
            text_vals = []

            for size in sizes_hm:
                cell = cross[
                    (cross["season"] == season)
                    & (cross["team_size"].astype(str) == size)
                ]

                if len(cell):
                    val = float(cell["drate"].values[0])
                    n = int(cell["exped"].values[0])
                else:
                    val = 0
                    n = 0

                warn = " (low n)" if n < 30 else ""
                row_vals.append(val)
                text_vals.append(f"<b>{val:.1f}%</b><br>n={n}{warn}")

            z.append(row_vals)
            text_z.append(text_vals)

        f4 = go.Figure(
            go.Heatmap(
                z=z,
                x=sizes_hm,
                y=hm_seasons,
                text=text_z,
                texttemplate="%{text}",
                textfont=dict(size=10.5, family=FONT_BODY, color=TEXT_PRI),
                colorscale=[
                    [0, "#FFFFFF"],
                    [0.15, "#FDE8DC"],
                    [0.35, "#F4B896"],
                    [0.60, "#E07840"],
                    [0.80, "#C85520"],
                    [1, "#D55E00"],
                ],
                colorbar=dict(
                    title=dict(text="Death rate (%)", font=dict(size=11, color=TEXT_SEC)),
                    tickfont=dict(color=TEXT_SEC),
                    outlinecolor=BORDER,
                    outlinewidth=1,
                ),
                hovertemplate=(
                    "Season: <b>%{y}</b><br>"
                    "Team size: <b>%{x}</b><br>"
                    "Fatality rate: %{z:.2f}%<extra></extra>"
                ),
            )
        )

        f4.update_layout(
            **BASE_LAYOUT,
            height=height,
            title=dict(
                text="Risk Matrix: Season and Team Size",
                font=dict(size=13, color=TEXT_PRI),
                x=0.01,
                xanchor="left",
            ),
            xaxis=dict(title="Team size (members)", showgrid=False),
            yaxis=dict(title="Season", showgrid=False),
        )

        # F5: Termination reason
        tr = (
            flt[flt["season"].isin(hm_seasons)]
            .groupby(["season", "term_simple"])
            .size()
            .reset_index(name="count")
        )

        if tr.empty:
            f5 = empty_figure("No termination data.")
        else:
            tr_piv = (
                tr.pivot(index="season", columns="term_simple", values="count")
                .fillna(0)
            )

            tr_piv = tr_piv.div(tr_piv.sum(axis=1), axis=0).fillna(0) * 100
            tr_piv = tr_piv.reset_index()

            f5 = go.Figure()

            for term in TERM_ORDER:
                if term not in tr_piv.columns:
                    continue

                f5.add_trace(
                    go.Bar(
                        x=tr_piv["season"],
                        y=tr_piv[term],
                        name=term,
                        marker_color=TERM_COLORS.get(term, "#999999"),
                        hovertemplate=f"<b>%{{x}}</b><br>{term}: %{{y:.1f}}%<extra></extra>",
                    )
                )

            f5.update_layout(
                **{**BASE_LAYOUT, "margin": dict(t=56, b=52, l=56, r=140)},
                height=height,
                barmode="stack",
                title=dict(
                    text="Expedition Outcomes by Season",
                    font=dict(size=13, color=TEXT_PRI),
                    x=0.01,
                    xanchor="left",
                ),
                xaxis=dict(title="Season", showgrid=False),
                yaxis=dict(
                    title="Proportion (%)",
                    gridcolor=BORDER,
                    zeroline=False,
                ),
                legend=dict(
                    orientation="v",
                    x=1.02,
                    y=1,
                    font=dict(size=10),
                ),
            )

        # F6: Highpoint
        hp = (
            flt[(flt["highpoint"] > 0) & flt["team_size"].notna()]
            .groupby("team_size", observed=True)
            .agg(
                avg_hp=("highpoint", "mean"),
                med_hp=("highpoint", "median"),
                count=("highpoint", "count"),
            )
            .reset_index()
        )

        if hp.empty:
            f6 = empty_figure("No highpoint data.")
        else:
            hp_std = (
                flt[(flt["highpoint"] > 0) & flt["team_size"].notna()]
                .groupby("team_size", observed=True)["highpoint"]
                .std()
                .reset_index()
                .rename(columns={"highpoint": "std"})
            )

            hp = hp.merge(hp_std, on="team_size", how="left")
            hp["std"] = hp["std"].fillna(0)
            hp["upper"] = (hp["avg_hp"] + hp["std"]).clip(upper=8849)
            hp["lower"] = (hp["avg_hp"] - hp["std"]).clip(lower=5000)

            size_labels = hp["team_size"].astype(str).tolist()

            f6 = go.Figure()

            f6.add_trace(
                go.Scatter(
                    x=size_labels + size_labels[::-1],
                    y=hp["upper"].tolist() + hp["lower"].tolist()[::-1],
                    fill="toself",
                    fillcolor="rgba(86,180,233,0.08)",
                    line=dict(color="rgba(0,0,0,0)"),
                    hoverinfo="skip",
                    name="1 SD range",
                    showlegend=True,
                )
            )

            f6.add_trace(
                go.Bar(
                    x=size_labels,
                    y=hp["avg_hp"],
                    name="Average highpoint",
                    marker_color=ACCENT,
                    marker_opacity=0.75,
                    marker_line=dict(color="rgba(255,255,255,0.15)", width=0.5),
                    text=hp["avg_hp"].map(lambda v: f"{int(v):,} m"),
                    textposition="outside",
                    textfont=dict(size=10, color=ACCENT),
                    hovertemplate="Team size: <b>%{x}</b><br>Average: %{y:,.0f} m<extra></extra>",
                )
            )

            f6.add_trace(
                go.Scatter(
                    x=size_labels,
                    y=hp["med_hp"],
                    name="Median highpoint",
                    mode="lines+markers",
                    line=dict(color=DANGER_COLOR, width=2.5, dash="dot"),
                    marker=dict(size=8, color=DANGER_COLOR, line=dict(color="white", width=2)),
                    hovertemplate="Team size: <b>%{x}</b><br>Median: %{y:,.0f} m<extra></extra>",
                )
            )

            f6.add_hline(
                y=8000,
                line_dash="dash",
                line_color=GOLD,
                line_width=1.5,
                annotation_text="8,000 m reference line",
                annotation_position="top left",
                annotation_font=dict(size=10, color=GOLD),
            )

            f6.update_layout(
                **BASE_LAYOUT,
                height=height,
                title=dict(
                    text="Altitude Reached by Team Size",
                    font=dict(size=13, color=TEXT_PRI),
                    x=0.01,
                    xanchor="left",
                ),
                xaxis=dict(title="Team size (members)", showgrid=False),
                yaxis=dict(
                    title="Altitude (m)",
                    gridcolor=BORDER,
                    zeroline=False,
                    range=[6000, 9000],
                ),
                legend=dict(
                    orientation="h",
                    y=-0.25,
                    x=0.5,
                    xanchor="center",
                    font=dict(size=11),
                ),
            )

        # F7: Boxplot
        f7 = go.Figure()

        for season in seasons:
            sub = flt[flt["season"] == season]["totmembers"].dropna()

            if len(sub) == 0:
                continue

            season_color = SEASON_COLORS.get(season, "#888888")

            f7.add_trace(
                go.Box(
                        y=sub,
                        name=season,
                        marker_color=SEASON_COLORS[season],
                        boxmean="sd",
                        hovertemplate=f"<b>{season}</b><br>Team size: %{{y}}<extra></extra>",
            )
            )

        f7.update_layout(
            **BASE_LAYOUT,
            height=height,
            title=dict(
                text="Team Size Distribution by Season",
                font=dict(size=13, color=TEXT_PRI),
                x=0.01,
                xanchor="left",
            ),
            yaxis=dict(
                title="Members per expedition",
                gridcolor=BORDER,
                zeroline=False,
            ),
            showlegend=False,
        )

        return (total_exped, total_deaths, death_rate, avg_team, success_rate), f1, f2, f3, f4, f5, f6, f7

    except Exception as error:
        print("ERROR:", repr(error))
        figs = [empty_figure(f"Error: {error}") for _ in range(7)]
        return (0, 0, 0, 0, 0), *figs


app = Dash(
    __name__,
    title="Himalayan Expedition Risk",
    suppress_callback_exceptions=True,
)

app.index_string = """<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #F5F4F0;
    --card: #FFFFFF;
    --card2: #F9F8F5;
    --border: #E4E1D9;
    --border-hi: #B8B0A0;
    --text-pri: #1C1A16;
    --text-sec: #6B6560;
    --text-ter: #A09890;
    --accent: #0072B2;
    --danger: #D55E00;
    --success: #009E73;
    --gold: #8B6914;
  }

  html { scroll-behavior: smooth; }

  body {
    background: var(--bg);
    font-family: 'DM Sans', 'Helvetica Neue', sans-serif;
    color: var(--text-pri);
    -webkit-font-smoothing: antialiased;
  }

  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 3px; }

  .chart-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 4px 8px;
    cursor: pointer;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    position: relative;
    overflow: hidden;
  }

  .chart-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(0,114,178,0.02) 0%, transparent 60%);
    pointer-events: none;
  }

  .chart-card:hover {
    border-color: var(--accent);
    box-shadow: 0 4px 20px rgba(0,114,178,0.12), 0 1px 4px rgba(0,0,0,0.06);
    transform: translateY(-1px);
  }

  .chart-card:hover::after {
    content: 'Expand';
    position: absolute;
    top: 10px;
    right: 12px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: var(--accent);
    background: rgba(0,114,178,0.08);
    border: 1px solid rgba(0,114,178,0.25);
    border-radius: 4px;
    padding: 2px 7px;
  }

  .kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  .kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .kpi-card:hover {
    border-color: var(--border-hi);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }

  .kpi-card:hover::before { opacity: 1; }

  .section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-ter);
    margin: 24px 0 10px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }

  .filter-bar {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 16px;
  }

  #btn-back {
    background: white;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-sec);
    cursor: pointer;
    transition: all 0.15s ease;
    letter-spacing: 0.02em;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }

  #btn-back:hover {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
  }

  .insight-banner {
    background: linear-gradient(135deg, rgba(139,105,20,0.08), rgba(139,105,20,0.04));
    border: 1px solid rgba(139,105,20,0.25);
    border-left: 3px solid var(--gold);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 13px;
    color: var(--gold);
    font-weight: 500;
  }

  .detail-desc-body {
    font-size: 14px;
    line-height: 1.85;
    color: var(--text-sec);
    margin: 0 0 14px;
  }

  .detail-desc-body:last-child { margin-bottom: 0; }

  .dash-checklist label,
  .dash-radioitems label {
    font-size: 13px;
    color: var(--text-sec);
    cursor: pointer;
  }

  .dash-checklist input,
  .dash-radioitems input {
    cursor: pointer;
  }

  .rc-slider-rail { background: var(--border) !important; }
  .rc-slider-track { background: var(--accent) !important; }

  .rc-slider-handle {
    border-color: var(--accent) !important;
    background: var(--card) !important;
  }

  .dash-radioitems label span {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    transition: background 0.15s;
  }

  .finding-item {
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
    line-height: 1.65;
  }

  .finding-item:last-child { border-bottom: none; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .chart-card { animation: fadeUp 0.35s ease both; }

  @media (max-width: 900px) {
    .responsive-grid-2 {
      grid-template-columns: 1fr !important;
    }

    .responsive-kpi-grid {
      grid-template-columns: repeat(2, 1fr) !important;
    }
  }

  @media (max-width: 600px) {
    .responsive-kpi-grid {
      grid-template-columns: 1fr !important;
    }
  }
</style>
</head>
<body>{%app_entry%}{%config%}{%scripts%}{%renderer%}</body>
</html>"""


WRAP = {
    "maxWidth": "1240px",
    "margin": "0 auto",
    "padding": "28px 20px 60px",
}


def kpi_card(label, val, note, color=None):
    val_color = color or TEXT_PRI

    return html.Div(
        className="kpi-card",
        children=[
            html.Div(
                label,
                style={
                    "fontSize": "10px",
                    "fontWeight": "700",
                    "letterSpacing": "0.1em",
                    "textTransform": "uppercase",
                    "color": TEXT_TER,
                },
            ),
            html.Div(
                val,
                style={
                    "fontSize": "28px",
                    "fontWeight": "600",
                    "color": val_color,
                    "lineHeight": "1.1",
                    "marginTop": "4px",
                    "fontVariantNumeric": "tabular-nums",
                },
            ),
            html.Div(
                note,
                style={
                    "fontSize": "11px",
                    "color": TEXT_TER,
                    "marginTop": "3px",
                },
            ),
        ],
    )


def section_label(text):
    return html.Div(text, className="section-label")


def chart_card(graph_id, delay=0):
    return html.Div(
        dcc.Graph(
            id=graph_id,
            config={"displayModeBar": False},
            style={"height": "360px"},
        ),
        id=f"card-{graph_id}",
        n_clicks=0,
        className="chart-card",
        style={"animationDelay": f"{delay}ms"},
    )


def make_filter_bar():
    return html.Div(
        className="filter-bar",
        children=[
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "Season",
                                style={
                                    "fontSize": "10px",
                                    "fontWeight": "700",
                                    "letterSpacing": "0.1em",
                                    "textTransform": "uppercase",
                                    "color": TEXT_TER,
                                    "marginRight": "10px",
                                },
                            ),
                            dcc.Checklist(
                                id="season-filter",
                                options=[
                                    {
                                        "label": html.Span(
                                            season,
                                            style={
                                                "color": SEASON_COLORS[season],
                                                "fontWeight": "600",
                                                "fontSize": "13px",
                                                "padding": "2px 8px",
                                                "borderRadius": "4px",
                                                "border": f"1px solid {SEASON_COLORS[season]}33",
                                                "background": f"{SEASON_COLORS[season]}11",
                                            },
                                        ),
                                        "value": season,
                                    }
                                    for season in ALL_SEASONS
                                ],
                                value=ALL_SEASONS,
                                inline=True,
                                inputStyle={
                                    "marginRight": "5px",
                                    "marginLeft": "10px",
                                    "cursor": "pointer",
                                    "accentColor": ACCENT,
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "marginBottom": "10px",
                            "flexWrap": "wrap",
                        },
                    ),

                    html.Div(
                        style={
                            "width": "100%",
                            "height": "1px",
                            "background": BORDER,
                            "margin": "8px 0",
                        }
                    ),

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "Peak",
                                        style={
                                            "fontSize": "10px",
                                            "fontWeight": "700",
                                            "letterSpacing": "0.1em",
                                            "textTransform": "uppercase",
                                            "color": TEXT_TER,
                                            "marginRight": "10px",
                                        },
                                    ),
                                    dcc.RadioItems(
                                        id="peak-filter",
                                        options=[
                                            {
                                                "label": html.Span(
                                                    "All peaks",
                                                    style={"fontSize": "12px"},
                                                ),
                                                "value": "all",
                                            },
                                            {
                                                "label": html.Span(
                                                    "Everest only",
                                                    style={
                                                        "fontSize": "12px",
                                                        "color": DANGER_COLOR,
                                                        "fontWeight": "600",
                                                    },
                                                ),
                                                "value": "everest",
                                            },
                                            {
                                                "label": html.Span(
                                                    "Non-Everest",
                                                    style={
                                                        "fontSize": "12px",
                                                        "color": ACCENT,
                                                        "fontWeight": "600",
                                                    },
                                                ),
                                                "value": "non_everest",
                                            },
                                        ],
                                        value="all",
                                        inline=True,
                                        inputStyle={
                                            "marginRight": "4px",
                                            "marginLeft": "14px",
                                            "cursor": "pointer",
                                            "accentColor": ACCENT,
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "flex": "0 0 auto",
                                    "flexWrap": "wrap",
                                },
                            ),

                            html.Div(
                                style={
                                    "width": "1px",
                                    "height": "24px",
                                    "background": BORDER,
                                    "margin": "0 16px",
                                    "flexShrink": "0",
                                }
                            ),

                            html.Div(
                                [
                                    html.Span(
                                        "Year range",
                                        style={
                                            "fontSize": "10px",
                                            "fontWeight": "700",
                                            "letterSpacing": "0.1em",
                                            "textTransform": "uppercase",
                                            "color": TEXT_TER,
                                            "marginRight": "14px",
                                            "whiteSpace": "nowrap",
                                            "flexShrink": "0",
                                        },
                                    ),
                                    html.Div(
                                        dcc.RangeSlider(
                                            id="year-filter",
                                            min=1950,
                                            max=2024,
                                            step=1,
                                            value=[1950, 2024],
                                            marks={
                                                year: {
                                                    "label": str(year),
                                                    "style": {
                                                        "fontSize": "9px",
                                                        "color": TEXT_TER,
                                                    },
                                                }
                                                for year in range(1950, 2025, 10)
                                            },
                                            tooltip={
                                                "placement": "bottom",
                                                "always_visible": False,
                                            },
                                        ),
                                        style={
                                            "flex": "1",
                                            "minWidth": "200px",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "flex": "1",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "flexWrap": "wrap",
                            "gap": "8px",
                        },
                    ),
                ]
            )
        ],
    )


app.layout = html.Div(
    style={
        "fontFamily": FONT_BODY,
        "color": TEXT_PRI,
        "background": BG,
        "minHeight": "100vh",
    },
    children=[
        dcc.Store(id="active-chart", data=None),

        html.Div(
            id="shared-header",
            style={
                "maxWidth": "1240px",
                "margin": "0 auto",
                "padding": "40px 20px 0",
            },
            children=[
                html.Div(
                    [
                        html.Div(
                            "Interactive Risk Dashboard",
                            style={
                                "fontSize": "11px",
                                "fontWeight": "700",
                                "letterSpacing": "0.16em",
                                "textTransform": "uppercase",
                                "color": GOLD,
                                "textAlign": "center",
                                "marginBottom": "8px",
                            },
                        ),
                        html.H1(
                            "Himalayan Expedition Risk",
                            style={
                                "fontFamily": FONT_SERIF,
                                "fontSize": "54px",
                                "fontWeight": "400",
                                "color": "#5E3023",
                                "letterSpacing": "-0.02em",
                                "lineHeight": "1.05",
                                "margin": "0 0 12px",
                                "textAlign": "center",
                            },
                        ),
                        html.P(
                            "1950 to 2024 · 11,000+ expeditions · The Himalayan Database · Anuska Acharya",
                            style={
                                "fontSize": "14px",
                                "color": TEXT_TER,
                                "textAlign": "center",
                                "letterSpacing": "0.04em",
                                "margin": "0 0 8px",
                            },
                        ),
                       
                    ],
                    style={
                        "textAlign": "center",
                        "marginBottom": "24px",
                    },
                ),

                make_filter_bar(),

                html.Div(
                    id="kpi-row",
                    className="responsive-kpi-grid",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(5, 1fr)",
                        "gap": "10px",
                        "marginBottom": "4px",
                    },
                ),
            ],
        ),

        html.Div(
            id="screen-overview",
            style={
                "maxWidth": "1240px",
                "margin": "0 auto",
                "padding": "8px 20px 60px",
            },
            children=[
                section_label("Season and Team Size Risk"),
                html.Div(
                    [
                        chart_card("fig-season-bar", delay=0),
                        chart_card("fig-teamsize-dual", delay=60),
                    ],
                    className="responsive-grid-2",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1fr 1fr",
                        "gap": "12px",
                        "marginBottom": "12px",
                    },
                ),

                section_label("Expedition Activity Over Time"),
                html.Div(
                    chart_card("fig-timeseries", delay=120),
                    style={"marginBottom": "12px"},
                ),

                section_label("Risk Breakdown"),
                html.Div(
                    [
                        chart_card("fig-heatmap", delay=180),
                        chart_card("fig-termreason", delay=240),
                    ],
                    className="responsive-grid-2",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1fr 1fr",
                        "gap": "12px",
                        "marginBottom": "12px",
                    },
                ),

                section_label("Team Size Deep Dive"),
                html.Div(
                    [
                        chart_card("fig-highpoint", delay=300),
                        chart_card("fig-boxplot", delay=360),
                    ],
                    className="responsive-grid-2",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1fr 1fr",
                        "gap": "12px",
                        "marginBottom": "24px",
                    },
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "Key Findings",
                                    style={
                                        "fontSize": "11px",
                                        "fontWeight": "700",
                                        "letterSpacing": "0.1em",
                                        "textTransform": "uppercase",
                                        "color": TEXT_SEC,
                                    },
                                ),
                            ],
                            style={
                                "marginBottom": "16px",
                                "paddingBottom": "12px",
                                "borderBottom": f"1px solid {BORDER}",
                            },
                        ),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span(
                                                    "Winter has the highest seasonal risk. ",
                                                    style={
                                                        "fontWeight": "600",
                                                        "color": SEASON_COLORS["Winter"],
                                                    },
                                                ),
                                                html.Span(
                                                    "The Winter fatality rate is substantially higher than Summer, showing the importance of seasonal conditions.",
                                                    style={"color": TEXT_SEC},
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="finding-item",
                                ),

                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span(
                                                    "Large teams have lower individual fatality rates. ",
                                                    style={
                                                        "fontWeight": "600",
                                                        "color": SUCCESS_COLOR,
                                                    },
                                                ),
                                                html.Span(
                                                    "Support systems such as fixed ropes, guides, oxygen, and rescue capacity may reduce per-member risk.",
                                                    style={"color": TEXT_SEC},
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="finding-item",
                                ),

                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span(
                                                    "Altitude helps explain the team-size pattern. ",
                                                    style={
                                                        "fontWeight": "600",
                                                        "color": GOLD,
                                                    },
                                                ),
                                                html.Span(
                                                    "Larger teams tend to reach higher elevations, often near or above 8,000 meters.",
                                                    style={"color": TEXT_SEC},
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="finding-item",
                                ),

                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span(
                                                    "Expedition volume increased sharply after the 1990s. ",
                                                    style={
                                                        "fontWeight": "600",
                                                        "color": ACCENT,
                                                    },
                                                ),
                                                html.Span(
                                                    "Deaths fluctuate around major disaster years, so activity levels and event context should be interpreted together.",
                                                    style={"color": TEXT_SEC},
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="finding-item",
                                ),
                            ]
                        ),
                    ],
                    style={
                        "background": CARD_BG2,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "20px 24px",
                    },
                ),
                html.Div(
    [
        html.Div(
            [
                html.Span(
                    "Video Presentation",
                    style={
                        "fontSize": "11px",
                        "fontWeight": "700",
                        "letterSpacing": "0.1em",
                        "textTransform": "uppercase",
                        "color": TEXT_SEC,
                    },
                ),
            ],
            style={
                "marginBottom": "14px",
                "paddingBottom": "12px",
                "borderBottom": f"1px solid {BORDER}",
            },
        ),

                html.P(
                    "Watch the recorded walkthrough for a guided explanation of the dashboard, design choices, and key insights.",
                    style={
                        "fontSize": "13px",
                        "color": TEXT_SEC,
                        "lineHeight": "1.6",
                        "margin": "0 0 14px",
                    },
                ),

                html.A(
                    "Open Walkthrough Video",
                    href=VIDEO_URL,
                    target="_blank",
                    style={
                        "display": "inline-block",
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "color": "#FFFFFF",
                        "background": "#5E3023",
                        "padding": "9px 16px",
                        "borderRadius": "6px",
                        "textDecoration": "none",
                        "letterSpacing": "0.03em",
                    },
                ),
            ],
            style={
                "background": CARD_BG2,
                "border": f"1px solid {BORDER}",
                "borderRadius": "12px",
                "padding": "20px 24px",
                "marginTop": "18px",
            },
        ),
            ],
        ),

        html.Div(
            id="screen-detail",
            style={
                "display": "none",
                "maxWidth": "1240px",
                "margin": "0 auto",
                "padding": "8px 20px 60px",
            },
            children=[
                html.Div(
                    [
                        html.Button("Back to Dashboard", id="btn-back"),
                        html.Span(
                            id="detail-breadcrumb",
                            style={
                                "fontSize": "12px",
                                "color": TEXT_TER,
                                "marginLeft": "14px",
                            },
                        ),
                    ],
                    style={
                        "marginBottom": "16px",
                        "display": "flex",
                        "alignItems": "center",
                    },
                ),

                html.Div(
                    id="detail-insight",
                    className="insight-banner",
                    style={"display": "none"},
                ),

                html.Div(
                    id="detail-chart-wrap",
                    style={
                        "background": CARD_BG,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "8px 12px",
                        "marginBottom": "16px",
                    },
                ),

                html.Div(
                    id="detail-description",
                    style={
                        "background": CARD_BG,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "28px 32px",
                    },
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("active-chart", "data"),
    Output("screen-overview", "style"),
    Output("screen-detail", "style"),
    Input("card-fig-season-bar", "n_clicks"),
    Input("card-fig-teamsize-dual", "n_clicks"),
    Input("card-fig-timeseries", "n_clicks"),
    Input("card-fig-heatmap", "n_clicks"),
    Input("card-fig-termreason", "n_clicks"),
    Input("card-fig-highpoint", "n_clicks"),
    Input("card-fig-boxplot", "n_clicks"),
    Input("btn-back", "n_clicks"),
    State("active-chart", "data"),
    prevent_initial_call=True,
)
def toggle_screen(*_):
    triggered = ctx.triggered_id

    if triggered == "btn-back" or triggered is None:
        return None, WRAP, {"display": "none"}

    chart_id = triggered.replace("card-", "")
    return chart_id, {"display": "none"}, WRAP


@app.callback(
    Output("kpi-row", "children"),
    Output("fig-season-bar", "figure"),
    Output("fig-teamsize-dual", "figure"),
    Output("fig-timeseries", "figure"),
    Output("fig-heatmap", "figure"),
    Output("fig-termreason", "figure"),
    Output("fig-highpoint", "figure"),
    Output("fig-boxplot", "figure"),
    Input("season-filter", "value"),
    Input("year-filter", "value"),
    Input("peak-filter", "value"),
)
def update_overview(seasons, year_range, peak_filter):
    seasons = seasons or ALL_SEASONS
    year_range = year_range or [1950, 2024]
    peak_filter = peak_filter or "all"

    (te, td, dr, at, sr), f1, f2, f3, f4, f5, f6, f7 = build_figures(
        seasons,
        year_range,
        height=360,
        peak_filter=peak_filter,
    )

    peak_label = {
        "all": "all peaks",
        "everest": "Everest only",
        "non_everest": "non-Everest",
    }.get(peak_filter, "all peaks")

    kpis = [
        kpi_card("Expeditions", f"{te:,}", f"{year_range[0]} to {year_range[1]} · {peak_label}"),
        kpi_card("Member Deaths", f"{td:,}", "filtered selection", DANGER_COLOR),
        kpi_card("Death Rate", f"{dr:.2f}%", "per expedition", DANGER_COLOR),
        kpi_card("Avg Team Size", f"{at}", "members per expedition"),
        kpi_card("Success Rate", f"{sr:.1f}%", "summit achieved", SUCCESS_COLOR),
    ]

    return kpis, f1, f2, f3, f4, f5, f6, f7


@app.callback(
    Output("detail-breadcrumb", "children"),
    Output("detail-insight", "children"),
    Output("detail-insight", "style"),
    Output("detail-chart-wrap", "children"),
    Output("detail-description", "children"),
    Input("active-chart", "data"),
    Input("season-filter", "value"),
    Input("year-filter", "value"),
    Input("peak-filter", "value"),
)
def update_detail(active_chart, seasons, year_range, peak_filter):
    hidden_style = {"display": "none"}

    if not active_chart:
        return "", "", hidden_style, [], []

    seasons = seasons or ALL_SEASONS
    year_range = year_range or [1950, 2024]
    peak_filter = peak_filter or "all"

    info = CHART_INFO.get(active_chart, {})

    (te, td, dr, at, sr), f1, f2, f3, f4, f5, f6, f7 = build_figures(
        seasons,
        year_range,
        height=540,
        peak_filter=peak_filter,
    )

    fig_map = {
        "fig-season-bar": f1,
        "fig-teamsize-dual": f2,
        "fig-timeseries": f3,
        "fig-heatmap": f4,
        "fig-termreason": f5,
        "fig-highpoint": f6,
        "fig-boxplot": f7,
    }

    big_fig = fig_map.get(active_chart, f1)
    breadcrumb = f"Dashboard > {info.get('title', active_chart)}"

    chart_section = dcc.Graph(
        figure=big_fig,
        config={
            "displayModeBar": True,
            "scrollZoom": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        },
        style={"height": "540px"},
    )

    insight_text = info.get("insight", "")
    insight_style = {
        "display": "block",
        "background": "linear-gradient(135deg, rgba(139,105,20,0.08), rgba(139,105,20,0.04))",
        "border": "1px solid rgba(139,105,20,0.25)",
        "borderLeft": "3px solid #8B6914",
        "borderRadius": "0 8px 8px 0",
        "padding": "12px 16px",
        "marginBottom": "16px",
        "fontSize": "13px",
        "color": GOLD,
        "fontWeight": "500",
    } if insight_text else hidden_style

    description = html.Div(
        [
            html.H2(
                info.get("title", ""),
                style={
                    "fontFamily": FONT_SERIF,
                    "fontSize": "22px",
                    "fontWeight": "400",
                    "color": TEXT_PRI,
                    "margin": "0 0 6px",
                },
            ),
            html.P(
                info.get("subtitle", ""),
                style={
                    "fontSize": "13px",
                    "color": TEXT_SEC,
                    "margin": "0 0 20px",
                    "paddingBottom": "18px",
                    "borderBottom": f"1px solid {BORDER}",
                },
            ),
            *[
                html.P(paragraph, className="detail-desc-body")
                for paragraph in info.get("description", [])
            ],
        ]
    )

    return breadcrumb, insight_text, insight_style, chart_section, description


server = app.server


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)