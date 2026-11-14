import io
import os

import pandas as pd
import streamlit as st


# ============================================================
# 1. PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="AI-Powered Data Insight Generator",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# 2. RESPONSIVE CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>
    /* Main hero section */
    .hero {
        background: linear-gradient(135deg, #1f222b 0%, #262b38 100%);
        border: 1px solid #30343d;
        border-radius: 20px;
        padding: 38px 28px;
        margin-bottom: 24px;
        text-align: center;
        box-sizing: border-box;
    }

    .hero-badge {
        color: #38bdf8;
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .hero-title {
        color: #ffffff;
        font-size: clamp(24px, 4vw, 36px);
        line-height: 1.2;
        font-weight: 750;
        margin-bottom: 12px;
    }

    .hero-text {
        color: #b8bcc8;
        font-size: clamp(14px, 2vw, 18px);
        line-height: 1.55;
        max-width: 760px;
        margin: 0 auto;
    }

    /* Reusable responsive grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        grid-auto-rows: 1fr;
        gap: 16px;
        align-items: stretch;
    }

    .feature-card {
        background: #191c23;
        border: 1px solid #30343d;
        border-radius: 15px;
        padding: 22px;
        min-height: 180px;
        height: 100%;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        overflow-wrap: anywhere;
    }

    .feature-icon {
        font-size: 28px;
        line-height: 1.2;
        margin-bottom: 12px;
    }

    .feature-title {
        color: #ffffff;
        font-size: 18px;
        line-height: 1.3;
        font-weight: 700;
        margin: 0 0 9px 0;
    }

    .feature-text {
        color: #b8bcc8;
        font-size: 14px;
        line-height: 1.5;
        margin: 0;
    }

    /* Workflow and technology grids */
    .workflow-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 12px;
        align-items: stretch;
    }

    .workflow-card,
    .tech-card {
        background: #191c23;
        border: 1px solid #30343d;
        border-radius: 13px;
        padding: 18px 12px;
        min-height: 105px;
        height: 100%;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    .workflow-icon {
        font-size: 27px;
        margin-bottom: 8px;
    }

    .workflow-title {
        color: #ffffff;
        font-size: 14px;
        font-weight: 650;
        line-height: 1.35;
    }

    .tech-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        align-items: stretch;
    }

    .tech-card {
        min-height: 68px;
        font-size: 15px;
        font-weight: 650;
        color: #ffffff;
    }

    /* Page-link button */
    div[data-testid="stPageLink"] a,
    a[data-testid="stPageLink-NavLink"] {
        background-color: #ff4b4b !important;
        border: 1px solid #ff4b4b !important;
        border-radius: 0.5rem !important;
        padding: 0.55rem 1rem !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-decoration: none !important;
        width: 100% !important;
        box-sizing: border-box !important;
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
        font-size: 15px !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }

    /* Tablet */
    @media (max-width: 900px) {
        .feature-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .workflow-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }

        .tech-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    /* Mobile */
    @media (max-width: 600px) {
        .hero {
            padding: 26px 16px;
            border-radius: 15px;
        }

        .feature-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
        }

        .feature-card {
            min-height: 190px;
            padding: 14px 12px;
            border-radius: 12px;
        }

        .feature-icon {
            font-size: 23px;
            margin-bottom: 9px;
        }

        .feature-title {
            font-size: 14px;
            line-height: 1.3;
            margin-bottom: 7px;
        }

        .feature-text {
            font-size: 12px;
            line-height: 1.45;
        }

        .workflow-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 9px;
        }

        .workflow-card {
            min-height: 92px;
            padding: 13px 8px;
        }

        .workflow-icon {
            font-size: 23px;
        }

        .workflow-title {
            font-size: 12px;
        }

        .tech-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 9px;
        }

        .tech-card {
            min-height: 58px;
            padding: 12px 8px;
            font-size: 13px;
        }
    }

    /* Very narrow phones */
    @media (max-width: 360px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }

        .feature-card {
            min-height: auto;
        }

        .workflow-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. HELPER: FIND A STREAMLIT PAGE
# ============================================================

def find_page_path(keyword: str) -> str | None:
    """Find a page whose filename contains the supplied keyword."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pages_dir = os.path.join(base_dir, "pages")

    if os.path.isdir(pages_dir):
        for filename in sorted(os.listdir(pages_dir)):
            if filename.endswith(".py") and keyword.casefold() in filename.casefold():
                return f"pages/{filename}"

    for filename in sorted(os.listdir(base_dir)):
        if (
            filename.endswith(".py")
            and filename != os.path.basename(__file__)
            and keyword.casefold() in filename.casefold()
        ):
            return filename

    return None


# ============================================================
# 4. HERO SECTION
# ============================================================

st.markdown(
    """
    <section class="hero">
        <div class="hero-badge">🤖 AI-Powered Data Insight Generator</div>
        <div class="hero-title">📊 Turn Your Data Into Meaningful Insights</div>
        <div class="hero-text">
            Upload your dataset, understand your data, clean it,
            analyze it and generate useful insights with AI.
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 5. DATA UPLOAD
# ============================================================

