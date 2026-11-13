import io
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# 1. PAGE SETUP & DATA VALIDATION
# --------------------------------------------------
st.set_page_config(page_title="Exploratory Data Analysis", page_icon="📊", layout="wide")

st.title("📊 Exploratory Data Analysis")
st.caption("Univariate, Bivariate, Numerical Analysis, and Export Final Dataset .")

if "data" not in st.session_state or st.session_state["data"].empty:
    st.warning("⚠️ Please upload and clean your dataset first.")
    st.stop()

df = st.session_state["data"]


# --------------------------------------------------
# 2. CACHED COMPUTATIONS & EXPORT HELPERS
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def classify_columns(data: pd.DataFrame):
    num_cols, cat_cols = [], []
    for col in data.columns:
        s = data[col]
        n_unique = s.nunique(dropna=True)
        if pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
            if n_unique <= 5:
                cat_cols.append(col)
            else:
                num_cols.append(col)
        elif n_unique <= 30:
            cat_cols.append(col)
    return num_cols, cat_cols


@st.cache_data(show_spinner=False)
def compute_correlation_matrix(data: pd.DataFrame, num_cols: list[str], cat_cols: list[str]):
    encode_df = data[num_cols + cat_cols].copy()
    for c in cat_cols:
        encode_df[c] = encode_df[c].astype(str)
    dummies = pd.get_dummies(encode_df, dtype=float)
    if dummies.shape[1] < 2:
        return pd.DataFrame()
    return dummies.corr()


@st.cache_data(show_spinner=False)
def prepare_export_buffers(data: pd.DataFrame):
    csv_bytes = data.to_csv(index=False).encode("utf-8")
    excel_buffer = io.BytesIO()
    excel_bytes = None

    for engine in ("openpyxl", "xlsxwriter"):
        try:
            with pd.ExcelWriter(excel_buffer, engine=engine) as writer:
                data.to_excel(writer, index=False, sheet_name="Processed_Data")
            excel_bytes = excel_buffer.getvalue()
            break
        except Exception:
            excel_buffer.seek(0)
            excel_buffer.truncate(0)

    return csv_bytes, excel_bytes


# --------------------------------------------------
# 3. EYE-CATCHING COLOR PALETTES & STYLING
# --------------------------------------------------
PALETTES = {
    "✨ Vibrant Neon (Recommended)": {
        "discrete": ["#6366F1", "#06B6D4", "#F43F5E", "#F59E0B", "#10B981", "#A855F7", "#EC4899"],
        "continuous": "Plasma"
    },
    "🌅 Sunset Glow": {
        "discrete": ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93", "#FF924C", "#52A675"],
        "continuous": "Sunsetdark"
    },
    "🌊 Oceanic Cyber": {
        "discrete": ["#00F5D4", "#00BBF9", "#FEE440", "#F15BB5", "#9B5DE5", "#38BDF8", "#FB7185"],
        "continuous": "Viridis"
    },
    "💎 Emerald & Gold": {
        "discrete": ["#10B981", "#F59E0B", "#3B82F6", "#EF4444", "#8B5CF6", "#14B8A6", "#F97316"],
        "continuous": "Tealgrn"
    }
}

top_col1, top_col2 = st.columns(2)
with top_col2:
    selected_theme = st.selectbox("Select Chart Color Theme", list(PALETTES.keys()), index=0)

ACTIVE_COLORS = PALETTES[selected_theme]["discrete"]
ACTIVE_SCALE = PALETTES[selected_theme]["continuous"]


