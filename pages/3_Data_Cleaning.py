from pathlib import Path
import re
import numpy as np
import pandas as pd
import streamlit as st


# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(page_title="Data Cleaning", page_icon="🧹", layout="wide")

st.title("🧹 Data Cleaning")
st.caption("Clean your dataset, convert data types, split/merge columns, and prepare features for Exploratory Data Analysis.")

if "data" not in st.session_state or st.session_state["data"].empty:
    st.warning("⚠️ Please upload a dataset first.")
    st.stop()

df = st.session_state["data"].copy()


# --------------------------------------------------
# 1. BEFORE CLEANING SUMMARY
# --------------------------------------------------

st.subheader("1. Current Dataset Status")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{df.shape[0]:,}")
c2.metric("Columns", f"{df.shape[1]:,}")
c3.metric("Missing Values", f"{int(df.isnull().sum().sum()):,}")
c4.metric("Duplicate Rows", f"{int(df.duplicated().sum()):,}")


# --------------------------------------------------
# 2. CLEANING & PREPROCESSING OPERATIONS
# --------------------------------------------------

st.markdown("---")
st.subheader("2. Select Cleaning Operations")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("**Basic Cleaning**")
    trim_spaces = st.checkbox("Trim extra spaces & convert blank text to NaN", value=True)
    remove_duplicates = st.checkbox("Remove duplicate rows", value=False)
    remove_empty = st.checkbox("Remove completely empty rows/columns", value=True)

    # Auto-detect ID columns (e.g., customerID)
    id_defaults = [
        c for c in df.columns
        if bool(re.search(r"(^|[_\s-])id$|^id($|[_\s-])", c.lower()))
    ]
    drop_cols = st.multiselect(
        "Drop unneeded / ID columns (e.g., customerID)",
        options=df.columns.tolist(),
        default=id_defaults
    )

with col_right:
    st.markdown("**Missing Value Handling**")
    missing_action = st.radio(
        "Choose how to handle missing values:",
        [
            "Drop rows with missing values",
            "Fill missing values (Median for Numeric, Mode for Categorical)",
            "Fill missing values with custom constant ('N/A' or 0)",
            "Keep missing values"
        ]
    )


# --------------------------------------------------
# 3. DATA TYPE CONVERSION (SEPARATE OPTIONS)
# --------------------------------------------------

st.markdown("---")
st.subheader("3. Data Type Conversion")
st.caption("Dedicated options to convert columns between Numeric, Text, Date/Time, and Categorical/Boolean formats.")

available_cols = [c for c in df.columns if c not in drop_cols]

# Auto-detect text columns that contain numbers (e.g., TotalCharges)
auto_num_candidates = []
for col in df.select_dtypes(include=["object", "string"]).columns:
    if col in available_cols:
        sample_s = df[col].dropna().astype(str).str.strip()
        if not sample_s.empty and pd.to_numeric(sample_s, errors="coerce").notna().mean() >= 0.85:
            auto_num_candidates.append(col)

dt_col1, dt_col2, dt_col3, dt_col4 = st.columns(4)

with dt_col1:
    st.markdown("**🔢 Text → Numeric**")
    cols_to_numeric = st.multiselect(
        "Convert to Numeric (Float/Int)",
        options=available_cols,
        default=auto_num_candidates,
        help="Converts text numbers like TotalCharges into numeric values."
    )

with dt_col2:
    st.markdown("**🔤 Column → Text (String)**")
    cols_to_text = st.multiselect(
        "Convert to Text / Categorical String",
        options=[c for c in available_cols if c not in cols_to_numeric],
        help="Useful for numeric codes like SeniorCitizen (0/1) or ZIP codes."
    )

with dt_col3:
    st.markdown("**📅 Column → Date/Time**")
    cols_to_date = st.multiselect(
        "Convert to DateTime",
        options=[c for c in available_cols if c not in cols_to_numeric + cols_to_text],
        help="Parses date strings into standard DateTime format."
    )

with dt_col4:
    st.markdown("**🏷️ Column → Category / Bool**")
    cols_to_category = st.multiselect(
        "Convert to Category dtype",
        options=[c for c in available_cols if c not in cols_to_numeric + cols_to_text + cols_to_date],
        help="Optimizes memory and marks column as a categorical feature."
    )


# --------------------------------------------------
# 4. COLUMN & FEATURE TRANSFORMATIONS (SPLIT, MERGE, BINNING & MORE)
# --------------------------------------------------

st.markdown("---")
st.subheader("4. Column & Feature Transformations")
st.caption("Split text into multiple columns, combine columns into text, bin numerical features, standardize text case, or replace values.")

tab_bin, tab_split, tab_merge, tab_text, tab_replace = st.tabs([
    "📦 Feature Binning (e.g., Tenure Group)",
    "✂️ Text to Columns (Split)",
    "🔗 Columns to Text (Merge)",
    "🔠 Text Case & Formatting",
    "🔍 Find & Replace Values"
])