st.markdown("## 📂 Upload Your Dataset")

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file to begin",
    type=["csv", "xlsx", "xls"],
)

if uploaded_file is not None:
    # Use the file contents to detect a newly selected upload.
    file_bytes = uploaded_file.getvalue()
    file_id = f"{uploaded_file.name}_{len(file_bytes)}"

    if st.session_state.get("uploaded_file_id") != file_id:
        try:
            file_buffer = io.BytesIO(file_bytes)

            if uploaded_file.name.lower().endswith(".csv"):
                new_df = pd.read_csv(file_buffer)
            else:
                new_df = pd.read_excel(file_buffer)

            st.session_state["data"] = new_df.copy()
            st.session_state["raw_data"] = new_df.copy()
            st.session_state["file_name"] = uploaded_file.name
            st.session_state["uploaded_file_id"] = file_id

            # A new upload should not retain an old cleaning result/state.
            st.success("Dataset uploaded successfully.")

        except Exception as error:
            st.error(f"Unable to read this file: {error}")

if "data" in st.session_state and isinstance(st.session_state["data"], pd.DataFrame):
    active_df = st.session_state["data"]
    file_label = st.session_state.get("file_name", "Uploaded Dataset")

    if not active_df.empty:
        st.success(f"✅ Active Dataset: **{file_label}**")

        metric_cols = st.columns([2, 1, 1])
        metric_cols[0].metric("Active File", file_label)
        metric_cols[1].metric("Total Rows", f"{active_df.shape[0]:,}")
        metric_cols[2].metric("Total Columns", f"{active_df.shape[1]:,}")

        profiling_path = find_page_path("profil")

        if profiling_path:
            _, nav_col, _ = st.columns([1, 2, 1])
            with nav_col:
                st.page_link(
                    profiling_path,
                    label="Proceed to Data Profiling →",
                    use_container_width=True,
                )
        else:
            st.warning(
                "Data Profiling page not found. Make sure a Python file "
                "containing 'profil' in its filename exists inside the pages folder."
            )
    else:
        st.warning("The uploaded dataset is empty.")


# ============================================================
# 6. PROJECT FEATURES
# ============================================================

st.markdown("---")
st.markdown("## 🚀 What This Project Offers")

FEATURES = [
    (
        "📂",
        "Upload Data",
        "Upload CSV or Excel datasets and view your data inside the application.",
    ),
    (
        "🔎",
        "Data Profiling",
        "Understand rows, columns, missing values, duplicates and basic data types.",
    ),
    (
        "🧹",
        "Data Cleaning",
        "Handle common data problems such as missing values, duplicates and formatting issues.",
    ),
    (
        "📊",
        "Exploratory Data Analysis",
        "Identify patterns and visualize your dataset.",
    ),
    (
        "💡",
        "Insights",
        "Transform analytics into clear, actionable insights.",
    ),
    (
        "📄",
        "Simple Summary",
        "Review important takeaways and data-driven conclusions.",
    ),
]

feature_html = ['<div class="feature-grid">']

for icon, title, description in FEATURES:
    feature_html.append(
        f"""
        <article class="feature-card">
            <div class="feature-icon">{icon}</div>
            <h3 class="feature-title">{title}</h3>
            <p class="feature-text">{description}</p>
        </article>
        """
    )

feature_html.append("</div>")

st.markdown("\n".join(feature_html), unsafe_allow_html=True)


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
    ("💡", "Insights"),
]

workflow_html = ['<div class="workflow-grid">']

for icon, title in WORKFLOW_STEPS:
    workflow_html.append(
        f"""
        <div class="workflow-card">
            <div class="workflow-icon">{icon}</div>
            <div class="workflow-title">{title}</div>
        </div>
        """
    )

workflow_html.append("</div>")

st.markdown("\n".join(workflow_html), unsafe_allow_html=True)


# ============================================================
# 8. TECHNOLOGIES USED
# ============================================================

st.markdown("---")
st.markdown("## 🛠️ Technologies Used")

TECH_STACK = ["🐍 Python", "🐼 Pandas", "📈 Plotly", "🌐 Streamlit"]

tech_html = ['<div class="tech-grid">']

for technology in TECH_STACK:
    tech_html.append(f'<div class="tech-card">{technology}</div>')

tech_html.append("</div>")

st.markdown("\n".join(tech_html), unsafe_allow_html=True)


# ============================================================
# 9. FOOTER
# ============================================================

st.markdown("---")
st.markdown(
    """
    <div style="
        text-align: center;
        color: #888f9f;
        padding: 20px 10px;
        line-height: 1.6;
    ">
        <strong>AI-Powered Data Insight Generator</strong><br>
        Exploratory Data Analysis
    </div>
    """,
    unsafe_allow_html=True,
)
