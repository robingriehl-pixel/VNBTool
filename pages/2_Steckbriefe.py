from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "output" / "df_data.csv"
BESS_DATA_PATH = BASE_DIR / "output" / "df_bess_data.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(DATA_PATH, sep=";", encoding="utf-8-sig")


@st.cache_data
def load_bess_data() -> pd.DataFrame:
    if not BESS_DATA_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(BESS_DATA_PATH, sep=";", encoding="utf-8-sig")


def read_csv_with_mtime(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return _read_csv_with_mtime(path, path.stat().st_mtime)


@st.cache_data
def _read_csv_with_mtime(path: Path, _mtime: float) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", encoding="utf-8-sig")


st.set_page_config(page_title="Steckbriefe", page_icon="V", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2.25rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        margin-top: 0.8rem;
        margin-bottom: 0.8rem;
    }

    div.stButton > button {
        height: 72px;
        white-space: normal;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        background: rgba(22, 27, 38, 0.78);
        color: #e5e7eb;
        font-weight: 600;
    }

    div.stButton > button:hover {
        border-color: rgba(96, 165, 250, 0.65);
        background: rgba(30, 41, 59, 0.95);
    }

    [data-testid="stMetric"] {
        background: rgba(22, 27, 38, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
    }

    [data-testid="stMetricLabel"] {
        padding-bottom: 0.25rem;
        color: #cbd5e1;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    [data-testid="stVerticalBlock"] > [data-testid="element-container"]:has([data-testid="stVegaLiteChart"]) {
        background: rgba(15, 23, 42, 0.52);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 20px;
        padding: 0.75rem 0.9rem 0.25rem 0.9rem;
        margin-bottom: 1.4rem;
    }

    [data-testid="stSelectbox"] {
        margin-top: 0.8rem;
        margin-bottom: 1.35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

df_data = read_csv_with_mtime(DATA_PATH)
df_bess_data = read_csv_with_mtime(BESS_DATA_PATH)

if "betriebsstatus" in df_bess_data.columns:
    df_bess_data_active = df_bess_data[
        df_bess_data["betriebsstatus"].astype(str).str.strip().eq("In Betrieb")
    ].copy()
else:
    df_bess_data_active = df_bess_data.copy()

st.title("Voltpark VNB Tool")
st.markdown("<div style='height: 1.1rem;'></div>", unsafe_allow_html=True)

if df_data.empty:
    st.warning("Keine Daten in 'output/df_data.csv' gefunden.")
    st.stop()

name_col = "vnb_names" if "vnb_names" in df_data.columns else None
key_col = "keys" if "keys" in df_data.columns else None

if not name_col or not key_col:
    st.error("Die benoetigten Spalten 'keys' und 'vnb_names' fehlen.")
    st.stop()

options = (
    df_data[[key_col, name_col]]
    .dropna()
    .drop_duplicates()
    .sort_values(name_col)
)

df_selector = df_data[[key_col, name_col, "length_ns", "length_ms", "length_hs"]].copy()
for col in ["length_ns", "length_ms", "length_hs"]:
    df_selector[col] = pd.to_numeric(df_selector[col], errors="coerce").fillna(0)
df_selector["total_length"] = (
    df_selector[["length_ns", "length_ms", "length_hs"]].sum(axis=1)
)

top_vnb_names = (
    df_selector[[name_col, "total_length"]]
    .dropna(subset=[name_col])
    .drop_duplicates(subset=[name_col])
    .sort_values("total_length", ascending=False)
    .head(8)[name_col]
    .tolist()
)

if "selected_vnb_name" not in st.session_state:
    st.session_state.selected_vnb_name = top_vnb_names[0] if top_vnb_names else options[name_col].iloc[0]

st.subheader("Größte VNB")
for idx, vnb_name in enumerate(top_vnb_names):
    if idx % 4 == 0:
        top_cols = st.columns(4)
    with top_cols[idx % 4]:
        if st.button(vnb_name, use_container_width=True, key=f"top_vnb_{idx}"):
            st.session_state.selected_vnb_name = vnb_name

all_vnb_names = options[name_col].tolist()
if st.session_state.selected_vnb_name not in all_vnb_names and all_vnb_names:
    st.session_state.selected_vnb_name = all_vnb_names[0]

selected_name = st.selectbox(
    "Anderen VNB suchen",
    all_vnb_names,
    index=all_vnb_names.index(st.session_state.selected_vnb_name),
)
st.session_state.selected_vnb_name = selected_name

selected_row = df_data.loc[df_data[name_col] == selected_name].head(1)

if selected_row.empty:
    st.info("Kein passender Datensatz gefunden.")
    st.stop()

record = selected_row.iloc[0]

total_length = (
    pd.to_numeric(pd.Series([record.get("length_ns", 0)]), errors="coerce").fillna(0).iloc[0]
    + pd.to_numeric(pd.Series([record.get("length_ms", 0)]), errors="coerce").fillna(0).iloc[0]
    + pd.to_numeric(pd.Series([record.get("length_hs", 0)]), errors="coerce").fillna(0).iloc[0]
)
digital_score_total = pd.to_numeric(
    pd.Series([record.get("digital_score_total", 0)]), errors="coerce"
).fillna(0).iloc[0]
storage_request_by_level = {
    "NS": {
        "count": pd.to_numeric(
            pd.Series([record.get("count_storage_requests_ns", 0)]), errors="coerce"
        ).fillna(0).iloc[0],
        "sum": pd.to_numeric(
            pd.Series([record.get("sum_storage_requests_ns", 0)]), errors="coerce"
        ).fillna(0).iloc[0],
        "duration": pd.to_numeric(
            pd.Series([record.get("duration_storage_ns", 0)]), errors="coerce"
        ).fillna(0).iloc[0],
    },
    "MS": {
        "count": pd.to_numeric(
            pd.Series([record.get("count_storage_requests_ms", 0)]), errors="coerce"
        ).fillna(0).iloc[0],
        "sum": pd.to_numeric(
            pd.Series([record.get("sum_storage_requests_ms", 0)]), errors="coerce"
        ).fillna(0).iloc[0],
        "duration": pd.to_numeric(
            pd.Series([record.get("duration_storage_ms", 0)]), errors="coerce"
        ).fillna(0).iloc[0],
    },
    "HS": {
        "count": pd.to_numeric(
            pd.Series([record.get("count_storage_requests_hs", 0)]), errors="coerce"
        ).fillna(0).iloc[0],
        "sum": pd.to_numeric(
            pd.Series([record.get("sum_storage_requests_hs", 0)]), errors="coerce"
        ).fillna(0).iloc[0],
        "duration": pd.to_numeric(
            pd.Series([record.get("duration_storage_hs", 0)]), errors="coerce"
        ).fillna(0).iloc[0],
    },
}

total_storage_request_sum = sum(
    storage_request_by_level[level]["sum"] for level in ("NS", "MS", "HS")
)

bess_brutto_by_level = {"NS": 0.0, "MS": 0.0, "HS": 0.0}
bess_timeline_df = pd.DataFrame(columns=["datum", "cumulative_bruttoleistung", "serie"])
if not df_bess_data_active.empty and record.get("MSTR_key") is not None:
    bess_vnb_df = df_bess_data_active.loc[
        df_bess_data_active["keys"] == record.get("MSTR_key")
    ].copy()
    if not bess_vnb_df.empty:
        bess_vnb_df["bruttoleistung_einheit"] = (
            bess_vnb_df["bruttoleistung_einheit"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        bess_vnb_df["bruttoleistung_einheit"] = pd.to_numeric(
            bess_vnb_df["bruttoleistung_einheit"], errors="coerce"
        )
        for level in ("NS", "MS", "HS"):
            bess_brutto_by_level[level] = (
                bess_vnb_df.loc[
                    bess_vnb_df["spannungsebene"] == level,
                    "bruttoleistung_einheit",
                ]
                .fillna(0)
                .sum()
            )
        bess_vnb_df["inbetriebnahme_datum"] = pd.to_datetime(
            bess_vnb_df["inbetriebnahme_datum"],
            format="%d.%m.%Y",
            errors="coerce",
        )
        bess_timeline_inbetrieb = (
            bess_vnb_df.dropna(subset=["inbetriebnahme_datum", "bruttoleistung_einheit"])
            .loc[lambda frame: frame["inbetriebnahme_datum"] >= pd.Timestamp("2010-01-01")]
            .sort_values("inbetriebnahme_datum")
            .groupby("inbetriebnahme_datum", as_index=False)["bruttoleistung_einheit"]
            .sum()
        )
        bess_timeline_inbetrieb["cumulative_bruttoleistung"] = (
            bess_timeline_inbetrieb["bruttoleistung_einheit"].cumsum()
        )
        bess_timeline_inbetrieb["datum"] = bess_timeline_inbetrieb["inbetriebnahme_datum"]
        bess_timeline_inbetrieb["serie"] = "In Betrieb"
        bess_timeline_df = pd.concat(
            [
                bess_timeline_df,
                bess_timeline_inbetrieb[["datum", "cumulative_bruttoleistung", "serie"]],
            ],
            ignore_index=True,
        )

if (
    not df_bess_data.empty
    and record.get("MSTR_key") is not None
    and "registrierungsdatum" in df_bess_data.columns
):
    bess_vnb_plan_df = df_bess_data.loc[
        df_bess_data["keys"] == record.get("MSTR_key")
    ].copy()
    if "betriebsstatus" in bess_vnb_plan_df.columns:
        bess_vnb_plan_df = bess_vnb_plan_df[
            bess_vnb_plan_df["betriebsstatus"].astype(str).str.strip().eq("In Planung")
        ].copy()

    if not bess_vnb_plan_df.empty:
        bess_vnb_plan_df["bruttoleistung_einheit"] = (
            bess_vnb_plan_df["bruttoleistung_einheit"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        bess_vnb_plan_df["bruttoleistung_einheit"] = pd.to_numeric(
            bess_vnb_plan_df["bruttoleistung_einheit"], errors="coerce"
        )
        bess_vnb_plan_df["registrierungsdatum"] = pd.to_datetime(
            bess_vnb_plan_df["registrierungsdatum"],
            format="%d.%m.%Y",
            errors="coerce",
        )
        bess_timeline_plan = (
            bess_vnb_plan_df.dropna(subset=["registrierungsdatum", "bruttoleistung_einheit"])
            .loc[lambda frame: frame["registrierungsdatum"] >= pd.Timestamp("2010-01-01")]
            .sort_values("registrierungsdatum")
            .groupby("registrierungsdatum", as_index=False)["bruttoleistung_einheit"]
            .sum()
        )
        bess_timeline_plan["cumulative_bruttoleistung"] = (
            bess_timeline_plan["bruttoleistung_einheit"].cumsum()
        )
        bess_timeline_plan["datum"] = bess_timeline_plan["registrierungsdatum"]
        bess_timeline_plan["serie"] = "In Planung"
        bess_timeline_df = pd.concat(
            [
                bess_timeline_df,
                bess_timeline_plan[["datum", "cumulative_bruttoleistung", "serie"]],
            ],
            ignore_index=True,
        )

st.markdown("---")

header_left, header_right = st.columns([4, 1])
with header_left:
    st.markdown(f"## {record.get('vnb_names', '')}")
with header_right:
    st.caption("MaStR-Key")
    st.write(record.get("MSTR_key", ""))

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Spannungsebenen", record.get("vnb_vlevels", ""))
metric_col2.metric("Stromkreislänge gesamt", f"{total_length:,.0f} km")
metric_col3.metric("Storage Requests gesamt", f"{total_storage_request_sum:,.0f} kW")

st.markdown("#### BESS Bruttoleistung")
st.caption("Nur Batteriespeicher ab 50kW")

bess_col1, bess_col2, bess_col3 = st.columns(3)
bess_col1.metric("NS", f"{bess_brutto_by_level['NS']:,.0f} kW")
bess_col2.metric("MS", f"{bess_brutto_by_level['MS']:,.0f} kW")
bess_col3.metric("HS", f"{bess_brutto_by_level['HS']:,.0f} kW")

if not bess_timeline_df.empty:
    bess_timeline_chart = (
        alt.Chart(bess_timeline_df)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X(
                "datum:T",
                title="Datum",
                scale=alt.Scale(
                    domain=[
                        pd.Timestamp("2010-01-01"),
                        pd.Timestamp.today().normalize(),
                    ]
                ),
                axis=alt.Axis(format="%Y"),
            ),
            y=alt.Y(
                "cumulative_bruttoleistung:Q",
                title="Kumulierte BESS-Bruttoleistung (kW)",
            ),
            color=alt.Color(
                "serie:N",
                title="Serie",
                scale=alt.Scale(
                    domain=["In Betrieb", "In Planung"],
                    range=["#2563eb", "#dc2626"],
                ),
            ),
            tooltip=[
                alt.Tooltip("serie:N", title="Serie"),
                alt.Tooltip("datum:T", title="Datum"),
                alt.Tooltip(
                    "cumulative_bruttoleistung:Q",
                    title="Kumulierte Bruttoleistung",
                    format=",.0f",
                ),
            ],
        )
        .properties(height=335)
    )

    st.altair_chart(bess_timeline_chart, use_container_width=True)

st.markdown("#### Netzanschluss")

for level in ("NS", "MS", "HS"):
    level_col, request_col1, request_col2, request_col3 = st.columns([0.7, 1, 1, 1])
    with level_col:
        st.markdown(f"**{level}**")
    request_col1.metric(
        "Count Storage Requests",
        f"{storage_request_by_level[level]['count']:,.0f}",
    )
    request_col2.metric(
        "Sum Storage Requests",
        f"{storage_request_by_level[level]['sum']:,.0f} kW",
    )
    request_col3.metric(
        "Duration Requests",
        f"{storage_request_by_level[level]['duration']:,.0f} Tage",
    )

st.markdown("#### NS / MS / HS Profil")
st.caption("Erhebung Stand 2024")

profile_configs = [
    (
        "Stromkreislänge",
        {
            "NS": pd.to_numeric(pd.Series([record.get("length_ns", 0)]), errors="coerce").fillna(0).iloc[0],
            "MS": pd.to_numeric(pd.Series([record.get("length_ms", 0)]), errors="coerce").fillna(0).iloc[0],
            "HS": pd.to_numeric(pd.Series([record.get("length_hs", 0)]), errors="coerce").fillna(0).iloc[0],
        },
        "km",
    ),
    (
        "Count Storage Requests",
        {
            "NS": storage_request_by_level["NS"]["count"],
            "MS": storage_request_by_level["MS"]["count"],
            "HS": storage_request_by_level["HS"]["count"],
        },
        "",
    ),
    (
        "Sum Storage Requests",
        {
            "NS": storage_request_by_level["NS"]["sum"],
            "MS": storage_request_by_level["MS"]["sum"],
            "HS": storage_request_by_level["HS"]["sum"],
        },
        "kW",
    ),
    (
        "Duration Storage",
        {
            "NS": storage_request_by_level["NS"]["duration"],
            "MS": storage_request_by_level["MS"]["duration"],
            "HS": storage_request_by_level["HS"]["duration"],
        },
        "Tage",
    ),
]

profile_color_scale = alt.Scale(
    domain=["NS", "MS", "HS"],
    range=["#2563eb", "#f59e0b", "#dc2626"],
)

for label, value_map, unit in profile_configs:
    display_label = f"{label} ({unit})" if unit else label
    profile_metric_df = pd.DataFrame(
        {
            "level": ["NS", "MS", "HS"],
            "value": [value_map["NS"], value_map["MS"], value_map["HS"]],
            "y": [0, 0, 0],
        }
    )
    max_value = max(profile_metric_df["value"].max(), 1)
    axis_padding = max_value * 0.04
    if max_value <= 100:
        axis_padding = max(axis_padding, 4)
    elif max_value <= 1000:
        axis_padding = max(axis_padding, 20)
    else:
        axis_padding = max(axis_padding, max_value * 0.03)
    x_domain = [0, max_value + axis_padding]
    baseline_df = pd.DataFrame({"x_start": [0], "x_end": [max_value], "y": [0]})

    st.markdown(f"**{display_label}**")

    profile_line = (
        alt.Chart(baseline_df)
        .mark_rule(strokeWidth=3, color="#6b7280")
        .encode(
            x=alt.X("x_start:Q", scale=alt.Scale(domain=x_domain), title=display_label),
            x2="x_end:Q",
            y=alt.Y("y:Q", axis=None),
        )
    )

    profile_points = (
        alt.Chart(profile_metric_df)
        .mark_circle(size=220, opacity=0.9)
        .encode(
            x=alt.X("value:Q", scale=alt.Scale(domain=x_domain), title=display_label),
            y=alt.Y("y:Q", axis=None),
            color=alt.Color("level:N", title="Ebene", scale=profile_color_scale),
            tooltip=[
                alt.Tooltip("level:N", title="Ebene"),
                alt.Tooltip("value:Q", title=display_label, format=",.2f"),
            ],
        )
        .properties(height=110)
    )

    profile_labels = (
        alt.Chart(profile_metric_df)
        .mark_text(dy=-18, fontSize=12, fontWeight="bold")
        .encode(
            x=alt.X("value:Q", scale=alt.Scale(domain=x_domain)),
            y=alt.Y("y:Q", axis=None),
            text="level:N",
            color=alt.Color("level:N", scale=profile_color_scale, legend=None),
        )
    )

    st.altair_chart(profile_line + profile_points + profile_labels, use_container_width=True)

base_line = pd.DataFrame({"x_start": [0.0], "x_end": [1.0], "y": [0]})
digital_score_configs = [
    ("Digital Score gesamt", "digital_score_total"),
    ("Smart Grids", "digital_score_smart_grids"),
    ("Digitale Prozesse und Systeme", "digital_score_processes_systems"),
    ("Datenmanagement und Analyse", "digital_score_data_management_analysis"),
    ("Kundenmanagement", "digital_score_customer_management"),
]

st.markdown("#### Einordnung der Digital Scores")
st.caption("Erhebung Stand 2024")

digital_x_domain = [0, 1.03]

for label, score_col in digital_score_configs:
    if score_col not in df_data.columns:
        continue

    score_value = pd.to_numeric(
        pd.Series([record.get(score_col, 0)]), errors="coerce"
    ).fillna(0).iloc[0]

    st.markdown(f"**{label}: {score_value:.2f}**")

    score_df = df_data[[name_col, score_col]].copy()
    score_df[score_col] = pd.to_numeric(score_df[score_col], errors="coerce")
    score_df = score_df.dropna(subset=[score_col])
    score_df["y"] = 0
    score_df["selected"] = score_df[name_col] == selected_name

    line = (
        alt.Chart(base_line)
        .mark_rule(strokeWidth=3, color="#6b7280")
        .encode(
            x=alt.X("x_start:Q", scale=alt.Scale(domain=digital_x_domain), title=label),
            x2="x_end:Q",
            y=alt.Y("y:Q", axis=None),
        )
    )

    all_points = (
        alt.Chart(score_df.loc[~score_df["selected"]])
        .mark_circle(size=60, opacity=0.45, color="#9ca3af")
        .encode(
            x=alt.X(
                f"{score_col}:Q",
                scale=alt.Scale(domain=digital_x_domain),
                axis=alt.Axis(values=[0, 0.25, 0.5, 0.75, 1.0], format=".2f"),
                title=label,
            ),
            y=alt.Y("y:Q", axis=None),
            tooltip=[
                alt.Tooltip(f"{name_col}:N", title="VNB"),
                alt.Tooltip(f"{score_col}:Q", title=label, format=".2f"),
            ],
        )
    )

    selected_point = (
        alt.Chart(score_df.loc[score_df["selected"]])
        .mark_circle(size=420, color="#1f77b4", stroke="white", strokeWidth=2)
        .encode(
            x=alt.X(f"{score_col}:Q", scale=alt.Scale(domain=digital_x_domain)),
            y=alt.Y("y:Q", axis=None),
            tooltip=[
                alt.Tooltip(f"{name_col}:N", title="VNB"),
                alt.Tooltip(f"{score_col}:Q", title=label, format=".2f"),
            ],
        )
    )

    st.altair_chart(
        (line + all_points + selected_point).properties(height=100),
        use_container_width=True,
    )
