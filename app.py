import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, ctx

# ── Load & prepare ───────────────────────────────────────────
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRhwhH25KVPdQAPyBplWFgv5W9KKvLxvu-vY33e7tKFAc3YDYEfCPxzvh0LXxJQFPxhfCDGo6Iqbu_n/pub?gid=1676311418&single=true&output=csv"
df = pd.read_csv(url)
df = df[df["season"].isin(["Spring", "Autumn", "Winter", "Summer"])]
df["team_size"] = pd.cut(
    df["totmembers"],
    bins=[0, 3, 6, 12, 25, 100],
    labels=["1–3", "4–6", "7–12", "13–25", "26+"],
)
TERM_MAP = {
    "Success (main peak)":            "Success",
    "Success (subpeak, foresummit)":  "Success",
    "Bad weather (storms, high winds)":                                            "Weather",
    "Bad conditions (deep snow, avalanching, falling ice, or rock)":               "Conditions",
    "Illness, AMS, exhaustion, or frostbite":                                      "Illness / AMS",
    "Accident (death or serious injury)":                                          "Accident",
    "Route technically too difficult, lack of experience, strength, or motivation":"Route difficulty",
    "Did not attempt climb":           "Did not attempt",
    "Lack (or loss) of supplies, support or equipment": "Supplies",
    "Other": "Other",
}
df["term_simple"] = df["termreason"].map(TERM_MAP).fillna("Other")

# ── Design tokens (Okabe-Ito colorblind-safe palette) ────────
SEASON_COLORS = {"Spring": "#0072B2", "Autumn": "#E69F00", "Winter": "#CC79A7", "Summer": "#009E73"}
DANGER_COLOR  = "#D55E00"
SUCCESS_COLOR = "#009E73"
ACCENT        = "#56B4E9"
BG            = "#FAFAF8"
CARD_BG       = "#FFFFFF"
BORDER        = "#E8E7E0"
TEXT_PRI      = "#2C2C2A"
TEXT_SEC      = "#73726C"
TEXT_TER      = "#9C9A92"
FONT          = "Inter, Arial, sans-serif"
ALL_SEASONS   = ["Spring", "Autumn", "Winter", "Summer"]
TERM_ORDER    = ["Success", "Weather", "Conditions", "Illness / AMS",
                 "Route difficulty", "Accident", "Supplies", "Did not attempt", "Other"]
TERM_COLORS   = {
    "Success": "#009E73", "Weather": "#56B4E9", "Conditions": "#0072B2",
    "Illness / AMS": "#E69F00", "Route difficulty": "#CC79A7", "Accident": "#D55E00",
    "Supplies": "#F0E442", "Did not attempt": "#999999", "Other": "#BBBBBB",
}
BASE = dict(
    font=dict(family=FONT, color=TEXT_PRI, size=12),
    plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG,
    margin=dict(t=52, b=48, l=52, r=24),
)

