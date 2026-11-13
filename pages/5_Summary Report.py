import io
import re
import pandas as pd
import streamlit as st


# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Summary Report",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Summary Report")
st.caption(
    "Generate a simple, structured summary containing key findings "
    "and actionable recommendations from your dataset."
)

if "data" not in st.session_state or st.session_state["data"].empty:
    st.warning("⚠️ Please upload and clean your dataset first.")
    st.stop()

df = st.session_state["data"].copy()
file_name = st.session_state.get("file_name", "Uploaded Dataset")


# --------------------------------------------------
# HELPER: CLEAN & FORMAT MARKDOWN INTO PDF
# --------------------------------------------------

def clean_for_pdf(text):
    """Strip emojis and normalize special characters for standard PDF fonts."""
    replacements = {
        "→": "->",
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "-",
        "`": "",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Remove emojis / non-latin-1 characters
    return text.encode("latin-1", "ignore").decode("latin-1").strip()


def generate_pdf_bytes(markdown_text, dataset_title):
    """Convert the Markdown summary report into a properly formatted PDF."""
    # Option 1: Using fpdf / fpdf2
    try:
        from fpdf import FPDF

        class ReportPDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 10)
                self.set_text_color(120, 120, 120)
                self.cell(0, 8, clean_for_pdf(f"AI Data Analytics Summary Report | {dataset_title}"), border=False, ln=True, align="R")
                self.set_draw_color(200, 200, 200)
                self.line(10, 18, 200, 18)
                self.ln(4)

            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 9)
                self.set_text_color(130, 130, 130)
                self.cell(0, 10, f"Page {self.page_no()}", align="C")

        pdf = ReportPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Report Main Title Banner
        pdf.set_fill_color(31, 34, 43)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, clean_for_pdf(f"  Data Insight & Summary Report: {dataset_title}"), ln=True, fill=True)
        pdf.ln(6)

        for raw_line in markdown_text.split("\n"):
            line = clean_for_pdf(raw_line)
            if not line:
                pdf.ln(3)
                continue

            # Section Headings (### or ## or #)
            if line.startswith("#"):
                heading_text = line.lstrip("#").strip()
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 13)
                pdf.set_text_color(31, 92, 143)
                pdf.multi_cell(0, 8, heading_text)
                pdf.set_draw_color(220, 220, 220)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(2)

            # Bullet Points (- or *)
            elif line.startswith("- ") or line.startswith("* "):
                bullet_text = line[2:].strip().replace("**", "")
                pdf.set_font("Helvetica", "", 11)
                pdf.set_text_color(40, 40, 40)
                pdf.set_x(14)
                # Bold the lead-in label if a colon is present
                if ":" in bullet_text:
                    label_part, rest_part = bullet_text.split(":", 1)
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.write(6, f"- {label_part}:")
                    pdf.set_font("Helvetica", "", 11)
                    pdf.multi_cell(0, 6, rest_part)
                else:
                    pdf.multi_cell(0, 6, f"- {bullet_text}")

            # Numbered Lists (1. , 2. , etc.)
            elif re.match(r"^\d+\.\s", line):
                clean_num_line = line.replace("**", "")
                pdf.set_font("Helvetica", "", 11)
                pdf.set_text_color(40, 40, 40)
                pdf.set_x(14)
                if ":" in clean_num_line:
                    label_part, rest_part = clean_num_line.split(":", 1)
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.write(6, f"{label_part}:")
                    pdf.set_font("Helvetica", "", 11)
                    pdf.multi_cell(0, 6, rest_part)
                else:
                    pdf.multi_cell(0, 6, clean_num_line)

            # Standard Paragraph
            else:
                pdf.set_font("Helvetica", "", 11)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(0, 6, line.replace("**", ""))

        out = pdf.output(dest="S")
        return bytes(out) if isinstance(out, (bytes, bytearray)) else out.encode("latin-1")

    except ImportError:
        pass

    # Option 2: Fallback to ReportLab if fpdf2 is not installed
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=16,
            textColor=colors.HexColor("#1f222b"),
            spaceAfter=12
        )
        h_style = ParagraphStyle(
            "SecHead",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.HexColor("#1f5c8f"),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontSize=10.5,
            leading=15,
            spaceAfter=4
        )

        story = [
            Paragraph(clean_for_pdf(f"AI Data Summary Report: {dataset_title}"), title_style),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")),
            Spacer(1, 10)
        ]

        for raw_line in markdown_text.split("\n"):
            line = clean_for_pdf(raw_line)
            if not line:
                story.append(Spacer(1, 6))
                continue
            if line.startswith("#"):
                story.append(Paragraph(line.lstrip("#").strip(), h_style))
            else:
                formatted = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
                if formatted.startswith("- ") or formatted.startswith("* "):
                    formatted = "&bull; " + formatted[2:]
                story.append(Paragraph(formatted, body_style))

        doc.build(story)
        return buffer.getvalue()

    except ImportError:
        return None


