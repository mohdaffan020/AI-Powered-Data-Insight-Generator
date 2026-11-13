from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------
st.set_page_config(page_title="Data Profiling", page_icon="🔍", layout="wide")

st.title("🔍 Data Profiling")
st.caption("Explore dataset structure, data types, summary statistics, target distribution, and missing values.")

if "data" not in st.session_state or st.session_state["data"].empty:
    st.warning("⚠️ Please upload a dataset on the Home page first.")
    st.stop()


@st.cache_data(show_spinner=False)
def prepare_profiling_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Normalize blank strings to NaN once per unique dataset."""
    df_clean = raw_df.copy()
    str_cols = df_clean.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        blank_mask = df_clean[col].astype("string").str.strip().eq("").fillna(False)
        if blank_mask.any():
            df_clean.loc[blank_mask, col] = pd.NA
    return df_clean


df = prepare_profiling_data(st.session_state["data"])
num_df = df.select_dtypes(include="number")
cat_df = df.select_dtypes(exclude="number")

# --------------------------------------------------
# 1. DATASET SHAPE & TOP 5 RECORDS
# --------------------------------------------------
st.subheader("1. Dataset Overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Rows", f"{df.shape[0]:,}")
c2.metric("Total Columns", f"{df.shape[1]:,}")
c3.metric("Numerical Columns", len(num_df.columns))
c4.metric("Categorical Columns", len(cat_df.columns))

st.markdown("**Top 10 Records**")
st.dataframe(df.head(10), use_container_width=True, hide_index=True)

# --------------------------------------------------
# 2. ATTRIBUTES, DATA TYPES & DESCRIPTIVE STATS
# --------------------------------------------------
st.markdown("---")
st.subheader("2. Data Attributes & Descriptive Statistics")

tab1, tab2, tab3 = st.tabs([
    "📋 Columns & Data Types",
    "🔢 Numerical Statistics",
    "🏷️ Categorical Summary"
])

with tab1:
    null_counts = df.isnull().sum()
    dtype_df = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Non-Null Count": (len(df) - null_counts).values,
        "Null Count": null_counts.values,
        "Unique Values": df.nunique(dropna=True).values
    })
    st.dataframe(dtype_df, use_container_width=True, hide_index=True)

with tab2:
    if not num_df.empty:
        st.dataframe(num_df.describe().round(2), use_container_width=True)
    else:
        st.info("No numerical columns found.")

with tab3:
    if not cat_df.empty:
        st.dataframe(cat_df.describe().T, use_container_width=True)
    else:
        st.info("No categorical columns found.")

# --------------------------------------------------
# 3. TARGET VARIABLE EXPLORATION
# --------------------------------------------------
st.markdown("---")
st.subheader("3. Target Variable Distribution")

target_candidates = [c for c in df.columns if 2 <= df[c].dropna().nunique() <= 10]
priority_names = {"churn", "target", "label", "status", "survived", "y"}
default_target = next(
    (c for c in target_candidates if c.lower() in priority_names),
    target_candidates[0] if target_candidates else None
)

if target_candidates:
    target_col = st.selectbox(
        "Select Target Variable",
        options=target_candidates,
        index=target_candidates.index(default_target)
    )
    st.session_state["target_col"] = target_col

    counts = df[target_col].fillna("Missing").astype(str).value_counts().reset_index()
    counts.columns = [target_col, "Count"]
    counts["Percentage (%)"] = (counts["Count"] / len(df) * 100).round(2)

    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        fig = px.bar(
            counts,
            x=target_col,
            y="Count",
            text="Count",
            color=target_col,
            title=f"Count of Target Variable ({target_col}) Per Category"
        )
        fig.update_layout(template="plotly_white", xaxis_showgrid=False, yaxis_showgrid=False)
        fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("**Target Counts & Ratio**")
        st.dataframe(counts, use_container_width=True, hide_index=True)
else:
    st.info("No low-cardinality target column detected.")

# --------------------------------------------------
# 4. MISSING VALUES CHECK
# --------------------------------------------------
st.markdown("---")
st.subheader("4. Percentage of Missing Values")

missing = (df.isnull().sum() * 100 / len(df)).round(2).reset_index()
missing.columns = ["Column", "Percentage"]

fig_miss = px.line(
    missing,
    x="Column",
    y="Percentage",
    markers=True,
    title="Percentage of Missing Values per Column"
)
fig_miss.update_layout(
    template="plotly_white",
    xaxis_tickangle=-45,
    xaxis_showgrid=False,
    yaxis_showgrid=False
)
st.plotly_chart(fig_miss, use_container_width=True)

# --------------------------------------------------
# NAVIGATION TO DATA CLEANING
# --------------------------------------------------
st.markdown("---")

_, btn_col, _ = st.columns([1, 1, 1])

with btn_col:
    if st.button("Proceed to Data Cleaning →", type="primary", use_container_width=True):
        cleaning_page = next(
            (p.as_posix() for p in Path("pages").glob("*Data*Cleaning*.py")),
            None
        )
        if cleaning_page:
            st.switch_page(cleaning_page)
        else:
            st.error("⚠️ Data Cleaning page not found inside the `pages/` folder.")