# ── Chart descriptions ────────────────────────────────────────
CHART_INFO = {
    "fig-season-bar": {
        "title": "Death Rate by Season",
        "subtitle": "Member vs. hired-staff fatality rates across climbing seasons",
        "description": [
            "This grouped bar chart compares how dangerous each climbing season is for two groups: "
            "expedition members (the climbers themselves) and hired staff (high-altitude porters and guides). "
            "The y-axis shows deaths per 100 expeditions, making different-sized seasons directly comparable.",
            "Winter stands out as the deadliest season for members, with roughly 9.4 deaths per 100 expeditions — "
            "nearly 50% higher than Autumn (6.5) and well above Spring (7.9). This reflects the extreme cold, "
            "high winds, and near-zero visibility that define Himalayan winters. Very few teams attempt winter "
            "ascents, and those that do tend to be elite alpinists pushing the limits of survivability.",
            "Hired-staff deaths follow a different pattern: Summer shows a disproportionately high hired-staff "
            "rate relative to member risk. This likely reflects the role of porters and logistics staff operating "
            "in monsoon conditions during the small number of Summer expeditions.",
            "Design note: The hatched pattern on hired-staff bars encodes a secondary data dimension "
            "(staff type) without adding a separate color — keeping the season color as the primary channel. "
            "The Okabe-Ito palette used here is fully colorblind-safe.",
        ],
    },
    "fig-teamsize-dual": {
        "title": "Death Rate vs. Summit Success Rate by Team Size",
        "subtitle": "The core trade-off: bigger teams summit more, but die more",
        "description": [
            "This dual-axis chart reveals the central tension in Himalayan mountaineering. The red bars show "
            "member death rate (left axis) and the green line shows summit success rate (right axis), both "
            "plotted against five team size buckets from 1-3 members up to 26+.",
            "The death rate increases dramatically with team size — from 2.8% for the smallest teams to over "
            "32% for the largest. Yet the success rate also climbs, from 48% for solo/tiny teams to nearly 79% "
            "for expeditions with 26 or more members. This means large teams are not simply reckless: they are "
            "achieving more summits, but at a far higher human cost.",
            "One likely explanation is peak selection. Large teams tend to attempt high-profile, technically "
            "demanding peaks like Everest under commercial conditions. The very routes that guarantee a summit "
            "for large groups — crowded fixed ropes, heavily trafficked corridors — also concentrate risk through "
            "bottlenecking, slower turnaround times, and exposure to objective hazards like seracs and icefalls.",
            "Design note: Two separate y-axes are used so neither metric distorts the other's scale. "
            "The opposing colors (vermillion for danger, green for success) create immediate semantic contrast "
            "that guides interpretation without requiring a legend lookup.",
        ],
    },
    "fig-timeseries": {
        "title": "Expedition Volume & Deaths Over Time",
        "subtitle": "120 years of Himalayan climbing history in one chart",
        "description": [
            "This combination chart overlays expedition volume (blue filled area, left axis) with annual "
            "member deaths (red bars, right axis) from 1905 to 2024. The dual-axis design lets both series "
            "remain readable despite being on very different scales.",
            "The most striking feature is the exponential growth in expedition volume since the 1990s, driven "
            "largely by the commercialization of Everest and other 8,000-meter peaks. Annual expedition counts "
            "roughly tripled between the 1980s and 2010s. Absolute deaths also rose over this period, though "
            "the death rate per expedition has actually declined — meaning safety has improved even as volume soared.",
            "Key annotated events include the 1996 Everest disaster (a spike in deaths during a moderate-volume "
            "year), the 2014 Khumbu Icefall avalanche that killed 16 Sherpas, the 2015 Nepal earthquake "
            "that wiped out an entire climbing season, and the 2020 COVID-19 closure that brought expedition "
            "counts to near zero for the first time in decades.",
            "Design note: Annotations are placed with arrowheads pointing to the exact year of each event, "
            "anchored with white backgrounds so they remain legible over the chart's area fill. "
            "The fill opacity (10%) is kept low to avoid overwhelming the death-count bars beneath.",
        ],
    },
    "fig-heatmap": {
        "title": "Death Rate Heatmap: Season x Team Size",
        "subtitle": "Which combination of season and team size is most dangerous?",
        "description": [
            "This heatmap encodes member death rate using a sequential white-to-dark-red color scale, "
            "with season on the y-axis and team size on the x-axis. Each cell also displays the exact rate "
            "and sample size (n), allowing viewers to assess both the magnitude and the statistical reliability "
            "of each combination.",
            "The most dangerous combination is Spring expeditions with 26 or more members, which shows a "
            "death rate well above 40%. This cell corresponds almost entirely to commercial Everest expeditions "
            "during peak season — large guided teams ascending fixed ropes through the Khumbu Icefall, "
            "a notoriously hazardous corridor.",
            "Winter with large teams is the second-highest risk combination, but the small sample size "
            "(n is very low in Winter cells) means those estimates should be interpreted cautiously. "
            "Autumn generally shows lower rates than Spring across all team sizes, possibly because "
            "post-monsoon conditions offer better visibility and more stable weather windows.",
            "Design note: The sequential single-hue color scale (white to dark red) is appropriate here because "
            "death rate is a unidirectional quantity — there is no meaningful 'negative' end. "
            "A diverging scale would imply a neutral midpoint, which would be misleading for a risk metric.",
        ],
    },
    "fig-termreason": {
        "title": "Expedition Outcome by Season",
        "subtitle": "Why do expeditions end? A breakdown by termination reason",
        "description": [
            "This 100% stacked bar chart shows the proportional breakdown of how expeditions ended across "
            "three seasons. Each color segment represents a different termination category, from successful "
            "summits (green) down through weather, conditions, illness, route difficulty, and accidents. "
            "The stacked-to-100% design makes cross-season proportions directly comparable regardless of "
            "the absolute number of expeditions per season.",
            "Spring and Autumn both achieve summit success roughly 57-59% of the time, while Winter "
            "success drops to around 44% — consistent with the harsher conditions. "
            "Weather-related terminations are notably higher in Winter (23%) compared to Spring (12%), "
            "while Conditions (deep snow, avalanche, ice) account for a larger share of Autumn failures "
            "than Spring, possibly reflecting post-monsoon snowpack instability.",
            "The Accident slice is small across all seasons but consistently present, and its share "
            "in Winter — though small — represents a high absolute risk given how few expeditions attempt "
            "that season. The 'Other' category is larger in Spring, likely reflecting the complex logistics "
            "and bureaucratic factors that can derail commercial expeditions.",
            "Design note: Each category uses a distinct Okabe-Ito or complementary color, ordered from "
            "most positive (success, green) to most severe (accident, vermillion). The legend is placed "
            "vertically outside the chart area to avoid obscuring the bars.",
        ],
    },
    "fig-highpoint": {
        "title": "Average Highpoint Reached by Team Size",
        "subtitle": "Larger teams climb higher — and deeper into the death zone",
        "description": [
            "This chart shows the average (bars) and median (dotted line) highest altitude reached "
            "by expeditions of each team size, with a reference line marking the 8,000 m 'death zone' — "
            "the altitude above which the human body cannot acclimatize and begins to deteriorate irreversibly.",
            "There is a clear monotonic relationship: larger teams reach higher altitudes on average. "
            "Small teams (1-3 members) average around 7,100-7,300 m, while teams of 26+ average above "
            "8,400 m. This explains much of the death rate difference seen in the team size charts — "
            "larger teams are operating in more extreme altitude environments where the margin for error is minimal.",
            "The gap between the average and median lines is also informative. For large teams, the two "
            "lines converge, suggesting a tight cluster of expeditions targeting a small number of very "
            "high peaks (primarily Everest at 8,849 m). For smaller teams, the larger gap indicates more "
            "diverse peak selection, from trekking peaks under 6,000 m to serious technical objectives.",
            "Design note: The 8,000 m death zone reference line provides a meaningful real-world anchor "
            "that guides interpretation without requiring the viewer to know altitude values from memory. "
            "The y-axis starts at 6,000 m rather than zero — a deliberate choice to avoid wasting chart "
            "space on altitudes no expedition in this dataset approaches.",
        ],
    },
    "fig-boxplot": {
        "title": "Team Size Distribution by Season",
        "subtitle": "How team sizes vary across climbing seasons",
        "description": [
            "This box plot shows the distribution of total expedition size (members) for each season. "
            "The box spans the interquartile range (25th to 75th percentile), the horizontal line marks "
            "the median, the whiskers extend to 1.5x IQR, and the dashed line shows +/-1 standard deviation. "
            "Outliers beyond the whiskers appear as individual dots.",
            "Spring has by far the widest spread and highest median team size. This reflects the diversity "
            "of Spring expeditions: from solo alpinists on technical routes to 50-person commercial Everest "
            "teams. The long upper tail of outliers in Spring tells the story of large guided expeditions "
            "that have become common since the 1990s.",
            "Autumn shows a slightly smaller median and tighter spread — most Autumn expeditions are "
            "smaller, more independent teams attempting peaks after the monsoon. Winter has the smallest "
            "median and fewest outliers, consistent with the elite, minimal-footprint style that winter "
            "climbing demands. Summer is the rarest season with fewest expeditions and moderate team sizes.",
            "Design note: Box plots are chosen over simple bar charts here because the shape of the "
            "distribution — not just the average — is the key insight. Season color is used consistently "
            "with all other charts in the dashboard, so viewers can instantly connect this chart to the "
            "season-based patterns shown elsewhere.",
        ],
    },
}


