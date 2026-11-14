import os
import pandas as pd
import streamlit as st


# ============================================================
# 1. PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="AI-Powered Data Insight Generator",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# 2. CUSTOM STYLING (DARK THEME + RED RECTANGLE PAGE LINK)
# ============================================================

st.markdown(
    """
    <style>
    .hero {
        background: linear-gradient(135deg, #1f222b 0%, #262b38 100%);
        border: 1px solid #30343d;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 25px;
    }
    .hero-badge {
        font-size: 16px;
        color: #38bdf8;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .hero-title {
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 12px;
    }
    .hero-text {
        font-size: 18px;
        color: #b8bcc8;
    }
    .card {
        background-color: #191c23;
        border: 1px solid #30343d;
        padding: 25px;
        border-radius: 15px;
        min-height: 185px;
        margin-bottom: 15px;
    }
    .card-icon {
        font-size: 30px;
    }
    .card-title {
        font-size: 20px;
        font-weight: bold;
        margin-top: 10px;
    }
    .card-text {
        color: #b8bcc8;
        line-height: 1.5;
    }
    .workflow {
        background-color: #191c23;
        border: 1px solid #30343d;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
    .workflow-icon {
        font-size: 30px;
    }
    .workflow-title {
        font-weight: bold;
        margin-top: 8px;
    }
    .tech {
        background-color: #191c23;
        border: 1px solid #30343d;
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
    }
    /* Red rectangle clickable layout for st.page_link */
    div[data-testid="stPageLink"] a,
    a[data-testid="stPageLink-NavLink"] {
        background-color: #ff4b4b !important;
        border: 1px solid #ff4b4b !important;
        border-radius: 0.5rem !important;
        padding: 0.4rem 1.0rem !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-decoration: none !important;
        width: 100% !important;
        transition: background-color 0.2s ease, transform 0.15s ease !important;
    }
    div[data-testid="stPageLink"] a:hover,
    a[data-testid="stPageLink-NavLink"]:hover {
        background-color: #ff3333 !important;
        border-color: #ff3333 !important;
        transform: translateY(-1px);
    }
    div[data-testid="stPageLink"] a p,
    a[data-testid="stPageLink-NavLink"] p,
    div[data-testid="stPageLink"] span {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. HELPER FUNCTION TO RESOLVE PAGE PATHS SAFELY
# ============================================================

def find_page_path(keyword: str) -> str | None:
    """Finds a matching Streamlit page inside pages/ or root directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pages_dir = os.path.join(base_dir, "pages")

    if os.path.isdir(pages_dir):
        for fname in sorted(os.listdir(pages_dir)):
            if fname.endswith(".py") and keyword.lower() in fname.lower():
                return f"pages/{fname}"

    for fname in sorted(os.listdir(base_dir)):
        if fname.endswith(".py") and fname != os.path.basename(__file__) and keyword.lower() in fname.lower():
            return fname

    return None


# ============================================================
# 4. HERO SECTION
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">🤖 AI-Powered Data Insight Generator</div>
        <div class="hero-title">📊 Turn Your Data Into Meaningful Insights</div>
        <div class="hero-text">
            Upload your dataset, understand your data, clean it,
            analyze it and generate useful insights with AI.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 5. DATA UPLOAD & RED RECTANGLE CLICKABLE LINK
# ============================================================

st.markdown("## 📂 Upload Your Dataset")

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file to begin",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.get("uploaded_file_id") != file_id:
        try:
            df = (
                pd.read_csv(uploaded_file)
                if uploaded_file.name.lower().endswith(".csv")
                else pd.read_excel(uploaded_file)
            )
            st.session_state["data"] = df
            st.session_state["raw_data"] = df.copy()
            st.session_state["file_name"] = uploaded_file.name
            st.session_state["uploaded_file_id"] = file_id
        except Exception as e:
            st.error(f"⚠️ Error reading file: {e}")

if "data" in st.session_state and not st.session_state["data"].empty:
    active_df = st.session_state["data"]
    file_label = st.session_state.get("file_name", "Uploaded Dataset")

    st.success(f"✅ Active Dataset: **{file_label}**")

    m1, m2, m3 = st.columns([2,1,1])
    m1.metric("Active File", file_label)
    m2.metric("Total Rows", f"{active_df.shape[0]:,}")
    m3.metric("Total Columns", f"{active_df.shape[1]:,}")

    # with st.expander("👀 View Dataset Preview (Top 10 Rows)", expanded=False):
    #     st.dataframe(active_df.head(10), use_container_width=True, hide_index=True)

    profiling_path = find_page_path("profil")

    _, nav_col, _ = st.columns([1, 1, 1])
    with nav_col:
        if profiling_path:
            st.page_link(
                profiling_path,
                label=" Proceed to Data Profiling →",
                use_container_width=True
            )
        else:
            st.warning("⚠️ Data Profiling page file not found. Please ensure a file with 'Profiling' in its name exists in `pages/`.")


# ============================================================
# 6. FEATURES OVERVIEW
# ============================================================

st.markdown("---")
st.markdown("## 🚀 What This Project Offers")

FEATURES = [
    ("📂", "Upload Data", "Upload CSV or Excel datasets and view your data inside the application."),
    ("🔎", "Data Profiling", "Understand rows, columns, missing values, duplicates and basic data types."),
    ("🧹", "Data Cleaning", "Handle missing values, duplicates and formatting issues."),
    ("📊", "Exploratory Data Analysis", " Perform Visualization and Identify patterns."),
    ("💡", "Insights", "Simple and understandable key findings."),
    ("📄", "Simple Summary", "Review important takeaways and data-driven conclusions."),
]

for row_start in range(0, len(FEATURES), 3):
    cols = st.columns(3)
    for col, (icon, title, text) in zip(cols, FEATURES[row_start:row_start + 3]):
        with col:
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{title}</div>
                    <div class="card-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# 7. WORKFLOW
# ============================================================

st.markdown("---")
st.markdown("## 🔄 How It Works")

WORKFLOW_STEPS = [
    ("📂", "Upload"),
    ("🔎", "Data Profiling"),
    ("🧹", "Data Cleaning"),
    ("📊", "EDA"),
    ("💡", "Insight"),
]

wf_cols = st.columns(len(WORKFLOW_STEPS))
for col, (icon, title) in zip(wf_cols, WORKFLOW_STEPS):
    with col:
        st.markdown(
            f"""
            <div class="workflow">
                <div class="workflow-icon">{icon}</div>
                <div class="workflow-title">{title}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# 8. TECHNOLOGIES USED
# ============================================================

st.markdown("---")
st.markdown("## 🛠️ Technologies Used")

TECH_STACK = ["🐍 Python", "🐼 Pandas", "📈 Plotly", "🌐 Streamlit"]
tech_cols = st.columns(len(TECH_STACK))
for col, tech in zip(tech_cols, TECH_STACK):
    with col:
        st.markdown(f'<div class="tech">{tech}</div>', unsafe_allow_html=True)


# ============================================================
# 9. FOOTER
# ============================================================

st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#888f9f; padding:20px;">
        <strong>AI-Powered Data Insight Generator</strong>
        <br>
        Exploratory Data Analysis
    </div>
    """,
    unsafe_allow_html=True
)