# --------------------------------------------------
# HELPER: BUILD DATA CONTEXT & FALLBACK SUMMARY
# --------------------------------------------------

def build_dataset_summary_context(dataframe, target_col=None):
    """Create a compact statistical summary of the dataset for AI or fallback."""
    num_cols = dataframe.select_dtypes(include="number").columns.tolist()
    cat_cols = dataframe.select_dtypes(exclude="number").columns.tolist()

    context_lines = [
        f"Dataset Name: {file_name}",
        f"Total Records: {len(dataframe):,}",
        f"Total Columns: {len(dataframe.columns)} ({len(num_cols)} numerical, {len(cat_cols)} categorical)",
        f"Missing Values Remaining: {int(dataframe.isnull().sum().sum()):,}",
    ]

    if target_col and target_col in dataframe.columns:
        t_counts = dataframe[target_col].astype(str).value_counts()
        t_pcts = (t_counts / len(dataframe) * 100).round(2)
        dist_str = ", ".join(f"{k}: {t_counts[k]:,} ({t_pcts[k]}%)" for k in t_counts.index)
        context_lines.append(f"Target Variable ({target_col}) Distribution: {dist_str}")

    if num_cols:
        context_lines.append("\nNumerical Columns Summary (Mean | Median | Min | Max):")
        for col in num_cols[:8]:
            s = dataframe[col].dropna()
            if not s.empty:
                context_lines.append(
                    f"- {col}: Mean={s.mean():.2f}, Median={s.median():.2f}, "
                    f"Min={s.min():.2f}, Max={s.max():.2f}"
                )

    if cat_cols:
        context_lines.append("\nTop Categorical Distributions:")
        for col in [c for c in cat_cols if c != target_col][:8]:
            top_val = dataframe[col].astype(str).value_counts()
            if not top_val.empty:
                top_name = top_val.index[0]
                top_pct = top_val.iloc[0] / len(dataframe) * 100
                context_lines.append(f"- {col}: Most frequent is '{top_name}' ({top_pct:.1f}%)")

    return "\n".join(context_lines)


def generate_smart_fallback_report(dataframe, target_col=None):
    """Generate a clean, structured analytical summary without requiring an external API key."""
    num_cols = dataframe.select_dtypes(include="number").columns.tolist()
    cat_cols = [c for c in dataframe.select_dtypes(exclude="number").columns if c != target_col]

    report = [
        f"### 📊 Executive Summary: {file_name}",
        f"- **Dataset Size:** `{len(dataframe):,}` records across `{len(dataframe.columns)}` features.",
        f"- **Feature Breakdown:** `{len(num_cols)}` numerical columns and `{len(cat_cols) + (1 if target_col else 0)}` categorical columns.",
        f"- **Data Completeness:** `{int(dataframe.isnull().sum().sum()):,}` missing values remaining.",
    ]

    if target_col and target_col in dataframe.columns:
        t_series = dataframe[target_col].astype(str)
        t_counts = t_series.value_counts()
        t_pcts = (t_counts / len(dataframe) * 100).round(1)

        report.append(f"\n### 🎯 Target Variable (`{target_col}`) Overview")
        for label in t_counts.index:
            report.append(f"- **{target_col} ({label}):** `{t_counts[label]:,}` records (`{t_pcts[label]}%`)")

        classes = list(t_counts.index)
        pos_class = next((c for c in classes if c.lower() in ["yes", "1", "true", "churn"]), classes[-1])
        flag = (t_series == pos_class)
        overall_rate = flag.mean() * 100

        report.append(f"\n### 🔍 Key Findings & High-Impact Drivers (for `{target_col} = {pos_class}`)")
        drivers = []
        for col in cat_cols:
            grp = flag.groupby(dataframe[col].astype(str)).agg(["mean", "count"])
            grp = grp[grp["count"] >= max(20, int(0.02 * len(dataframe)))]
            if not grp.empty:
                max_cat = grp["mean"].idxmax()
                max_rate = grp.loc[max_cat, "mean"] * 100
                if max_rate > overall_rate + 3:
                    drivers.append((col, max_cat, max_rate))

        drivers.sort(key=lambda x: x[2], reverse=True)
        if drivers:
            for col, val, rate in drivers[:5]:
                report.append(
                    f"- **{col} ({val}):** Shows a `{rate:.1f}%` rate of `{target_col} = {pos_class}` "
                    f"(compared to `{overall_rate:.1f}%` overall)."
                )
        else:
            report.append("- **Distribution:** Categorical features show relatively uniform distribution across target classes.")

    if num_cols:
        report.append("\n### 📈 Numerical Feature Highlights")
        for col in num_cols[:5]:
            s = dataframe[col].dropna()
            if not s.empty:
                report.append(
                    f"- **{col}:** Average is `{s.mean():,.2f}` (Median `{s.median():,.2f}`), "
                    f"ranging from `{s.min():,.2f}` to `{s.max():,.2f}`."
                )

    report.append(
        "\n### 💡 Strategic Recommendations\n"
        "1. **Focus on High-Risk Segments:** Prioritize retention or intervention strategies on the top categorical segments identified above.\n"
        "2. **Monitor Early-Stage & High-Cost Thresholds:** Track records where numerical metrics deviate significantly from the median.\n"
        "3. **Feature Engineering for Modeling:** Use one-hot encoded categorical variables and binned numerical groups (such as tenure intervals) for predictive modeling."
    )

    return "\n".join(report)