# --- TAB 1: FEATURE BINNING ---
with tab_bin:
    num_cols = [
        c for c in available_cols
        if pd.api.types.is_numeric_dtype(df[c]) or c in cols_to_numeric
    ]
    create_bins = st.checkbox("Create grouped bins from a numerical column (e.g., Tenure Group)")

    if create_bins and num_cols:
        b1, b2, b3 = st.columns(3)
        default_bin = num_cols.index("tenure") if "tenure" in num_cols else 0
        with b1:
            bin_col = st.selectbox("Column to group", num_cols, index=default_bin)
        with b2:
            bin_size = st.number_input("Bin width (e.g., 12 for 12-month groups)", min_value=1, value=12)
        with b3:
            drop_raw_bin_col = st.checkbox(f"Drop original '{bin_col}' column after grouping", value=True)
    elif create_bins:
        st.info("No numerical columns available for binning.")

# --- TAB 2: TEXT TO COLUMNS (SPLIT COLUMN) ---
with tab_split:
    enable_split = st.checkbox("Split a text column into multiple columns (Text to Columns)")
    if enable_split:
        text_candidates = [c for c in available_cols if c in df.select_dtypes(include=["object", "string"]).columns]
        if text_candidates:
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                split_col = st.selectbox("Column to split", text_candidates)
            with s2:
                split_delim = st.text_input("Delimiter (e.g., '-', ',', ' ')", value="-")
            with s3:
                split_prefix = st.text_input("New column prefix", value=f"{split_col}_part")
            with s4:
                drop_split_orig = st.checkbox(f"Drop original '{split_col}'", value=False)
        else:
            st.info("No text columns available to split.")

# --- TAB 3: COLUMNS TO TEXT (MERGE / CONCATENATE COLUMNS) ---
with tab_merge:
    enable_merge = st.checkbox("Combine multiple columns into a single text column (Columns to Text)")
    if enable_merge:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            merge_cols = st.multiselect("Select columns to combine", available_cols)
        with m2:
            merge_sep = st.text_input("Separator", value="_")
        with m3:
            merge_new_name = st.text_input("New combined column name", value="Combined_Feature")
        with m4:
            drop_merge_orig = st.checkbox("Drop original merged columns", value=False)

# --- TAB 4: TEXT CASE & FORMATTING ---
with tab_text:
    enable_case = st.checkbox("Standardize text casing (UPPERCASE, lowercase, Title Case)")
    if enable_case:
        text_cols_all = [c for c in available_cols if c in df.select_dtypes(include=["object", "string"]).columns]
        tc1, tc2 = st.columns(2)
        with tc1:
            case_cols = st.multiselect("Select text columns to format", text_cols_all)
        with tc2:
            case_mode = st.selectbox("Select text format", ["Title Case", "lowercase", "UPPERCASE"])

# --- TAB 5: FIND & REPLACE VALUES ---
with tab_replace:
    enable_replace = st.checkbox("Find and replace specific values in a column (e.g., 0 → No, 1 → Yes)")
    if enable_replace:
        r1, r2, r3 = st.columns(3)
        with r1:
            rep_col = st.selectbox("Select column", available_cols)
        with r2:
            find_val = st.text_input("Value to find (e.g., No internet service)")
        with r3:
            replace_val = st.text_input("Replace with (e.g., No)")


# --------------------------------------------------
# 5. APPLY CLEANING BUTTON
# --------------------------------------------------

st.markdown("---")