# ── Build all 7 figures ───────────────────────────────────────
def build_figures(seasons, year_range, height=320, peak_filter="all"):
    y0, y1 = year_range
    flt = df[df["season"].isin(seasons) & df["year"].between(y0, y1)]
    if peak_filter == "everest":
        flt = flt[flt["peakid"] == "EVER"]
    elif peak_filter == "non_everest":
        flt = flt[flt["peakid"] != "EVER"]

    total_exped  = len(flt)
    total_deaths = int(flt["mdeaths"].sum())
    death_rate   = round(total_deaths / total_exped * 100, 1) if total_exped else 0
    avg_team     = round(flt["totmembers"].mean(), 1) if total_exped else 0

    # Fig 1 — death rate by season
    sg = (flt.groupby("season")
          .agg(exped=("expid","count"), mdeaths=("mdeaths","sum"), hdeaths=("hdeaths","sum"))
          .reset_index())
    sg["mrate"] = (sg["mdeaths"] / sg["exped"] * 100).round(2)
    sg["hrate"] = (sg["hdeaths"] / sg["exped"] * 100).round(2)
    sg = sg.sort_values("mrate", ascending=False)
    f1 = go.Figure()
    f1.add_trace(go.Bar(x=sg["season"], y=sg["mrate"], name="Member deaths",
        marker_color=[SEASON_COLORS.get(s,"#aaa") for s in sg["season"]],
        text=sg["mrate"].map(lambda v: f"{v:.1f}%"), textposition="outside",
        hovertemplate="<b>%{x}</b><br>Member death rate: %{y:.2f}%<extra></extra>"))
    f1.add_trace(go.Bar(x=sg["season"], y=sg["hrate"], name="Hired-staff deaths",
        marker_color=[SEASON_COLORS.get(s,"#aaa") for s in sg["season"]],
        marker_pattern_shape="/", opacity=0.55,
        text=sg["hrate"].map(lambda v: f"{v:.1f}%"), textposition="outside",
        hovertemplate="<b>%{x}</b><br>Hired-staff death rate: %{y:.2f}%<extra></extra>"))
    f1.update_layout(**{**BASE, "margin": dict(t=52, b=80, l=52, r=24)}, height=height,
        title=dict(text="Death Rate by Season", font=dict(size=13), x=0.01, xanchor="left"),
        barmode="group", xaxis_title="Season",
        yaxis=dict(title="Deaths / 100 expeditions", gridcolor="#EEEEEE", zeroline=False),
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center", font=dict(size=11)))

    # Fig 2 — dual-axis team size (death rate PER MEMBER, not per expedition)
    ts = (flt.groupby("team_size", observed=True)
          .agg(exped=("expid","count"), deaths=("mdeaths","sum"),
               total_members=("totmembers","sum"), success=("success1","sum"))
          .reset_index())
    ts["drate"] = (ts["deaths"] / ts["total_members"] * 100).round(3)  # per-member rate
    ts["srate"] = (ts["success"] / ts["exped"] * 100).round(2)
    ts["small_n"] = ts["exped"] < 30  # flag unreliable cells
    f2 = make_subplots(specs=[[{"secondary_y": True}]])
    # Reliable bars normal, low-sample bars hatched with warning
    for _, row in ts.iterrows():
        pattern = "/" if row["small_n"] else ""
        label = f"{row['drate']:.3f}%" + (" ⚠️" if row["small_n"] else "")
        f2.add_trace(go.Bar(
            x=[row["team_size"]], y=[row["drate"]],
            name="Death rate per member (%)" if _ == 0 else "",
            showlegend=(_ == 0),
            marker_color=DANGER_COLOR,
            marker_pattern_shape=pattern,
            opacity=0.5 if row["small_n"] else 0.85,
            text=[label], textposition="outside",
            hovertemplate=(
                f"Team: <b>{row['team_size']}</b><br>"
                f"Deaths per member: {row['drate']:.3f}%<br>"
                f"Expeditions: {int(row['exped'])}"
                + (" ⚠️ small sample" if row["small_n"] else "")
                + "<extra></extra>"
            ),
        ), secondary_y=False)
    f2.add_trace(go.Scatter(x=ts["team_size"], y=ts["srate"], name="Success rate (%)",
        mode="lines+markers", line=dict(color=SUCCESS_COLOR, width=2.5),
        marker=dict(size=8, color=SUCCESS_COLOR, line=dict(color="white", width=1.5)),
        hovertemplate="Team: <b>%{x}</b><br>Success rate: %{y:.2f}%<extra></extra>"), secondary_y=True)
    f2.update_layout(**BASE, height=height,
        title=dict(text="Death Rate per Member vs. Success Rate by Team Size", font=dict(size=13), x=0.01, xanchor="left"),
        xaxis_title="Team size (members)",
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center", font=dict(size=11)),
        yaxis=dict(title=dict(text="Death rate per member (%)", font=dict(color=DANGER_COLOR)), gridcolor="#EEEEEE", zeroline=False),
        yaxis2=dict(title=dict(text="Success rate (%)", font=dict(color=SUCCESS_COLOR)), zeroline=False))

    # Fig 3 — time series
    yr = (flt.groupby("year").agg(exped=("expid","count"), deaths=("mdeaths","sum")).reset_index())
    f3 = make_subplots(specs=[[{"secondary_y": True}]])
    f3.add_trace(go.Scatter(x=yr["year"], y=yr["exped"], name="Expeditions",
        mode="lines", fill="tozeroy", line=dict(color=ACCENT, width=2),
        fillcolor="rgba(86,180,233,0.10)",
        hovertemplate="<b>%{x}</b><br>Expeditions: %{y}<extra></extra>"), secondary_y=False)
    f3.add_trace(go.Bar(x=yr["year"], y=yr["deaths"], name="Deaths",
        marker_color=DANGER_COLOR, opacity=0.6,
        hovertemplate="<b>%{x}</b><br>Deaths: %{y}<extra></extra>"), secondary_y=True)
    events = {1996: ("1996 disaster", 40), 2014: ("2014 avalanche", -60),
              2015: ("2015 earthquake", -80), 2020: ("COVID closure", 40)}
    annots = []
    for yr_ev, (label, ay) in events.items():
        row = yr[yr["year"] == yr_ev]
        if len(row):
            annots.append(dict(x=yr_ev, y=row["exped"].values[0], text=label,
                showarrow=True, arrowhead=2, arrowcolor=TEXT_TER, ax=0, ay=ay,
                font=dict(size=10, color=TEXT_SEC), bgcolor="white", bordercolor=BORDER, borderwidth=1))
    f3.update_layout(**BASE, height=height,
        title=dict(text="Expedition Volume & Deaths Over Time", font=dict(size=13), x=0.01, xanchor="left"),
        xaxis_title="Year",
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center", font=dict(size=11)),
        yaxis=dict(title="Expeditions per year", gridcolor="#EEEEEE", zeroline=False),
        yaxis2=dict(title=dict(text="Deaths per year", font=dict(color=DANGER_COLOR)), zeroline=False),
        annotations=annots)

    # Fig 4 — heatmap
    hm_seasons = [s for s in ["Spring","Autumn","Winter"] if s in seasons] or ["Spring","Autumn","Winter"]
    sizes_hm   = ["1–3","4–6","7–12","13–25","26+"]
    cross = (flt[flt["season"].isin(hm_seasons)]
             .groupby(["season","team_size"], observed=True)
             .agg(exped=("expid","count"), deaths=("mdeaths","sum")).reset_index())
    cross["drate"] = (cross["deaths"] / cross["exped"] * 100).round(2)
    z, text_z = [], []
    for s in hm_seasons:
        row, trow = [], []
        for sz in sizes_hm:
            cell = cross[(cross["season"]==s)&(cross["team_size"]==sz)]
            val = cell["drate"].values[0] if len(cell) else 0
            n   = int(cell["exped"].values[0]) if len(cell) else 0
            warn = " ⚠️" if n < 30 else ""
            row.append(val); trow.append(f"{val:.1f}%<br>n={n}{warn}")
        z.append(row); text_z.append(trow)
    f4 = go.Figure(go.Heatmap(z=z, x=sizes_hm, y=hm_seasons,
        text=text_z, texttemplate="%{text}", textfont=dict(size=11),
        colorscale=[[0,"#FFFFFF"],[0.25,"#FAE8E7"],[0.55,"#F09080"],[1,"#8B2010"]],
        colorbar=dict(title="Death<br>rate (%)", titlefont=dict(size=11)),
        hovertemplate="Season: <b>%{y}</b><br>Team: <b>%{x}</b><br>Death rate: %{z:.2f}%<extra></extra>"))
    f4.update_layout(**BASE, height=height,
        title=dict(text="Death Rate Heatmap: Season x Team Size", font=dict(size=13), x=0.01, xanchor="left"),
        xaxis_title="Team size (members)", yaxis_title="Season")

    # Fig 5 — termination stacked bar
    tr = (flt[flt["season"].isin(hm_seasons)]
          .groupby(["season","term_simple"]).size().reset_index(name="count"))
    tr_piv = (tr.pivot(index="season", columns="term_simple", values="count")
              .fillna(0).apply(lambda r: r / r.sum() * 100, axis=1).reset_index())
    f5 = go.Figure()
    for term in TERM_ORDER:
        if term not in tr_piv.columns:
            continue
        f5.add_trace(go.Bar(x=tr_piv["season"], y=tr_piv[term], name=term,
            marker_color=TERM_COLORS.get(term,"#aaa"),
            hovertemplate=f"<b>%{{x}}</b><br>{term}: %{{y:.1f}}%<extra></extra>"))
    f5.update_layout(**{**BASE, "margin": dict(t=52, b=48, l=52, r=130)}, height=height,
        title=dict(text="Expedition Outcome by Season (%)", font=dict(size=13), x=0.01, xanchor="left"),
        barmode="stack", xaxis_title="Season",
        yaxis=dict(title="Proportion (%)", gridcolor="#EEEEEE", zeroline=False),
        legend=dict(orientation="v", x=1.01, y=1, font=dict(size=10)))

    # Fig 6 — highpoint
    hp = (flt[flt["highpoint"]>0].groupby("team_size", observed=True)
          .agg(avg_hp=("highpoint","mean"), med_hp=("highpoint","median")).reset_index())
    f6 = go.Figure()
    f6.add_trace(go.Bar(x=hp["team_size"], y=hp["avg_hp"], name="Avg highpoint",
        marker_color=ACCENT, text=hp["avg_hp"].map(lambda v: f"{int(v):,} m"), textposition="outside",
        hovertemplate="Team: <b>%{x}</b><br>Avg highpoint: %{y:,.0f} m<extra></extra>"))
    f6.add_trace(go.Scatter(x=hp["team_size"], y=hp["med_hp"], name="Median highpoint",
        mode="lines+markers", line=dict(color=DANGER_COLOR, width=2, dash="dot"),
        marker=dict(size=7, color=DANGER_COLOR),
        hovertemplate="Team: <b>%{x}</b><br>Median highpoint: %{y:,.0f} m<extra></extra>"))
    f6.add_hline(y=8000, line_dash="dash", line_color="#888", line_width=1,
        annotation_text="8,000 m death zone", annotation_position="top right",
        annotation_font=dict(size=10, color=TEXT_SEC))
    f6.update_layout(**BASE, height=height,
        title=dict(text="Avg Highpoint Reached by Team Size", font=dict(size=13), x=0.01, xanchor="left"),
        xaxis_title="Team size (members)",
        yaxis=dict(title="Altitude (m)", gridcolor="#EEEEEE", zeroline=False, range=[6000, 8800]),
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center", font=dict(size=11)))

    # Fig 7 — boxplot
    f7 = go.Figure()
    for s in seasons:
        sub = flt[flt["season"]==s]["totmembers"].dropna()
        if len(sub) == 0:
            continue
        f7.add_trace(go.Box(y=sub, name=s, marker_color=SEASON_COLORS.get(s,"#aaa"),
            line_color=SEASON_COLORS.get(s,"#aaa"), fillcolor=SEASON_COLORS.get(s,"#aaa"),
            opacity=0.7, boxmean="sd",
            hovertemplate=f"<b>{s}</b><br>Team size: %{{y}}<extra></extra>"))
    f7.update_layout(**BASE, height=height,
        title=dict(text="Team Size Distribution by Season", font=dict(size=13), x=0.01, xanchor="left"),
        yaxis=dict(title="Members per expedition", gridcolor="#EEEEEE", zeroline=False),
        showlegend=False)

    return (total_exped, total_deaths, death_rate, avg_team), f1, f2, f3, f4, f5, f6, f7


# ── Reusable components ───────────────────────────────────────
def make_filter_bar():
    return html.Div([
        html.Div([
            html.Span("Season ", style={"fontSize":"12px","fontWeight":"600","color":TEXT_SEC,"marginRight":"8px"}),
            dcc.Checklist(id="season-filter",
                options=[{"label": html.Span(s, style={"color":SEASON_COLORS[s],"fontWeight":"600","fontSize":"13px"}),
                          "value": s} for s in ALL_SEASONS],
                value=ALL_SEASONS, inline=True,
                inputStyle={"marginRight":"4px","marginLeft":"14px","cursor":"pointer"}),
            html.Span("  |  ", style={"color":BORDER,"margin":"0 12px"}),
            html.Span("Peak ", style={"fontSize":"12px","fontWeight":"600","color":TEXT_SEC,"marginRight":"8px"}),
            dcc.RadioItems(id="peak-filter",
                options=[
                    {"label": html.Span("All peaks",    style={"fontSize":"13px"}), "value": "all"},
                    {"label": html.Span("Everest only", style={"fontSize":"13px","color":DANGER_COLOR,"fontWeight":"600"}), "value": "everest"},
                    {"label": html.Span("Non-Everest",  style={"fontSize":"13px","color":ACCENT,"fontWeight":"600"}), "value": "non_everest"},
                ],
                value="all", inline=True,
                inputStyle={"marginRight":"4px","marginLeft":"14px","cursor":"pointer"}),
        ], style={"display":"flex","alignItems":"center","flexWrap":"wrap","marginBottom":"10px"}),
        html.Div([
            html.Span("Year range ", style={"fontSize":"12px","fontWeight":"600","color":TEXT_SEC,"marginRight":"8px","whiteSpace":"nowrap"}),
            html.Div(dcc.RangeSlider(id="year-filter", min=1950, max=2024, step=1, value=[1950,2024],
                marks={y: {"label":str(y),"style":{"fontSize":"10px","color":TEXT_SEC}} for y in range(1950,2025,10)},
                tooltip={"placement":"bottom","always_visible":False}),
                style={"flex":"1","minWidth":"260px"}),
        ], style={"display":"flex","alignItems":"center"}),
    ], style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"8px",
              "padding":"14px 16px","marginBottom":"16px"})


def make_kpi_card(label, val, note, color=TEXT_PRI):
    return html.Div([
        html.Div(label, style={"fontSize":"10px","fontWeight":"600","letterSpacing":"0.06em",
                               "textTransform":"uppercase","color":TEXT_SEC,"marginBottom":"4px"}),
        html.Div(val,   style={"fontSize":"26px","fontWeight":"600","color":color,"lineHeight":"1"}),
        html.Div(note,  style={"fontSize":"11px","color":TEXT_TER,"marginTop":"3px"}),
    ], style={"background":CARD_BG,"borderRadius":"8px","border":f"1px solid {BORDER}","padding":"14px 16px"})


def section_label(text):
    return html.P(text, style={"fontSize":"11px","fontWeight":"600","letterSpacing":"0.07em",
                                "textTransform":"uppercase","color":TEXT_SEC,"margin":"20px 0 8px"})


def clickable_card(graph_id):
    return html.Div(
        dcc.Graph(id=graph_id, config={"displayModeBar": False}, style={"cursor":"pointer"}),
        id=f"card-{graph_id}", n_clicks=0,
        style={"background":CARD_BG,"borderRadius":"10px","border":f"1px solid {BORDER}",
               "padding":"6px 10px","cursor":"pointer",
               "transition":"box-shadow 0.15s ease, border-color 0.15s ease"},
    )


# ── App layout ────────────────────────────────────────────────
app = Dash(__name__, title="Himalayan Expedition Risk", suppress_callback_exceptions=True)

app.index_string = """<!DOCTYPE html>
<html>
<head>{%metas%}<title>{%title%}</title>{%favicon%}{%css%}
<style>
  * { box-sizing: border-box; }
  body { margin: 0; background: #FAFAF8; }
  div[id^="card-"]:hover {
    box-shadow: 0 4px 18px rgba(0,114,178,0.15) !important;
    border-color: #0072B2 !important;
  }
  #btn-back:hover { background: #0072B2 !important; color: white !important; border-color: #0072B2 !important; }
</style>
</head>
<body>{%app_entry%}{%config%}{%scripts%}{%renderer%}</body>
</html>"""

WRAP = {"maxWidth":"1200px","margin":"0 auto","padding":"28px 20px 56px"}

app.layout = html.Div(
    style={"fontFamily":FONT,"color":TEXT_PRI,"background":BG,"minHeight":"100vh"},
    children=[
        dcc.Store(id="active-chart", data=None),

        # ── SHARED HEADER + FILTERS (always visible, single instance of each ID) ──
        html.Div(id="shared-header", style={"maxWidth":"1200px","margin":"0 auto","padding":"28px 20px 0"},
        children=[
            html.H1("Himalayan Expedition Risk Dashboard",
                    style={"fontSize":"22px","fontWeight":"600","margin":"0 0 4px"}),
            html.P("How do team size and season influence expedition activity and fatality risk?  "
                   "· 1905–2024 · 11,000+ expeditions · The Himalayan Database",
                   style={"fontSize":"13px","color":TEXT_SEC,"margin":"0 0 4px"}),
            html.P("💡 Click any chart to expand it and read the full analysis.",
                   id="hint-text",
                   style={"fontSize":"12px","color":TEXT_TER,"margin":"0 0 14px"}),

            # ── ONE filter bar, one set of IDs ──
            make_filter_bar(),

            html.Div(id="kpi-row",
                     style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)",
                            "gap":"10px","marginBottom":"4px"}),
        ]),

        # ────────────────────────────────────────────────────
        # SCREEN 1 content (below shared header)
        # ────────────────────────────────────────────────────
        html.Div(id="screen-overview",
                 style={"maxWidth":"1200px","margin":"0 auto","padding":"12px 20px 56px"},
                 children=[
            section_label("Season & Team Size Risk"),
            html.Div([clickable_card("fig-season-bar"), clickable_card("fig-teamsize-dual")],
                     style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px","marginBottom":"12px"}),

            section_label("Activity Over Time"),
            html.Div(clickable_card("fig-timeseries"), style={"marginBottom":"12px"}),

            section_label("Risk Breakdown"),
            html.Div([clickable_card("fig-heatmap"), clickable_card("fig-termreason")],
                     style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px","marginBottom":"12px"}),

            section_label("Team Size Deep Dive"),
            html.Div([clickable_card("fig-highpoint"), clickable_card("fig-boxplot")],
                     style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px","marginBottom":"24px"}),

            html.Div([
                html.H3("Key Findings", style={"fontSize":"14px","fontWeight":"600","margin":"0 0 12px"}),
                *[html.Div([html.Span(bold, style={"fontWeight":"600"}), html.Span(rest)],
                           style={"fontSize":"13px","lineHeight":"1.65","marginBottom":"8px"})
                  for bold, rest in [
                    ("❄️  Winter is deadliest — ", "9.4 deaths per 100 expeditions, nearly 50% higher than Autumn."),
                    ("👥  Bigger teams, bigger risk — ", "Teams of 26+ have 11× the death rate of 1–3 person teams, yet achieve the highest summit success rates."),
                    ("🏔️  Larger teams reach higher — ", "The median highpoint for 26+ teams is 8,485 m vs. 7,246 m for small teams."),
                    ("📈  Exponential growth since the 1990s — ", "Expedition volume tripled from the 1980s to 2010s, driven by commercial Spring expeditions."),
                ]],
            ], style={"background":"#F0F4FB","borderRadius":"10px","border":"1px solid #C8D8F0","padding":"18px 22px"}),
        ]),

        # ────────────────────────────────────────────────────
        # SCREEN 2 content (hidden until chart clicked)
        # ────────────────────────────────────────────────────
        html.Div(id="screen-detail",
                 style={"display":"none","maxWidth":"1200px","margin":"0 auto","padding":"12px 20px 56px"},
                 children=[

            html.Div([
                html.Button("← Back to Dashboard", id="btn-back",
                    style={"background":"white","border":f"1px solid {BORDER}","borderRadius":"6px",
                           "padding":"7px 16px","fontSize":"13px","fontWeight":"600","color":TEXT_PRI,
                           "cursor":"pointer","marginRight":"14px","transition":"all 0.2s"}),
                html.Span(id="detail-breadcrumb", style={"fontSize":"13px","color":TEXT_SEC}),
            ], style={"marginBottom":"16px","display":"flex","alignItems":"center"}),

            html.Div(id="kpi-row-detail",
                     style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)",
                            "gap":"10px","marginBottom":"20px"}),

            html.Div(id="detail-chart-wrap",
                     style={"background":CARD_BG,"borderRadius":"12px",
                            "border":f"1px solid {BORDER}","padding":"10px 16px","marginBottom":"20px"}),

            html.Div(id="detail-description",
                     style={"background":CARD_BG,"borderRadius":"12px",
                            "border":f"1px solid {BORDER}","padding":"28px 32px"}),
        ]),
    ],
)


