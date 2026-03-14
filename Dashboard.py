from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
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


st.set_page_config(
    page_title="VNB Dashboard",
    page_icon="V",
    layout="wide",
)

df_data = load_data()
df_bess_data = load_bess_data()

st.title("VNB Dashboard")
st.caption("Uebersicht ueber alle geladenen VNB-Daten")

if df_data.empty:
    st.warning("Keine Daten in 'output/df_data.csv' gefunden.")
    st.stop()

st.subheader("Uebersicht nach Spannungsebene")

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
        st.metric("Stromkreislaenge", f"{total_length:,.0f} km")

st.subheader("Top 20 VNB nach Stromkreislaenge")

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
        x=alt.X(f"{length_col}:Q", title=f"Stromkreislaenge {selected_level}"),
        y=alt.Y(
            "vnb_names:N",
            sort=alt.EncodingSortField(field=length_col, order="descending"),
            title="VNB",
        ),
        tooltip=[
            alt.Tooltip("vnb_names:N", title="VNB"),
            alt.Tooltip(
                f"{length_col}:Q",
                title=f"Stromkreislaenge {selected_level}",
                format=",.2f",
            ),
        ],
    )
    .properties(height=600)
)

st.altair_chart(chart, use_container_width=True)

st.subheader("Top 20 VNB nach Summenleistung der Speicher-Anschlussbegehren")

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

if not df_bess_data.empty and "MSTR_key" in df_data.columns:
    st.subheader("Top 20 VNB nach BESS-Bruttoleistung")

    bess_chart_df = df_bess_data[["keys", "bruttoleistung_einheit"]].copy()
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

st.subheader("Netzlaenge, Flaeche und Speicher-Anschlussbegehren")

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
        x=alt.X(f"{length_bubble_col}:Q", title=f"Stromkreislaenge {selected_bubble_level}"),
        y=alt.Y(f"{area_bubble_col}:Q", title=f"Flaeche {selected_bubble_level}"),
        size=alt.Size(
            f"{size_bubble_col}:Q",
            title=f"Summenleistung Speicher {selected_bubble_level}",
            scale=alt.Scale(range=[40, 1200]),
        ),
        tooltip=[
            alt.Tooltip("vnb_names:N", title="VNB"),
            alt.Tooltip(
                f"{length_bubble_col}:Q",
                title=f"Stromkreislaenge {selected_bubble_level}",
                format=",.2f",
            ),
            alt.Tooltip(
                f"{area_bubble_col}:Q",
                title=f"Flaeche {selected_bubble_level}",
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

st.subheader("Stromkreislaenge vs. Summenleistung Speicher-Anschlussbegehren")

scatter_storage_options = {
    "NS": ("length_ns", "count_storage_requests_ns", "sum_storage_requests_ns"),
    "MS": ("length_ms", "count_storage_requests_ms", "sum_storage_requests_ms"),
    "HS": ("length_hs", "count_storage_requests_hs", "sum_storage_requests_hs"),
}

selected_scatter_storage_level = st.segmented_control(
    "Spannungsebene Scatter Stromkreislaenge / Speicher",
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
            title=f"Stromkreislaenge {selected_scatter_storage_level} (km)",
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
                title=f"Stromkreislaenge {selected_scatter_storage_level}",
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