if st.button("🧹 Clean Data", type="primary", use_container_width=True):
    cleaned = df.copy()

    # 1. Trim spaces and blanks
    if trim_spaces:
        for col in cleaned.select_dtypes(include=["object", "string"]).columns:
            cleaned[col] = cleaned[col].astype("string").str.strip()
            cleaned.loc[cleaned[col].eq(""), col] = np.nan

    # 2. Data Type Conversions
    for col in cols_to_numeric:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    for col in cols_to_text:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].astype("string")

    for col in cols_to_date:
        if col in cleaned.columns:
            cleaned[col] = pd.to_datetime(cleaned[col], errors="coerce")

    for col in cols_to_category:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].astype("category")

    # 3. Find & Replace Values
    if enable_replace and rep_col in cleaned.columns and find_val != "":
        col_str_mask = cleaned[rep_col].astype(str) == find_val
        cleaned.loc[col_str_mask, rep_col] = replace_val

    # 4. Text Case Formatting
    if enable_case and case_cols:
        for col in case_cols:
            if col in cleaned.columns:
                s = cleaned[col].astype("string")
                if case_mode == "Title Case":
                    cleaned[col] = s.str.title()
                elif case_mode == "lowercase":
                    cleaned[col] = s.str.lower()
                elif case_mode == "UPPERCASE":
                    cleaned[col] = s.str.upper()

    # 5. Text to Columns (Split)
    if enable_split and text_candidates and split_col in cleaned.columns and split_delim != "":
        split_df = cleaned[split_col].astype("string").str.split(split_delim, expand=True)
        for i in range(split_df.shape[1]):
            cleaned[f"{split_prefix}_{i + 1}"] = split_df[i].str.strip()
        if drop_split_orig:
            cleaned.drop(columns=[split_col], inplace=True)

    # 6. Columns to Text (Merge)
    if enable_merge and len(merge_cols) >= 2 and merge_new_name.strip():
        valid_m_cols = [c for c in merge_cols if c in cleaned.columns]
        if valid_m_cols:
            cleaned[merge_new_name.strip()] = (
                cleaned[valid_m_cols]
                .fillna("")
                .astype(str)
                .agg(merge_sep.join, axis=1)
            )
            if drop_merge_orig:
                cleaned.drop(columns=valid_m_cols, inplace=True)

    # 7. Drop duplicates and empty rows/cols
    if remove_duplicates:
        cleaned.drop_duplicates(inplace=True)
    if remove_empty:
        cleaned.dropna(how="all", inplace=True)
        cleaned.dropna(axis=1, how="all", inplace=True)

    # 8. Handle missing values
    if missing_action == "Drop rows with missing values":
        cleaned.dropna(how="any", inplace=True)
    elif "Median for Numeric" in missing_action:
        for col in cleaned.columns:
            if cleaned[col].isnull().any():
                if pd.api.types.is_numeric_dtype(cleaned[col]):
                    cleaned[col] = cleaned[col].fillna(cleaned[col].median())
                else:
                    mode_val = cleaned[col].mode(dropna=True)
                    cleaned[col] = cleaned[col].fillna(mode_val.iloc[0] if not mode_val.empty else "N/A")
    elif "custom constant" in missing_action:
        for col in cleaned.columns:
            if cleaned[col].isnull().any():
                if pd.api.types.is_numeric_dtype(cleaned[col]):
                    cleaned[col] = cleaned[col].fillna(0)
                else:
                    cleaned[col] = cleaned[col].fillna("N/A")

    # 9. Create grouped bins (matching notebook's tenure_group logic)
    if create_bins and num_cols and bin_col in cleaned.columns:
        valid_num = pd.to_numeric(cleaned[bin_col], errors="coerce").dropna()
        if not valid_num.empty:
            max_v = int(valid_num.max())
            labels = [f"{i} - {i + int(bin_size) - 1}" for i in range(1, max_v + 1, int(bin_size))]
            edges = range(1, max_v + int(bin_size) + 1, int(bin_size))
            cleaned[f"{bin_col}_group"] = pd.cut(
                pd.to_numeric(cleaned[bin_col], errors="coerce"),
                bins=edges,
                right=False,
                labels=labels
            ).astype(str)
            if drop_raw_bin_col:
                cleaned.drop(columns=[bin_col], inplace=True)

    # 10. Drop unneeded / ID columns
    if drop_cols:
        cleaned.drop(columns=[c for c in drop_cols if c in cleaned.columns], inplace=True)

    cleaned.reset_index(drop=True, inplace=True)
    st.session_state["data"] = cleaned
    st.success("✅ Data cleaned and transformed successfully!")


# --------------------------------------------------
# 6. AFTER CLEANING PREVIEW
# --------------------------------------------------

st.subheader("5. Cleaned Dataset Preview")
current_df = st.session_state["data"]

ac1, ac2, ac3 = st.columns(3)
ac1.metric("Cleaned Rows", f"{current_df.shape[0]:,}")
ac2.metric("Cleaned Columns", f"{current_df.shape[1]:,}")
ac3.metric("Remaining Missing Values", f"{int(current_df.isnull().sum().sum()):,}")

st.dataframe(current_df.head(10), use_container_width=True, hide_index=True)

with st.expander("🔄 View Updated Column Data Types"):
    dtype_summary = pd.DataFrame({
        "Column": current_df.columns,
        "Data Type": current_df.dtypes.astype(str).values,
        "Unique Values": current_df.nunique(dropna=True).values
    })
    st.dataframe(dtype_summary, use_container_width=True, hide_index=True)


# --------------------------------------------------
# NAVIGATION TO EDA
# --------------------------------------------------

st.markdown("---")

_, btn_col, _ = st.columns([1, 1, 1])

with btn_col:
    if st.button("Proceed to EDA →", type="primary", use_container_width=True):
        eda_page = next(
            (
                p.as_posix()
                for p in Path("pages").glob("*.py")
                if any(k in p.stem.lower() for k in ["eda", "analysis"])
            ),
            None
        )
        if eda_page:
            st.switch_page(eda_page)
        else:
            st.error("⚠️ EDA page not found inside the `pages/` folder.")