# ── Callback 1: switch screens on card click or back button ──
@app.callback(
    Output("active-chart",    "data"),
    Output("screen-overview", "style"),
    Output("screen-detail",   "style"),
    Input("card-fig-season-bar",    "n_clicks"),
    Input("card-fig-teamsize-dual", "n_clicks"),
    Input("card-fig-timeseries",    "n_clicks"),
    Input("card-fig-heatmap",       "n_clicks"),
    Input("card-fig-termreason",    "n_clicks"),
    Input("card-fig-highpoint",     "n_clicks"),
    Input("card-fig-boxplot",       "n_clicks"),
    Input("btn-back",               "n_clicks"),
    State("active-chart", "data"),
    prevent_initial_call=True,
)
def toggle_screen(*_):
    triggered = ctx.triggered_id
    if triggered == "btn-back" or triggered is None:
        return None, {**WRAP}, {"display":"none"}
    chart_id = triggered.replace("card-", "")
    return chart_id, {"display":"none"}, {**WRAP}


# ── Callback 2: update overview charts & KPIs ────────────────
@app.callback(
    Output("kpi-row",           "children"),
    Output("fig-season-bar",    "figure"),
    Output("fig-teamsize-dual", "figure"),
    Output("fig-timeseries",    "figure"),
    Output("fig-heatmap",       "figure"),
    Output("fig-termreason",    "figure"),
    Output("fig-highpoint",     "figure"),
    Output("fig-boxplot",       "figure"),
    Input("season-filter", "value"),
    Input("year-filter",   "value"),
    Input("peak-filter",   "value"),
)
def update_overview(seasons, year_range, peak_filter):
    seasons = seasons or ALL_SEASONS
    peak_filter = peak_filter or "all"
    (te, td, dr, at), f1, f2, f3, f4, f5, f6, f7 = build_figures(seasons, year_range, height=300, peak_filter=peak_filter)
    kpis = [
        make_kpi_card("Total Expeditions", f"{te:,}", f"{year_range[0]}–{year_range[1]}"),
        make_kpi_card("Member Deaths",     f"{td:,}", "filtered selection", DANGER_COLOR),
        make_kpi_card("Death Rate",        f"{dr}%",  "per expedition",     DANGER_COLOR),
        make_kpi_card("Avg Team Size",     f"{at}",   "members"),
    ]
    return kpis, f1, f2, f3, f4, f5, f6, f7


