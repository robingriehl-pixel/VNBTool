from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "output" / "df_data.csv"
BESS_DATA_PATH = BASE_DIR / "output" / "df_bess_data.csv"
OVERVIEW_DATA_PATH = BASE_DIR / "output" / "df_overview.csv"
RAW_BESS_INPUT_PATH = BASE_DIR / "input" / "mstr_bess_50kW_all.csv"


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


@st.cache_data
def load_raw_bess_input() -> pd.DataFrame:
    if not RAW_BESS_INPUT_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(RAW_BESS_INPUT_PATH, sep=";", encoding="utf-8-sig")


@st.cache_data
def load_overview_data() -> pd.DataFrame:
    if not OVERVIEW_DATA_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(OVERVIEW_DATA_PATH, sep=";", encoding="utf-8-sig")


def read_csv_with_mtime(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return _read_csv_with_mtime(path, path.stat().st_mtime)


@st.cache_data
def _read_csv_with_mtime(path: Path, _mtime: float) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", encoding="utf-8-sig")


st.set_page_config(
    page_title="VNB Dashboard",
    page_icon="V",
    layout="wide",
)

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

    [data-testid="stSegmentedControl"] {
        margin-bottom: 1rem;
    }

    div.stButton > button {
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

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        border-color: rgba(147, 197, 253, 0.95);
        color: white;
        box-shadow: 0 0 0 1px rgba(147, 197, 253, 0.25), 0 12px 30px rgba(37, 99, 235, 0.35);
    }

    div.stButton > button[kind="secondary"] {
        background: rgba(22, 27, 38, 0.78);
        border-color: rgba(148, 163, 184, 0.22);
        color: #e5e7eb;
    }

    .bess-card {
        background: rgba(22, 27, 38, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 1rem 1rem 1.1rem 1rem;
        min-height: 210px;
        height: 100%;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
        display: flex;
        flex-direction: column;
    }

    .bess-card-title {
        font-size: 0.98rem;
        font-weight: 700;
        line-height: 1.35;
        color: #f8fafc;
        margin-bottom: 0.55rem;
    }

    .bess-card-meta {
        font-size: 0.88rem;
        color: #cbd5e1;
        margin-bottom: 0.3rem;
    }

    .bess-bubble-wrap {
        margin-top: auto;
        padding-top: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .bess-bubble {
        border-radius: 999px;
        background: radial-gradient(circle at 30% 30%, #93c5fd, #2563eb 60%, #1d4ed8 100%);
        flex: 0 0 auto;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.28);
    }

    [data-testid="column"] > div:has(.bess-card) {
        padding: 0.35rem 0.45rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

df_data = read_csv_with_mtime(DATA_PATH)
df_bess_data = read_csv_with_mtime(BESS_DATA_PATH)
df_overview = read_csv_with_mtime(OVERVIEW_DATA_PATH)
df_bess_raw = read_csv_with_mtime(RAW_BESS_INPUT_PATH)

if "betriebsstatus" in df_bess_data.columns:
    df_bess_data_active = df_bess_data[
        df_bess_data["betriebsstatus"].astype(str).str.strip().eq("In Betrieb")
    ].copy()
else:
    df_bess_data_active = df_bess_data.copy()

if "Betriebs-Status" in df_bess_raw.columns:
    df_bess_raw_active = df_bess_raw[
        df_bess_raw["Betriebs-Status"].astype(str).str.strip().eq("In Betrieb")
    ].copy()
else:
    df_bess_raw_active = df_bess_raw.copy()

st.title("Voltpark VNB Tool")
st.markdown("<div style='height: 1.1rem;'></div>", unsafe_allow_html=True)

if df_data.empty:
    st.warning("Keine Daten in 'output/df_data.csv' gefunden.")
    st.stop()

if not df_overview.empty:
    st.markdown("---")
    st.header("Prognosen für Regionalszenarien")

    valid_regions = ["Nord", "Ost", "Mitte", "West", "Südwest", "Bayern"]

    df_overview_clean = df_overview.copy()
    df_overview_clean["Planungsregion"] = (
        df_overview_clean["Planungsregion"].astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.replace("Bayern (Hinweis unten)", "Bayern", regex=False)
        .str.strip()
    )
    df_overview_clean = df_overview_clean[
        df_overview_clean["Planungsregion"].isin(valid_regions)
    ].copy()

    overview_year_cols = {
        2024: "Verteilnetzbetreiber_Bestand_2024.0",
        2030: "Verteilnetzbetreiber_Prognosen_2030.0",
        2035: "Verteilnetzbetreiber_Prognosen_2035.0",
        2045: "Verteilnetzbetreiber_Prognosen_2045.0",
    }
    year_lookup = {column: year for year, column in overview_year_cols.items()}

    st.subheader("Technologievergleich innerhalb einer Planungsregion")
    st.caption("Regionalszenarien der VNB 2025")

    region_options = (
        df_overview_clean["Planungsregion"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    if "dashboard_selected_region" not in st.session_state:
        st.session_state.dashboard_selected_region = (
            "Nord" if "Nord" in region_options else region_options[0]
        )

    st.caption("Planungsregion")
    for idx, region_name in enumerate(region_options):
        if idx % 3 == 0:
            region_cols = st.columns(3)
        with region_cols[idx % 3]:
            if st.button(
                region_name,
                use_container_width=True,
                key=f"dashboard_region_{idx}",
                type=(
                    "primary"
                    if st.session_state.dashboard_selected_region == region_name
                    else "secondary"
                ),
            ):
                st.session_state.dashboard_selected_region = region_name
                st.rerun()

    selected_region = st.session_state.dashboard_selected_region

    category_patterns = {
        "Photovoltaik": r"Photovoltaik",
        "Windenergie": r"Windenergie",
        "Konventionelle Kraftwerke": r"Konventionelle Kraftwerke",
        "Kleinbatteriespeicher": r"Kleinbatteriespeicher",
        "Großbatteriespeicher": r"Großbatteriespeicher|Grossbatteriespeicher",
    }

    region_compare_df = df_overview_clean.loc[
        df_overview_clean["Planungsregion"].eq(selected_region),
        ["Planungsregion", "Anlagenart", *overview_year_cols.values()],
    ].copy()

    region_compare_frames = []
    for label, pattern in category_patterns.items():
        subset = region_compare_df.loc[
            region_compare_df["Anlagenart"].astype(str).str.contains(
                pattern, case=False, na=False
            )
        ].copy()
        if subset.empty:
            continue

        subset = subset.melt(
            id_vars=["Planungsregion", "Anlagenart"],
            value_vars=list(overview_year_cols.values()),
            var_name="year_col",
            value_name="value",
        )
        subset["year"] = subset["year_col"].map(year_lookup)
        subset["value"] = pd.to_numeric(subset["value"], errors="coerce")
        subset["category_group"] = label
        region_compare_frames.append(subset)

    if region_compare_frames:
        region_compare_long = pd.concat(region_compare_frames, ignore_index=True)
        region_compare_long = (
            region_compare_long.groupby(["year", "category_group"], as_index=False)["value"]
            .sum()
            .dropna(subset=["value"])
        )

        region_compare_chart = (
            alt.Chart(region_compare_long)
            .mark_line(point=True, strokeWidth=3)
            .encode(
                x=alt.X("year:O", title="Jahr"),
                y=alt.Y("value:Q", title="Leistung / Prognosewert"),
                color=alt.Color("category_group:N", title="Kategorie"),
                tooltip=[
                    alt.Tooltip("category_group:N", title="Kategorie"),
                    alt.Tooltip("year:O", title="Jahr"),
                    alt.Tooltip("value:Q", title="Wert", format=",.2f"),
                ],
            )
            .properties(height=420)
        )

        st.altair_chart(region_compare_chart, use_container_width=True)

    st.subheader("Technologiemix innerhalb einer Planungsregion")
    st.caption("Regionalszenarien der VNB 2025")

    mix_region_options = region_options

    if "dashboard_mix_region" not in st.session_state:
        st.session_state.dashboard_mix_region = (
            "Nord" if "Nord" in mix_region_options else mix_region_options[0]
        )

    st.caption("Planungsregion für Technologiemix")
    for idx, region_name in enumerate(mix_region_options):
        if idx % 3 == 0:
            mix_region_cols = st.columns(3)
        with mix_region_cols[idx % 3]:
            if st.button(
                region_name,
                use_container_width=True,
                key=f"dashboard_mix_region_{idx}",
                type=(
                    "primary"
                    if st.session_state.dashboard_mix_region == region_name
                    else "secondary"
                ),
            ):
                st.session_state.dashboard_mix_region = region_name
                st.rerun()

    selected_mix_region = st.session_state.dashboard_mix_region

    mix_category_patterns = {
        "Photovoltaik": r"Photovoltaik",
        "Windenergie": r"Windenergie",
        "Sonstige erneuerbare Erzeugung": r"Sonstige erneuerbare Erzeugung",
        "Konventionelle Kraftwerke": r"Konventionelle Kraftwerke",
    }

    region_mix_df = df_overview_clean.loc[
        df_overview_clean["Planungsregion"].eq(selected_mix_region),
        ["Planungsregion", "Anlagenart", *overview_year_cols.values()],
    ].copy()

    mix_frames = []
    for label, pattern in mix_category_patterns.items():
        subset = region_mix_df.loc[
            region_mix_df["Anlagenart"].astype(str).str.contains(
                pattern, case=False, na=False
            )
        ].copy()
        if subset.empty:
            continue

        subset = subset.melt(
            id_vars=["Planungsregion", "Anlagenart"],
            value_vars=list(overview_year_cols.values()),
            var_name="year_col",
            value_name="value",
        )
        subset["year"] = subset["year_col"].map(year_lookup)
        subset["value"] = pd.to_numeric(subset["value"], errors="coerce")
        subset["category_group"] = label
        mix_frames.append(subset)

    if mix_frames:
        region_mix_long = pd.concat(mix_frames, ignore_index=True)
        region_mix_long = (
            region_mix_long.groupby(["year", "category_group"], as_index=False)["value"]
            .sum()
            .dropna(subset=["value"])
        )

        mix_chart = (
            alt.Chart(region_mix_long)
            .transform_joinaggregate(year_total="sum(value)", groupby=["year"])
            .transform_calculate(share="datum.value / datum.year_total")
            .mark_bar()
            .encode(
                x=alt.X("year:O", title="Jahr"),
                y=alt.Y(
                    "value:Q",
                    title="Anteil",
                    stack="normalize",
                    axis=alt.Axis(format="%"),
                ),
                color=alt.Color(
                    "category_group:N",
                    title="Kategorie",
                    scale=alt.Scale(
                        domain=[
                            "Photovoltaik",
                            "Windenergie",
                            "Sonstige erneuerbare Erzeugung",
                            "Konventionelle Kraftwerke",
                        ],
                        range=[
                            "#facc15",
                            "#2563eb",
                            "#166534",
                            "#8b5e34",
                        ],
                    ),
                ),
                tooltip=[
                    alt.Tooltip("category_group:N", title="Kategorie"),
                    alt.Tooltip("year:O", title="Jahr"),
                    alt.Tooltip("value:Q", title="Wert", format=",.2f"),
                    alt.Tooltip("share:Q", title="Anteil", format=".1%"),
                ],
            )
            .properties(height=420)
        )

        st.altair_chart(mix_chart, use_container_width=True)

    st.subheader("Erneuerbare Erzeugung nach Planungsregion")
    st.caption("Regionalszenarien der VNB 2025")

    generation_df = df_overview_clean[
        ["Planungsregion", "Anlagenart", *overview_year_cols.values()]
    ].copy()

    generation_category_patterns = {
        "Erneuerbare Erzeugung": (
            r"Photovoltaik|Windenergie|Sonstige erneuerbare Erzeugung"
        ),
    }

    generation_frames = []
    for label, pattern in generation_category_patterns.items():
        subset = generation_df.loc[
            generation_df["Anlagenart"].astype(str).str.contains(
                pattern, case=False, na=False
            )
        ].copy()
        if subset.empty:
            continue

        subset = subset.melt(
            id_vars=["Planungsregion", "Anlagenart"],
            value_vars=list(overview_year_cols.values()),
            var_name="year_col",
            value_name="value",
        )
        subset["year"] = subset["year_col"].map(year_lookup)
        subset["value"] = pd.to_numeric(subset["value"], errors="coerce")
        subset["series"] = label
        generation_frames.append(subset)

    if generation_frames:
        generation_long = pd.concat(generation_frames, ignore_index=True)
        generation_long = (
            generation_long.groupby(["Planungsregion", "year", "series"], as_index=False)["value"]
            .sum()
            .dropna(subset=["value"])
        )

        generation_chart = (
            alt.Chart(generation_long)
            .mark_line(point=True, strokeWidth=3)
            .encode(
                x=alt.X("year:O", title="Jahr"),
                y=alt.Y("value:Q", title="Leistung / Prognosewert"),
                color=alt.Color(
                    "Planungsregion:N",
                    title="Planungsregion",
                ),
                tooltip=[
                    alt.Tooltip("Planungsregion:N", title="Planungsregion"),
                    alt.Tooltip("series:N", title="Reihe"),
                    alt.Tooltip("year:O", title="Jahr"),
                    alt.Tooltip("value:Q", title="Wert", format=",.2f"),
                ],
            )
            .properties(height=420)
        )

        st.altair_chart(generation_chart, use_container_width=True)

    st.subheader("Batteriespeicher nach Planungsregion")
    st.caption("Regionalszenarien der VNB 2025")

    overview_bess_df = df_overview_clean.loc[
        df_overview_clean["Anlagenart"].astype(str).str.contains(
            "Großbatteriespeicher|Grossbatteriespeicher|Kleinbatteriespeicher",
            case=False,
            na=False,
        ),
        ["Planungsregion", "Anlagenart", *overview_year_cols.values()],
    ].copy()

    overview_bess_long = overview_bess_df.melt(
        id_vars=["Planungsregion"],
        value_vars=list(overview_year_cols.values()),
        var_name="year_col",
        value_name="value",
    )

    overview_bess_long["year"] = overview_bess_long["year_col"].map(year_lookup)
    overview_bess_long["value"] = pd.to_numeric(
        overview_bess_long["value"], errors="coerce"
    )
    overview_bess_long = (
        overview_bess_long.dropna(subset=["value", "year"])
        .groupby(["Planungsregion", "year"], as_index=False)["value"]
        .sum()
    )

    overview_bess_chart = (
        alt.Chart(overview_bess_long)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("year:O", title="Jahr"),
            y=alt.Y("value:Q", title="Batteriespeicher gesamt (MW)"),
            color=alt.Color("Planungsregion:N", title="Planungsregion"),
            tooltip=[
                alt.Tooltip("Planungsregion:N", title="Planungsregion"),
                alt.Tooltip("year:O", title="Jahr"),
                alt.Tooltip("value:Q", title="Batteriespeicher gesamt", format=",.2f"),
            ],
        )
        .properties(height=420)
    )

    st.altair_chart(overview_bess_chart, use_container_width=True)

    if not df_bess_data_active.empty:
        st.subheader("Größte BESS-Einheiten")

        if not df_bess_raw_active.empty:
            top_bess_units = df_bess_raw_active[
                [
                    "MaStR-Nr. des Anschluss-Netzbetreibers",
                    "Name des Anschluss-Netzbetreibers",
                    "Anzeige-Name der Einheit",
                    "MaStR-Nr. der Einheit",
                    "Bruttoleistung der Einheit",
                    "Inbetriebnahmedatum der Einheit",
                ]
            ].rename(
                columns={
                    "MaStR-Nr. des Anschluss-Netzbetreibers": "keys",
                    "Name des Anschluss-Netzbetreibers": "netzbetreiber_name",
                    "Anzeige-Name der Einheit": "einheit_name",
                    "MaStR-Nr. der Einheit": "einheit_mastr",
                    "Bruttoleistung der Einheit": "bruttoleistung_einheit",
                    "Inbetriebnahmedatum der Einheit": "inbetriebnahme_datum",
                }
            ).copy()
        else:
            top_bess_units = df_bess_data_active[
                [
                    "keys",
                    "netzbetreiber_name",
                    "betriebsstatus",
                    "bruttoleistung_einheit",
                    "inbetriebnahme_datum",
                ]
            ].copy()

        top_bess_units = top_bess_units.merge(
            df_data[["MSTR_key", "vnb_names"]].dropna().drop_duplicates(),
            left_on="keys",
            right_on="MSTR_key",
            how="left",
        )

        top_bess_units["bruttoleistung_kw"] = pd.to_numeric(
            top_bess_units["bruttoleistung_einheit"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False),
            errors="coerce",
        )
        top_bess_units["parsed_date"] = pd.to_datetime(
            top_bess_units["inbetriebnahme_datum"],
            format="%d.%m.%Y",
            errors="coerce",
        )

        top_bess_units = (
            top_bess_units.dropna(subset=["bruttoleistung_kw"])
            .sort_values("bruttoleistung_kw", ascending=False)
            .head(8)
            .copy()
        )

        if not top_bess_units.empty:
            max_power = top_bess_units["bruttoleistung_kw"].max()

            for start_idx in range(0, len(top_bess_units), 4):
                card_cols = st.columns(4)
                chunk = top_bess_units.iloc[start_idx:start_idx + 4]

                for col, (_, row) in zip(card_cols, chunk.iterrows()):
                    bubble_size_px = (
                        max(18, min(72, (row["bruttoleistung_kw"] / max_power) * 72))
                        if max_power
                        else 18
                    )
                    date_text = (
                        row["parsed_date"].strftime("%d.%m.%Y")
                        if pd.notna(row["parsed_date"])
                        else str(row.get("inbetriebnahme_datum", ""))
                    )
                    name_text = (
                        row.get("einheit_name")
                        if pd.notna(row.get("einheit_name"))
                        else (
                            row.get("vnb_names")
                            if pd.notna(row.get("vnb_names"))
                            else row.get("keys", "")
                        )
                    )
                    netzbetreiber_text = str(
                        row.get("netzbetreiber_name", row.get("vnb_names", ""))
                    )
                    netzbetreiber_text = (
                        pd.Series([netzbetreiber_text])
                        .str.replace(r"\s*\([^)]*\)\s*$", "", regex=True)
                        .iloc[0]
                    )

                    col.markdown(
                        f"""
                        <div class="bess-card">
                            <div class="bess-card-title">{name_text}</div>
                            <div class="bess-card-meta"><strong>Inbetriebnahme:</strong> {date_text}</div>
                            <div class="bess-card-meta"><strong>Netzbetreiber:</strong> {netzbetreiber_text}</div>
                            <div class="bess-bubble-wrap">
                                <div class="bess-bubble" style="width:{bubble_size_px:.0f}px; height:{bubble_size_px:.0f}px;"></div>
                                <div class="bess-card-meta"><strong>Leistung:</strong> {row["bruttoleistung_kw"]:,.0f} kW</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

st.subheader("Übersicht nach Spannungsebene")

level_summary = {
    "NS": {
        "mask": df_data["vnb_vlevels"].astype(str).str.contains(r"\bNS\b", na=False),
        "length_col": "length_ns",
    },
    "MS": {
        "mask": df_data["vnb_vlevels"].astype(str).str.contains(r"\bMS\b", na=False),
        "length_col": "length_ms",
    },
    "HS": {
        "mask": df_data["vnb_vlevels"].astype(str).str.contains(r"\bHS\b", na=False),
        "length_col": "length_hs",
    },
}

col_ns, col_ms, col_hs = st.columns(3)

for column, level in zip((col_ns, col_ms, col_hs), ("NS", "MS", "HS")):
    mask = level_summary[level]["mask"]
    length_col = level_summary[level]["length_col"]
    vnb_count = int(df_data.loc[mask, "keys"].nunique()) if "keys" in df_data.columns else 0
    total_length = pd.to_numeric(
        df_data.loc[mask, length_col], errors="coerce"
    ).fillna(0).sum()

    with column:
        st.markdown(f"### {level}")
        st.metric("VNB", vnb_count)
        st.metric("Stromkreislänge", f"{total_length:,.0f} km")

st.subheader("Top 20 VNB nach Stromkreislänge")
st.caption("Erhebung Stand 2024")

length_options = {
    "NS": "length_ns",
    "MS": "length_ms",
    "HS": "length_hs",
}

selected_level = st.segmented_control(
    "Spannungsebene",
    options=list(length_options.keys()),
    default="NS",
)

length_col = length_options[selected_level]

top_length_df = (
    df_data[["vnb_names", length_col]]
    .dropna(subset=["vnb_names"])
    .copy()
    .assign(**{length_col: lambda frame: pd.to_numeric(frame[length_col], errors="coerce")})
    .dropna(subset=[length_col])
    .sort_values(length_col, ascending=False)
    .head(20)
)

chart = (
    alt.Chart(top_length_df)
    .mark_bar()
    .encode(
        x=alt.X(f"{length_col}:Q", title=f"Stromkreislänge {selected_level}"),
        y=alt.Y(
            "vnb_names:N",
            sort=alt.EncodingSortField(field=length_col, order="descending"),
            title="VNB",
        ),
        tooltip=[
            alt.Tooltip("vnb_names:N", title="VNB"),
            alt.Tooltip(
                f"{length_col}:Q",
                title=f"Stromkreislänge {selected_level}",
                format=",.2f",
            ),
        ],
    )
    .properties(height=600)
)

st.altair_chart(chart, use_container_width=True)

st.subheader("Top 20 VNB nach Summenleistung der Speicher-Anschlussbegehren")
st.caption("Erhebung Stand 2024")

storage_sum_options = {
    "NS": "sum_storage_requests_ns",
    "MS": "sum_storage_requests_ms",
    "HS": "sum_storage_requests_hs",
}

selected_storage_level = st.segmented_control(
    "Spannungsebene Speicher",
    options=list(storage_sum_options.keys()),
    default="NS",
    key="storage_sum_level",
)

storage_sum_col = storage_sum_options[selected_storage_level]

top_storage_df = (
    df_data[["vnb_names", storage_sum_col]]
    .dropna(subset=["vnb_names"])
    .copy()
    .assign(
        **{
            storage_sum_col: lambda frame: pd.to_numeric(
                frame[storage_sum_col], errors="coerce"
            )
        }
    )
    .dropna(subset=[storage_sum_col])
    .sort_values(storage_sum_col, ascending=False)
    .head(20)
)

storage_chart = (
    alt.Chart(top_storage_df)
    .mark_bar()
    .encode(
        x=alt.X(
            f"{storage_sum_col}:Q",
            title=f"Summenleistung Speicher-Anschlussbegehren {selected_storage_level}",
        ),
        y=alt.Y(
            "vnb_names:N",
            sort=alt.EncodingSortField(field=storage_sum_col, order="descending"),
            title="VNB",
        ),
        tooltip=[
            alt.Tooltip("vnb_names:N", title="VNB"),
            alt.Tooltip(
                f"{storage_sum_col}:Q",
                title=f"Summenleistung {selected_storage_level}",
                format=",.2f",
            ),
        ],
    )
    .properties(height=600)
)

st.altair_chart(storage_chart, use_container_width=True)

if not df_bess_data_active.empty and "MSTR_key" in df_data.columns:
    st.subheader("Top 20 VNB nach BESS-Bruttoleistung")
    st.caption("Marktstammdatenregister, Anlagen über 50 kW, Stand März 2026")

    bess_chart_df = df_bess_data_active[["keys", "bruttoleistung_einheit"]].copy()
    bess_chart_df["bruttoleistung_einheit"] = (
        bess_chart_df["bruttoleistung_einheit"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    bess_chart_df["bruttoleistung_einheit"] = pd.to_numeric(
        bess_chart_df["bruttoleistung_einheit"], errors="coerce"
    )

    bess_chart_df = (
        bess_chart_df.dropna(subset=["keys", "bruttoleistung_einheit"])
        .groupby("keys", as_index=False)["bruttoleistung_einheit"]
        .sum()
        .merge(
            df_data[["MSTR_key", "vnb_names"]].dropna().drop_duplicates(),
            left_on="keys",
            right_on="MSTR_key",
            how="left",
        )
        .dropna(subset=["vnb_names"])
        .sort_values("bruttoleistung_einheit", ascending=False)
        .head(20)
    )

    bess_chart = (
        alt.Chart(bess_chart_df)
        .mark_bar()
        .encode(
            x=alt.X("bruttoleistung_einheit:Q", title="BESS-Bruttoleistung gesamt (kW)"),
            y=alt.Y(
                "vnb_names:N",
                sort=alt.EncodingSortField(
                    field="bruttoleistung_einheit",
                    order="descending",
                ),
                title="VNB",
            ),
            tooltip=[
                alt.Tooltip("vnb_names:N", title="VNB"),
                alt.Tooltip(
                    "bruttoleistung_einheit:Q",
                    title="BESS-Bruttoleistung gesamt",
                    format=",.0f",
                ),
            ],
        )
        .properties(height=600)
    )

    st.altair_chart(bess_chart, use_container_width=True)

st.subheader("Top 20 VNB nach Anschlussdauer Speicher mit Vergleich zu EE")
st.caption("Erhebung Stand 2024")

duration_options = {
    "NS": ("duration_storage_ns", "duration_ee_ns"),
    "MS": ("duration_storage_ms", "duration_ee_ms"),
    "HS": ("duration_storage_hs", "duration_ee_hs"),
}

selected_duration_level = st.segmented_control(
    "Spannungsebene Anschlussdauer",
    options=list(duration_options.keys()),
    default="NS",
    key="duration_level",
)

storage_duration_col, ee_duration_col = duration_options[selected_duration_level]

duration_df = (
    df_data[["vnb_names", storage_duration_col, ee_duration_col]]
    .dropna(subset=["vnb_names"])
    .copy()
    .assign(
        **{
            storage_duration_col: lambda frame: pd.to_numeric(
                frame[storage_duration_col], errors="coerce"
            ),
            ee_duration_col: lambda frame: pd.to_numeric(
                frame[ee_duration_col], errors="coerce"
            ),
        }
    )
    .dropna(subset=[storage_duration_col])
    .sort_values(storage_duration_col, ascending=False)
    .head(20)
)

duration_long_df = duration_df.melt(
    id_vars="vnb_names",
    value_vars=[storage_duration_col, ee_duration_col],
    var_name="metric",
    value_name="duration_value",
)

duration_long_df["series"] = duration_long_df["metric"].map(
    {
        storage_duration_col: "Speicher",
        ee_duration_col: "EE-Anlagen",
    }
)

series_order = ["Speicher", "EE-Anlagen"]
vnb_order = duration_df["vnb_names"].tolist()

duration_chart = (
    alt.Chart(duration_long_df)
    .mark_bar()
    .encode(
        x=alt.X(
            "duration_value:Q",
            title=f"Anschlussdauer {selected_duration_level}",
        ),
        y=alt.Y(
            "vnb_names:N",
            sort=vnb_order,
            title="VNB",
        ),
        color=alt.Color("series:N", title="Reihe", sort=series_order),
        yOffset=alt.YOffset("series:N", sort=series_order),
        tooltip=[
            alt.Tooltip("vnb_names:N", title="VNB"),
            alt.Tooltip("series:N", title="Typ"),
            alt.Tooltip("duration_value:Q", title="Dauer", format=",.2f"),
        ],
    )
    .properties(height=600)
)

st.altair_chart(duration_chart, use_container_width=True)

st.subheader("Netzlänge, Fläche und Speicher-Anschlussbegehren")
st.caption("Erhebung Stand 2024")

bubble_options = {
    "NS": ("length_ns", "area_ns", "sum_storage_requests_ns"),
    "MS": ("length_ms", "area_ms", "sum_storage_requests_ms"),
    "HS": ("length_hs", "area_hs", "sum_storage_requests_hs"),
}

selected_bubble_level = st.segmented_control(
    "Spannungsebene Bubble Chart",
    options=list(bubble_options.keys()),
    default="NS",
    key="bubble_level",
)

length_bubble_col, area_bubble_col, size_bubble_col = bubble_options[selected_bubble_level]

bubble_df = (
    df_data[["vnb_names", length_bubble_col, area_bubble_col, size_bubble_col]]
    .dropna(subset=["vnb_names"])
    .copy()
    .assign(
        **{
            length_bubble_col: lambda frame: pd.to_numeric(
                frame[length_bubble_col], errors="coerce"
            ),
            area_bubble_col: lambda frame: pd.to_numeric(
                frame[area_bubble_col], errors="coerce"
            ),
            size_bubble_col: lambda frame: pd.to_numeric(
                frame[size_bubble_col], errors="coerce"
            ),
        }
    )
    .dropna(subset=[length_bubble_col, area_bubble_col, size_bubble_col])
)

bubble_chart = (
    alt.Chart(bubble_df)
    .mark_circle(opacity=0.7)
    .encode(
        x=alt.X(f"{length_bubble_col}:Q", title=f"Stromkreislänge {selected_bubble_level}"),
        y=alt.Y(f"{area_bubble_col}:Q", title=f"Fläche {selected_bubble_level}"),
        size=alt.Size(
            f"{size_bubble_col}:Q",
            title=f"Summenleistung Speicher {selected_bubble_level}",
            scale=alt.Scale(range=[40, 1200]),
        ),
        tooltip=[
            alt.Tooltip("vnb_names:N", title="VNB"),
            alt.Tooltip(
                f"{length_bubble_col}:Q",
                title=f"Stromkreislänge {selected_bubble_level}",
                format=",.2f",
            ),
            alt.Tooltip(
                f"{area_bubble_col}:Q",
                title=f"Fläche {selected_bubble_level}",
                format=",.2f",
            ),
            alt.Tooltip(
                f"{size_bubble_col}:Q",
                title=f"Summenleistung Speicher {selected_bubble_level}",
                format=",.2f",
            ),
        ],
    )
    .properties(height=600)
)

st.altair_chart(bubble_chart, use_container_width=True)

st.subheader("Stromkreislänge vs. Summenleistung Speicher-Anschlussbegehren")
st.caption("Erhebung Stand 2024")

scatter_storage_options = {
    "NS": ("length_ns", "count_storage_requests_ns", "sum_storage_requests_ns"),
    "MS": ("length_ms", "count_storage_requests_ms", "sum_storage_requests_ms"),
    "HS": ("length_hs", "count_storage_requests_hs", "sum_storage_requests_hs"),
}

selected_scatter_storage_level = st.segmented_control(
    "Spannungsebene Scatter Stromkreislänge / Speicher",
    options=list(scatter_storage_options.keys()),
    default="NS",
    key="scatter_storage_level",
)

scatter_length_col, scatter_count_col, scatter_sum_col = scatter_storage_options[selected_scatter_storage_level]

scatter_storage_df = (
    df_data[["vnb_names", scatter_length_col, scatter_count_col, scatter_sum_col]]
    .copy()
    .assign(
        **{
            scatter_length_col: lambda frame: pd.to_numeric(
                frame[scatter_length_col], errors="coerce"
            ),
            scatter_count_col: lambda frame: pd.to_numeric(
                frame[scatter_count_col], errors="coerce"
            ),
            scatter_sum_col: lambda frame: pd.to_numeric(
                frame[scatter_sum_col], errors="coerce"
            ),
        }
    )
    .dropna(subset=[scatter_length_col, scatter_count_col, scatter_sum_col, "vnb_names"])
)

scatter_storage_chart = (
    alt.Chart(scatter_storage_df)
    .mark_circle(opacity=0.55, color="#1f77b4")
    .encode(
        x=alt.X(
            f"{scatter_length_col}:Q",
            title=f"Stromkreislänge {selected_scatter_storage_level} (km)",
        ),
        y=alt.Y(
            f"{scatter_count_col}:Q",
            title=f"Count Storage Requests {selected_scatter_storage_level}",
        ),
        size=alt.Size(
            f"{scatter_sum_col}:Q",
            title=f"Sum Storage Requests {selected_scatter_storage_level} (kW)",
            scale=alt.Scale(range=[60, 1400]),
        ),
        tooltip=[
            alt.Tooltip("vnb_names:N", title="VNB"),
            alt.Tooltip(
                f"{scatter_length_col}:Q",
                title=f"Stromkreislänge {selected_scatter_storage_level}",
                format=",.0f",
            ),
            alt.Tooltip(
                f"{scatter_count_col}:Q",
                title=f"Count Storage Requests {selected_scatter_storage_level}",
                format=",.0f",
            ),
            alt.Tooltip(
                f"{scatter_sum_col}:Q",
                title=f"Sum Storage Requests {selected_scatter_storage_level}",
                format=",.0f",
            ),
        ],
    )
    .properties(height=360)
)

st.altair_chart(scatter_storage_chart, use_container_width=True)
