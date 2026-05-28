"""HTML rendering for the P0020 weekly home POC browser UI."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping


TABLE_COLUMNS = (
    "hour",
    "weekday_hour",
    "outdoor_temp_c",
    "outdoor_rh_pct",
    "spot_index",
    "heat_need_kWh",
    "heat_kWh",
    "heat_soc_pct",
    "heat_cost_weight",
    "heat_price_index",
    "heat_action_kw",
    "cop_optimized",
    "heat_el_kWh",
    "heat_el_cost",
    "flat_heat_kWh",
    "cop_flat",
    "flat_heat_el_kWh",
    "flat_heat_el_cost",
    "rh_weight",
    "supply_pct",
    "flow_lps",
    "ppm_delta",
    "ppm_absolute",
    "rh_delta",
    "total_cost",
)


def _attr(value: object) -> str:
    return escape(str(value), quote=True)


def render_page(title: str, body: str, status_message: str | None = None) -> str:
    """Render a complete HTML page for the local POC UI."""

    status = ""
    if status_message:
        status = f'<p class="status">{escape(status_message)}</p>'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f7f5;
      --panel: #ffffff;
      --ink: #17201a;
      --muted: #5d6a62;
      --line: #d8e0da;
      --accent: #0f7b6c;
      --accent-2: #8b5a12;
      --bad: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: #e9f0ec;
    }}
    .wrap {{
      width: min(1180px, calc(100% - 28px));
      margin: 0 auto;
      padding: 18px 0;
    }}
    h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 650;
      letter-spacing: 0;
    }}
    main .wrap {{ padding-top: 20px; }}
    form {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      align-items: end;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    label {{
      display: grid;
      gap: 5px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
    }}
    input {{
      width: 100%;
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      color: var(--ink);
      background: #fff;
      font: inherit;
    }}
    button, .button {{
      min-height: 38px;
      border: 1px solid var(--accent);
      border-radius: 6px;
      padding: 8px 12px;
      background: var(--accent);
      color: white;
      font: inherit;
      font-weight: 650;
      text-decoration: none;
      cursor: pointer;
      text-align: center;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
      margin: 16px 0;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-width: 0;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
    }}
    .metric strong {{
      display: block;
      margin-top: 4px;
      font-size: 20px;
      font-weight: 700;
    }}
    .actions {{
      display: flex;
      gap: 10px;
      align-items: center;
      margin: 12px 0;
      flex-wrap: wrap;
    }}
    .table-wrap {{
      overflow: auto;
      max-height: 70vh;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      min-width: 1120px;
      font-variant-numeric: tabular-nums;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 6px 8px;
      white-space: nowrap;
      text-align: right;
    }}
    th {{
      position: sticky;
      top: 0;
      background: #f8faf8;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      z-index: 1;
    }}
    th:nth-child(2), td:nth-child(2) {{ text-align: left; }}
    tr:nth-child(even) td {{ background: #fbfcfb; }}
    .status {{
      margin: 0 0 12px;
      color: var(--bad);
      font-weight: 650;
    }}
    .comparison {{
      margin: 14px 0 0;
      font-weight: 700;
    }}
    @media (max-width: 760px) {{
      .wrap {{ width: min(100% - 20px, 1180px); padding: 14px 0; }}
      h1 {{ font-size: 20px; }}
      form {{ grid-template-columns: 1fr; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .metric strong {{ font-size: 18px; }}
    }}
  </style>
</head>
<body>
  <header><div class="wrap"><h1>Weekly Home POC</h1></div></header>
  <main><div class="wrap">{status}{body}</div></main>
</body>
</html>
"""


def render_form(values: Mapping[str, object] | None = None, error: str | None = None) -> str:
    """Render the browser input form."""

    current = values or {}
    week = _attr(current.get("week", 2))
    ppm = _attr(current.get("ppm", 500))
    house_temp = _attr(current.get("houseTemp", 22))
    people = _attr(current.get("people", 3))
    body = f"""
<form method="get" action="/">
  <label>Week
    <input name="week" inputmode="numeric" value="{week}" required>
  </label>
  <label>PPM
    <input name="ppm" inputmode="decimal" value="{ppm}" required>
  </label>
  <label>House Temp
    <input name="houseTemp" inputmode="decimal" value="{house_temp}" required>
  </label>
  <label>People
    <input name="people" inputmode="decimal" value="{people}" required>
  </label>
  <button type="submit">Run Plan</button>
</form>
"""
    return render_page("Weekly Home POC", body, error)