# ── Callback 3: populate detail screen ───────────────────────
@app.callback(
    Output("detail-breadcrumb",  "children"),
    Output("kpi-row-detail",     "children"),
    Output("detail-chart-wrap",  "children"),
    Output("detail-description", "children"),
    Input("active-chart",  "data"),
    Input("season-filter", "value"),
    Input("year-filter",   "value"),
    Input("peak-filter",   "value"),
)
def update_detail(active_chart, seasons, year_range, peak_filter):
    if not active_chart:
        return "", [], [], []

    seasons = seasons or ALL_SEASONS
    peak_filter = peak_filter or "all"
    info    = CHART_INFO.get(active_chart, {})

    (te, td, dr, at), f1, f2, f3, f4, f5, f6, f7 = build_figures(seasons, year_range, height=500, peak_filter=peak_filter)

    fig_map = {"fig-season-bar": f1, "fig-teamsize-dual": f2, "fig-timeseries": f3,
               "fig-heatmap": f4, "fig-termreason": f5, "fig-highpoint": f6, "fig-boxplot": f7}
    big_fig = fig_map.get(active_chart, f1)

    kpis = [
        make_kpi_card("Total Expeditions", f"{te:,}", f"{year_range[0]}–{year_range[1]}"),
        make_kpi_card("Member Deaths",     f"{td:,}", "filtered selection", DANGER_COLOR),
        make_kpi_card("Death Rate",        f"{dr}%",  "per expedition",     DANGER_COLOR),
        make_kpi_card("Avg Team Size",     f"{at}",   "members"),
    ]

    breadcrumb = f"Dashboard  ›  {info.get('title', active_chart)}"

    chart_section = dcc.Graph(figure=big_fig, config={"displayModeBar": True, "scrollZoom": False})

    description = html.Div([
        html.H2(info.get("title",""),
                style={"fontSize":"19px","fontWeight":"600","color":TEXT_PRI,"margin":"0 0 6px"}),
        html.P(info.get("subtitle",""),
               style={"fontSize":"13px","color":TEXT_SEC,"margin":"0 0 20px",
                      "paddingBottom":"18px","borderBottom":f"1px solid {BORDER}"}),
        *[html.P(p, style={"fontSize":"14px","lineHeight":"1.8","color":TEXT_PRI,"margin":"0 0 16px"})
          for p in info.get("description", [])],
    ])

    return breadcrumb, kpis, chart_section, description


server = app.server

if __name__ == "__main__":
    app.run(debug=True)