# --------------------------------------------------
# 1. QUICK DATASET SNAPSHOT
# --------------------------------------------------

st.subheader("1. Dataset Snapshot")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Dataset", file_name)
c2.metric("Total Rows", f"{len(df):,}")
c3.metric("Total Columns", f"{len(df.columns):,}")
c4.metric("Missing Values", f"{int(df.isnull().sum().sum()):,}")


# --------------------------------------------------
# 2. AI CONFIGURATION & GENERATE BUTTON
# --------------------------------------------------

st.markdown("---")
st.subheader("2. Generate Summary")

col_cfg1, col_cfg2 = st.columns(2)

with col_cfg1:
    target_candidates = ["— None —"] + [
        c for c in df.columns if 2 <= df[c].dropna().nunique() <= 10
    ]
    saved_target = st.session_state.get("target_col")
    default_idx = (
        target_candidates.index(saved_target)
        if saved_target in target_candidates
        else (1 if len(target_candidates) > 1 else 0)
    )
    selected_target = st.selectbox(
        "Target Variable for Summary Focus",
        target_candidates,
        index=default_idx
    )
    target_col = None if selected_target == "— None —" else selected_target

with col_cfg2:
    api_key = st.text_input(
        "Gemini API Key (Optional – leave blank for built-in AI Summary)",
        type="password",
        help="Enter your Google Gemini API key to generate a live LLM response, or leave blank to use the built-in automated report generator."
    )

if st.button("🤖 Generate with AI", type="primary", use_container_width=True):
    with st.spinner("Analyzing dataset and generating summary report..."):
        data_context = build_dataset_summary_context(df, target_col)

        if api_key.strip():
            try:
                import google.generativeai as genai

                genai.configure(api_key=api_key.strip())
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = (
                    "You are an expert Data Analyst. Based on the following dataset summary, "
                    "write a clear, concise, and well-structured Markdown report covering:\n"
                    "1. Executive Overview\n"
                    "2. Key Data & Target Variable Insights\n"
                    "3. Major Patterns & Drivers\n"
                    "4. Recommendations\n\n"
                    f"Dataset Summary:\n{data_context}"
                )
                response = model.generate_content(prompt)
                st.session_state["ai_summary_report"] = response.text
                st.success("✅ Summary generated with Gemini AI!")
            except Exception as e:
                st.warning(f"⚠️ Gemini API call failed ({e}). Showing built-in automated summary instead.")
                st.session_state["ai_summary_report"] = generate_smart_fallback_report(df, target_col)
        else:
            st.session_state["ai_summary_report"] = generate_smart_fallback_report(df, target_col)
            st.success("✅ Summary Report generated successfully!")


# --------------------------------------------------
# 3. DISPLAY & DOWNLOAD GENERATED SUMMARY (PDF)
# --------------------------------------------------

if "ai_summary_report" in st.session_state:
    st.markdown("---")
    st.subheader("📋 Generated Report")

    with st.container(border=True):
        st.markdown(st.session_state["ai_summary_report"])

    pdf_bytes = generate_pdf_bytes(st.session_state["ai_summary_report"], file_name)

    if pdf_bytes is not None:
        st.download_button(
            label=" Download Summary Report (.pdf)",
            data=pdf_bytes,
            file_name="AI_Data_Summary_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    else:
        st.error(
            "⚠️ PDF library not found. Run `pip install fpdf2` or `pip install reportlab` "
            "in your terminal to enable PDF export."
        )