def show_plot(fig):
    """Applies modern styling and renders the Plotly chart."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_x=0.01,
        title_font=dict(size=18),
        margin=dict(l=25, r=25, t=55, b=35),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        bargap=0.22,
        barcornerradius=6
    )
    st.plotly_chart(fig, use_container_width=True)


def show_insights(bullets: list[str]):
    """Renders generated statistical insights directly below a chart."""
    if bullets:
        st.info("**💡 Automated Chart Insights**\n" + "\n".join(f"- {b}" for b in bullets))


for section_key in ("uni_charts", "num_charts", "biv_charts"):
    if not st.session_state.get(section_key):
        st.session_state[section_key] = [0]


def add_chart(section_key: str):
    st.session_state[section_key].append(max(st.session_state[section_key], default=-1) + 1)


def remove_chart(section_key: str, chart_id: int):
    if len(st.session_state[section_key]) > 1:
        st.session_state[section_key].remove(chart_id)


# --------------------------------------------------
# 4. COLUMN SEPARATION & TARGET SELECTION
# --------------------------------------------------
numeric_cols, categorical_cols = classify_columns(df)

target_options = ["— None —"] + [c for c in categorical_cols if 2 <= df[c].nunique(dropna=True) <= 10]
saved_target = st.session_state.get("target_col")
default_idx = (
    target_options.index(saved_target)
    if saved_target in target_options
    else (1 if len(target_options) > 1 else 0)
)

with top_col1:
    target_choice = st.selectbox("Select Target Variable for Comparison", target_options, index=default_idx)

target = None if target_choice == "— None —" else target_choice
if target:
    st.session_state["target_col"] = target

feature_cats = [c for c in categorical_cols if c != target]


# --------------------------------------------------
# SECTION 1: UNIVARIATE ANALYSIS (CATEGORICAL)
# --------------------------------------------------
st.markdown("---")
h1, b1 = st.columns([4, 1])
h1.subheader("1. Univariate Analysis (Categorical Analysis)")
b1.button("➕ Add Chart", key="add_uni_btn", on_click=add_chart, args=("uni_charts",), use_container_width=True)

if feature_cats:
    for idx, cid in enumerate(st.session_state["uni_charts"]):
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 0.4])
            with c1:
                sel_cat = st.selectbox(
                    "Select Categorical Column",
                    feature_cats,
                    index=idx % len(feature_cats),
                    key=f"uni_col_{cid}"
                )
            with c2:
                uni_type = st.selectbox(
                    "Select Chart Type",
                    ["Column Chart", "Bar Chart", "Line Chart", "Donut Chart", "Pie Chart"],
                    key=f"uni_type_{cid}"
                )
            with c3:
                st.write("")
                if len(st.session_state["uni_charts"]) > 1:
                    st.button("🗑️", key=f"del_uni_{cid}", on_click=remove_chart, args=("uni_charts", cid))

            plot_df = df[[sel_cat] + ([target] if target else [])].dropna().astype(str)

            if target and uni_type in ("Column Chart", "Bar Chart", "Line Chart"):
                counts = plot_df.groupby([sel_cat, target]).size().reset_index(name="Count")
                color_col = target
            else:
                counts = plot_df[sel_cat].value_counts().reset_index()
                counts.columns = [sel_cat, "Count"]
                color_col = sel_cat

            if uni_type == "Column Chart":
                fig_uni = px.bar(
                    counts, x=sel_cat, y="Count", color=color_col, barmode="group",
                    text="Count", color_discrete_sequence=ACTIVE_COLORS,
                    title=f"Column Chart: {sel_cat}"
                )
                fig_uni.update_traces(textposition="outside", cliponaxis=False)
            elif uni_type == "Bar Chart":
                fig_uni = px.bar(
                    counts, y=sel_cat, x="Count", color=color_col, orientation="h",
                    barmode="group", text="Count", color_discrete_sequence=ACTIVE_COLORS,
                    title=f"Bar Chart: {sel_cat}"
                )
                fig_uni.update_traces(textposition="outside", cliponaxis=False)
            elif uni_type == "Line Chart":
                fig_uni = px.line(
                    counts, x=sel_cat, y="Count", color=target if target else None,
                    markers=True, color_discrete_sequence=ACTIVE_COLORS,
                    title=f"Line Chart: {sel_cat}"
                )
                fig_uni.update_traces(line=dict(width=3.5), marker=dict(size=10))
            else:
                pie_df = plot_df[sel_cat].value_counts().reset_index()
                pie_df.columns = [sel_cat, "Count"]
                hole_val = 0.48 if uni_type == "Donut Chart" else 0.0
                fig_uni = px.pie(
                    pie_df, names=sel_cat, values="Count", hole=hole_val,
                    color_discrete_sequence=ACTIVE_COLORS, title=f"{uni_type}: {sel_cat}"
                )
                fig_uni.update_traces(textinfo="percent+label", pull=[0.04] + [0] * (len(pie_df) - 1))

            show_plot(fig_uni)

            vc = plot_df[sel_cat].value_counts()
            uni_insights = []
            if not vc.empty:
                total = len(plot_df)
                uni_insights.append(
                    f"**Dominant Category:** `{vc.index[0]}` leads with **{vc.iloc[0]:,}** records (**{vc.iloc[0] / total * 100:.1f}%**), while `{vc.index[-1]}` is lowest with **{vc.iloc[-1]:,}** (**{vc.iloc[-1] / total * 100:.1f}%**)."
                )
                if target:
                    pos_cls = sorted(plot_df[target].unique())[-1]
                    rates = plot_df.groupby(sel_cat)[target].apply(lambda s: (s == pos_cls).mean() * 100).sort_values(ascending=False)
                    uni_insights.append(
                        f"**Target Concentration (`{target} = {pos_cls}`):** Highest in `{rates.index[0]}` (**{rates.iloc[0]:.1f}%**) and lowest in `{rates.index[-1]}` (**{rates.iloc[-1]:.1f}%**)."
                    )
            show_insights(uni_insights)
else:
    st.info("No categorical features available.")


# --------------------------------------------------
# SECTION 2: NUMERICAL ANALYSIS (DISTRIBUTIONS & RELATIONSHIPS)
# --------------------------------------------------
st.markdown("---")
h2, b2 = st.columns([4, 1])
h2.subheader("2. Numerical Analysis (Distributions & Relationships)")
b2.button("➕ Add Chart", key="add_num_btn", on_click=add_chart, args=("num_charts",), use_container_width=True)

if numeric_cols:
    num_opts = (
        ["Scatter Plot", "Column Chart", "Bar Chart", "Line Chart", "Heat Map"]
        if len(numeric_cols) >= 2
        else ["Column Chart", "Bar Chart", "Line Chart"]
    )
    for idx, cid in enumerate(st.session_state["num_charts"]):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 0.4])
            with c1:
                n_type = st.selectbox("Select Chart Type", num_opts, key=f"num_type_{cid}")
            with c2:
                x_num = st.selectbox(
                    "Primary Numerical Column (X)",
                    numeric_cols,
                    index=idx % len(numeric_cols),
                    key=f"num_x_{cid}"
                )
            with c3:
                needs_two = n_type in ("Scatter Plot", "Heat Map")
                if needs_two:
                    y_candidates = [c for c in numeric_cols if c != x_num]
                    y_num = st.selectbox("Secondary Numerical Column (Y)", y_candidates, key=f"num_y_{cid}")
                else:
                    y_num = None
                    st.selectbox("Secondary Numerical Column (Y)", ["— Not Required —"], disabled=True, key=f"num_y_dis_{cid}")
            with c4:
                st.write("")
                if len(st.session_state["num_charts"]) > 1:
                    st.button("🗑️", key=f"del_num_{cid}", on_click=remove_chart, args=("num_charts", cid))

            num_insights = []

            if not needs_two:
                s_clean = pd.to_numeric(df[x_num], errors="coerce").dropna()
                bins = pd.cut(s_clean, bins=10)
                bin_df = bins.value_counts().sort_index().reset_index()
                bin_df.columns = ["Range", "Count"]
                bin_df["Range"] = bin_df["Range"].astype(str)

                if n_type == "Column Chart":
                    fig_num = px.bar(
                        bin_df, x="Range", y="Count", color="Count",
                        color_continuous_scale=ACTIVE_SCALE, text="Count",
                        title=f"Column Chart (Distribution): {x_num}"
                    )
                    fig_num.update_traces(textposition="outside", cliponaxis=False)
                elif n_type == "Bar Chart":
                    fig_num = px.bar(
                        bin_df, y="Range", x="Count", orientation="h", color="Count",
                        color_continuous_scale=ACTIVE_SCALE, text="Count",
                        title=f"Bar Chart (Distribution): {x_num}"
                    )
                    fig_num.update_traces(textposition="outside", cliponaxis=False)
                else:
                    fig_num = px.line(
                        bin_df, x="Range", y="Count", markers=True,
                        color_discrete_sequence=[ACTIVE_COLORS[1]],
                        title=f"Line Chart (Distribution Trend): {x_num}"
                    )
                    fig_num.update_traces(line=dict(width=3.5), marker=dict(size=10, color=ACTIVE_COLORS[2]))

                show_plot(fig_num)

                if not s_clean.empty:
                    q25, q75 = s_clean.quantile(0.25), s_clean.quantile(0.75)
                    iqr = q75 - q25
                    skew = s_clean.skew()
                    shape = "right-skewed" if skew > 0.5 else ("left-skewed" if skew < -0.5 else "symmetric")
                    top_bin = bin_df.sort_values("Count", ascending=False).iloc[0]
                    num_insights.extend([
                        f"**Summary Statistics:** Mean = **{s_clean.mean():,.2f}**, Median = **{s_clean.median():,.2f}**, Std Dev = **{s_clean.std():,.2f}**, IQR = **{iqr:,.2f}**.",
                        f"**Distribution Shape:** `{x_num}` is **{shape}** (skewness = **{skew:.2f}**), with peak frequency in `{top_bin['Range']}` (**{top_bin['Count']:,}** records)."
                    ])
            else:
                pair_df = df[[x_num, y_num] + ([target] if target else [])].dropna().copy()
                if target:
                    pair_df[target] = pair_df[target].astype(str)

                if n_type == "Scatter Plot":
                    fig_num = px.scatter(
                        pair_df, x=x_num, y=y_num,
                        color=target if target else y_num,
                        color_discrete_sequence=ACTIVE_COLORS,
                        color_continuous_scale=ACTIVE_SCALE,
                        opacity=0.8, title=f"Scatter Plot: {x_num} vs. {y_num}"
                    )
                    fig_num.update_traces(marker=dict(size=8, line=dict(width=0.5, color="white")))
                else:
                    x_bins = pd.cut(pair_df[x_num], bins=6).astype(str)
                    y_bins = pd.cut(pair_df[y_num], bins=6).astype(str)
                    ctab = pd.crosstab(y_bins, x_bins)
                    fig_num = px.imshow(
                        ctab, text_auto=True, color_continuous_scale=ACTIVE_SCALE,
                        aspect="auto", title=f"Heat Map: {x_num} vs. {y_num}"
                    )

                show_plot(fig_num)

                if len(pair_df) >= 2:
                    r = pair_df[x_num].corr(pair_df[y_num])
                    strength = "strong" if abs(r) >= 0.6 else ("moderate" if abs(r) >= 0.3 else "weak")
                    direction = "positive" if r > 0 else "negative"
                    num_insights.append(
                        f"**Correlation Strength:** Pearson $r = {r:.3f}$, indicating a **{strength} {direction}** linear relationship ($R^2 = {r**2:.1%}$ variance explained)."
                    )
                    if target:
                        meds = pair_df.groupby(target)[[x_num, y_num]].median().round(2)
                        med_summary = " | ".join(
                            f"`{idx_val}`: {x_num}={row[x_num]}, {y_num}={row[y_num]}"
                            for idx_val, row in meds.iterrows()
                        )
                        num_insights.append(f"**Medians by `{target}`:** {med_summary}.")

            show_insights(num_insights)
else:
    st.info("No numerical columns available.")


# --------------------------------------------------
# SECTION 3: BIVARIATE ANALYSIS (FEATURE & COHORT COMPARISON)
# --------------------------------------------------
st.markdown("---")
h3, b3 = st.columns([4, 1])
h3.subheader("3. Bivariate Analysis (Feature & Cohort Comparison)")
b3.button("➕ Add Chart", key="add_biv_btn", on_click=add_chart, args=("biv_charts",), use_container_width=True)

if len(feature_cats) >= 2:
    for idx, cid in enumerate(st.session_state["biv_charts"]):
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([1.4, 1.4, 1.2, 1.4, 0.4])
            with c1:
                x_cat = st.selectbox(
                    "Primary Feature (X)",
                    feature_cats,
                    index=idx % len(feature_cats),
                    key=f"biv_x_{cid}"
                )
            with c2:
                hue_opts = [c for c in feature_cats if c != x_cat]
                hue_cat = st.selectbox("Secondary Feature (Group)", hue_opts, index=0, key=f"biv_hue_{cid}")
            with c3:
                if target:
                    t_classes = sorted(df[target].dropna().astype(str).unique())
                    cohort = st.selectbox(f"Filter {target}", ["All Records"] + t_classes, key=f"biv_coh_{cid}")
                else:
                    cohort = "All Records"
                    st.selectbox("Filter Cohort", ["All Records"], disabled=True, key=f"biv_coh_dis_{cid}")
            with c4:
                biv_type = st.selectbox(
                    "Select Chart Type",
                    ["Column Chart", "Bar Chart", "Line Chart", "Heat Map", "Scatter Plot", "Donut Chart", "Pie Chart"],
                    key=f"biv_type_{cid}"
                )
            with c5:
                st.write("")
                if len(st.session_state["biv_charts"]) > 1:
                    st.button("🗑️", key=f"del_biv_{cid}", on_click=remove_chart, args=("biv_charts", cid))

            sub_df = df if not (target and cohort != "All Records") else df[df[target].astype(str) == cohort]
            sub_df = sub_df[[x_cat, hue_cat]].dropna().astype(str)
            cohort_label = f"{target} = {cohort}" if (target and cohort != "All Records") else "All Records"

            if not sub_df.empty:
                biv_counts = sub_df.groupby([x_cat, hue_cat]).size().reset_index(name="Count")
                biv_counts["Pct"] = (
                    biv_counts["Count"] / biv_counts.groupby(x_cat)["Count"].transform("sum") * 100
                ).round(1)
                biv_counts["Combination"] = biv_counts[x_cat] + " | " + biv_counts[hue_cat]

                if biv_type == "Column Chart":
                    fig_biv = px.bar(
                        biv_counts, x=x_cat, y="Count", color=hue_cat, barmode="group",
                        text="Count", color_discrete_sequence=ACTIVE_COLORS,
                        title=f"Column Chart: {x_cat} by {hue_cat} ({cohort_label})"
                    )
                    fig_biv.update_traces(textposition="outside", cliponaxis=False)
                elif biv_type == "Bar Chart":
                    fig_biv = px.bar(
                        biv_counts, y=x_cat, x="Count", color=hue_cat, orientation="h",
                        barmode="group", text="Count", color_discrete_sequence=ACTIVE_COLORS,
                        title=f"Bar Chart: {x_cat} by {hue_cat} ({cohort_label})"
                    )
                    fig_biv.update_traces(textposition="outside", cliponaxis=False)
                elif biv_type == "Line Chart":
                    fig_biv = px.line(
                        biv_counts, x=x_cat, y="Count", color=hue_cat, markers=True,
                        color_discrete_sequence=ACTIVE_COLORS,
                        title=f"Line Chart: {x_cat} across {hue_cat} ({cohort_label})"
                    )
                    fig_biv.update_traces(line=dict(width=3.5), marker=dict(size=10))
                elif biv_type == "Heat Map":
                    ctab = pd.crosstab(sub_df[x_cat], sub_df[hue_cat])
                    fig_biv = px.imshow(
                        ctab, text_auto=True, color_continuous_scale=ACTIVE_SCALE,
                        aspect="auto", title=f"Heat Map: {x_cat} vs. {hue_cat} ({cohort_label})"
                    )
                elif biv_type == "Scatter Plot":
                    fig_biv = px.scatter(
                        biv_counts, x=x_cat, y=hue_cat, size="Count", color=hue_cat,
                        size_max=45, color_discrete_sequence=ACTIVE_COLORS,
                        title=f"Scatter Plot (Size = Count): {x_cat} vs. {hue_cat} ({cohort_label})"
                    )
                else:
                    hole_val = 0.48 if biv_type == "Donut Chart" else 0.0
                    fig_biv = px.pie(
                        biv_counts, names="Combination", values="Count", hole=hole_val,
                        color_discrete_sequence=ACTIVE_COLORS,
                        title=f"{biv_type}: {x_cat} & {hue_cat} ({cohort_label})"
                    )
                    fig_biv.update_traces(textinfo="percent+label")

                show_plot(fig_biv)

                top_pair = biv_counts.sort_values("Count", ascending=False).iloc[0]
                min_pair = biv_counts.sort_values("Count", ascending=True).iloc[0]
                top_pct = biv_counts.sort_values("Pct", ascending=False).iloc[0]
                total_sub = len(sub_df)

                show_insights([
                    f"**Largest Segment ({cohort_label}):** `{top_pair[x_cat]}` paired with `{top_pair[hue_cat]}` leads with **{top_pair['Count']:,}** records (**{top_pair['Count'] / total_sub * 100:.1f}%**).",
                    f"**Smallest Segment:** `{min_pair[x_cat]}` paired with `{min_pair[hue_cat]}` has **{min_pair['Count']:,}** records (**{min_pair['Count'] / total_sub * 100:.1f}%**).",
                    f"**Within-Group Concentration:** Inside `{x_cat} = {top_pct[x_cat]}`, **{top_pct['Pct']:.1f}%** belong to `{hue_cat} = {top_pct[hue_cat]}`."
                ])
            else:
                st.warning("No records match the selected filter.")
else:
    st.info("At least 2 categorical columns are required for Bivariate Analysis.")


# --------------------------------------------------
# SECTION 4: CORRELATION ANALYSIS
# --------------------------------------------------
st.markdown("---")
st.subheader("4. Feature Correlation & Heat Map")

corr_matrix = compute_correlation_matrix(df, numeric_cols, categorical_cols)

if not corr_matrix.empty:
    if target:
        target_dummies = [c for c in corr_matrix.columns if c.startswith(f"{target}_")]
        if target_dummies:
            pos_col = target_dummies[-1]
            target_corr = (
                corr_matrix[pos_col]
                .drop(labels=target_dummies, errors="ignore")
                .dropna()
                .sort_values(ascending=False)
                .reset_index()
            )
            target_corr.columns = ["Feature", "Correlation"]

            corr_type = st.selectbox(
                "Select Correlation Chart Type",
                ["Column Chart", "Bar Chart", "Line Chart"],
                key="corr_chart_type"
            )

            if corr_type == "Column Chart":
                fig_corr = px.bar(
                    target_corr, x="Feature", y="Correlation", color="Correlation",
                    color_continuous_scale="Turbo", range_color=[-1, 1],
                    title=f"Column Chart: Feature Correlations with {pos_col}"
                )
            elif corr_type == "Bar Chart":
                fig_corr = px.bar(
                    target_corr.sort_values("Correlation", ascending=True),
                    y="Feature", x="Correlation", orientation="h", color="Correlation",
                    color_continuous_scale="Turbo", range_color=[-1, 1],
                    title=f"Bar Chart: Feature Correlations with {pos_col}"
                )
            else:
                fig_corr = px.line(
                    target_corr, x="Feature", y="Correlation", markers=True,
                    color_discrete_sequence=[ACTIVE_COLORS[0]],
                    title=f"Line Chart: Feature Correlations with {pos_col}"
                )
                fig_corr.update_traces(line=dict(width=3), marker=dict(size=9, color=ACTIVE_COLORS[2]))

            fig_corr.update_xaxes(tickangle=-45)
            show_plot(fig_corr)

            if not target_corr.empty:
                top_pos = target_corr.iloc[0]
                top_neg = target_corr.iloc[-1]
                show_insights([
                    f"**Strongest Positive Driver:** `{top_pos['Feature']}` has the highest positive correlation with `{pos_col}` ($r = {top_pos['Correlation']:.3f}$).",
                    f"**Strongest Negative Driver:** `{top_neg['Feature']}` has the strongest inverse correlation with `{pos_col}` ($r = {top_neg['Correlation']:.3f}$)."
                ])

    with st.expander("🔍 View Full Correlation Heat Map", expanded=True):
        fig_heat = px.imshow(
            corr_matrix.round(2),
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
            title="Heat Map: Feature Correlation Matrix"
        )
        fig_heat.update_layout(height=650)
        show_plot(fig_heat)

        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        stacked = upper.stack().reset_index()
        if not stacked.empty:
            stacked.columns = ["Feature 1", "Feature 2", "Correlation"]
            stacked["AbsCorr"] = stacked["Correlation"].abs()
            best_pair = stacked.sort_values("AbsCorr", ascending=False).iloc[0]
            show_insights([
                f"**Strongest Feature Pair:** `{best_pair['Feature 1']}` and `{best_pair['Feature 2']}` have the strongest correlation across the entire dataset ($r = {best_pair['Correlation']:.2f}$)."
            ])


# --------------------------------------------------
# SECTION 5: FINAL PROCESSED DATASET SUMMARY & EXPORT
# --------------------------------------------------
st.markdown("---")
st.subheader("5. Final Processed Dataset")
st.caption("Review the final processed dataset, download it in CSV or Excel format, or proceed to the Summary Report.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Records (Rows)", f"{len(df):,}")
m2.metric("Total Features (Columns)", f"{df.shape[1]:,}")
m3.metric("Numerical / Categorical", f"{len(numeric_cols)} / {len(categorical_cols)}")
m4.metric("Remaining Missing Values", f"{int(df.isna().sum().sum()):,}")

st.dataframe(df.head(10), use_container_width=True, hide_index=True)

csv_bytes, excel_bytes = prepare_export_buffers(df)

st.write("#### 📥 Download Dataset & Generate Summary")
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    st.download_button(
        label="Download Dataset (.CSV)",
        data=csv_bytes,
        file_name="Processed_Dataset.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary"
    )

with btn_col2:
    if excel_bytes is not None:
        st.download_button(
            label="Download Dataset (.XLSX)",
            data=excel_bytes,
            file_name="Processed_Dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
    else:
        st.button(
            "Download Dataset (.XLSX) — Install 'openpyxl'",
            disabled=True,
            use_container_width=True
        )

with btn_col3:
    if st.button("Generate Summary →", type="primary", use_container_width=True):
        summary_page = next(
            (
                p.as_posix()
                for p in sorted(Path("pages").glob("*.py"))
                if any(k in p.stem.lower() for k in ("summary", "report", "insight"))
            ),
            None
        )
        if summary_page:
            st.switch_page(summary_page)
        else:
            st.error("Summary Report page not found inside the `pages/` folder.")