def render_result(payload: Mapping[str, Any]) -> str:
    """Render a valid plan result page."""

    input_data = payload["input"]
    summary = payload["summary"]
    hours = payload["hours"]
    query = (
        f"week={_attr(input_data['week'])}&ppm={_attr(input_data['ppm'])}"
        f"&houseTemp={_attr(input_data['houseTemp'])}&people={_attr(input_data['people'])}"
    )
    metrics = [
        ("Hours", summary["hours"]),
        ("Min PPM", summary["min_ppm"]),
        ("Max PPM", summary["max_ppm"]),
        ("Avg Supply", summary["avg_supply_pct"]),
        ("Heat kWh", summary["total_heat_kWh"]),
        ("Heat Opt", summary["heat_optimizer"]),
        ("End SOC", summary["end_heat_soc_pct"]),
        ("Min SOC", summary["min_heat_soc_pct"]),
        ("Heat Cost", summary["heat_cost_model"]),
        ("Opt El Cost", summary["optimized_heat_el_cost"]),
        ("Flat El Cost", summary["flat_heat_el_cost"]),
        ("Opt vs Flat", _pct(summary["optimized_vs_flat_cost_pct"])),
        ("Estimated saving", _pct(summary["optimized_saving_pct"])),
        ("COP Opt", summary["avg_cop_optimized"]),
        ("COP Flat", summary["avg_cop_flat"]),
        ("People", summary["people"]),
        ("PPM/h", summary["occupancy_gain_ppm_h"]),
        ("Weather", summary["weather_source"]),
        ("Provider", summary["weather_provider"]),
        ("Weather Year", summary["weather_profile_year"]),
    ]
    if summary.get("weather_fallback_reason"):
        metrics.append(("Fallback", summary["weather_fallback_reason"]))
    if summary.get("heat_optimizer_warnings"):
        metrics.append(("Heat Warnings", ", ".join(summary["heat_optimizer_warnings"])))
    if summary.get("heat_cost_comparison_warnings"):
        metrics.append(("Cost Warnings", ", ".join(summary["heat_cost_comparison_warnings"])))
    metric_html = "\n".join(
        f'<div class="metric"><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>'
        for label, value in metrics
    )
    header_html = "".join(f"<th>{escape(column)}</th>" for column in TABLE_COLUMNS)
    row_html = []
    for row in hours:
        cells = "".join(f"<td>{escape(str(row[column]))}</td>" for column in TABLE_COLUMNS)
        row_html.append(f"<tr>{cells}</tr>")
    comparison = _comparison_sentence(summary)
    body = f"""
{_result_form(input_data)}
{comparison}
<section class="summary">{metric_html}</section>
<div class="actions">
  <a class="button" href="/api/weekly-home-poc?{query}">JSON</a>
</div>
<div class="table-wrap">
  <table>
    <thead><tr>{header_html}</tr></thead>
    <tbody>{''.join(row_html)}</tbody>
  </table>
</div>
"""
    return render_page("Weekly Home POC Result", body)


def _pct(value: object) -> str:
    if value is None:
        return "n/a"
    return f"{value}%"


def _comparison_sentence(summary: Mapping[str, Any]) -> str:
    pct = summary.get("optimized_vs_flat_cost_pct")
    saving = summary.get("optimized_saving_pct")
    if pct is None:
        text = "Optimized heat cost comparison is unavailable for this emulated POC run."
    else:
        text = (
            f"Optimized heat did the weekly job at {pct}% of flat-production cost "
            f"({saving}% estimated saving, emulated POC)."
        )
    return f'<p class="comparison">{escape(text)}</p>'


def _result_form(input_data: Mapping[str, Any]) -> str:
    week = _attr(input_data["week"])
    ppm = _attr(input_data["ppm"])
    house_temp = _attr(input_data["houseTemp"])
    people = _attr(input_data.get("people", 3))
    return f"""
<form method="get" action="/">
  <label>Week
    <input name="week" inputmode="numeric" value="{week}" required>
  </label>
  <label>PPM
    <input name="ppm" inputmode="decimal" value="{ppm}" required>
  </label>
  <label>House Temp
    <input name="houseTemp" inputmode="decimal" value="{house_temp}" required>
  </label>
  <label>People
    <input name="people" inputmode="decimal" value="{people}" required>
  </label>
  <button type="submit">Run Plan</button>
</form>
"""
