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
