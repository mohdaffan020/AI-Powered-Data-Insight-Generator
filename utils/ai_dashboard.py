# import json


# # ==================================================
# # CREATE DASHBOARD PLAN
# # ==================================================

# def create_dashboard_plan(client, df):

#     # --------------------------------------------------
#     # GET COLUMN INFORMATION
#     # --------------------------------------------------

#     numeric_columns = (
#         df.select_dtypes(include="number")
#         .columns
#         .tolist()
#     )

#     categorical_columns = (
#         df.select_dtypes(include="object")
#         .columns
#         .tolist()
#     )

#     date_columns = (
#         df.select_dtypes(include="datetime")
#         .columns
#         .tolist()
#     )

#     # --------------------------------------------------
#     # DATASET INFORMATION
#     # --------------------------------------------------

#     dataset_info = f"""
# Dataset rows: {df.shape[0]}

# Dataset columns: {df.shape[1]}

# Numerical columns:
# {numeric_columns}

# Categorical columns:
# {categorical_columns}

# Date columns:
# {date_columns}
# """

#     # --------------------------------------------------
#     # AI PROMPT
#     # --------------------------------------------------

#     prompt = f"""
# You are an expert business dashboard designer.

# Analyze this dataset:

# {dataset_info}


# ==============================
# DASHBOARD REQUIREMENTS
# ==============================

# Create a simple business dashboard.

# The dashboard should contain:

# 1. Maximum 4 KPIs.

# 2. Exactly 4 charts when the dataset
#    contains enough suitable columns.

# 3. Maximum 3 dashboard filters.


# ==============================
# KPI REQUIREMENTS
# ==============================

# Allowed calculations:

# - sum
# - average
# - count
# - unique_count
# - minimum
# - maximum


# Choose KPIs that are useful for understanding
# the business performance.

# Do not use:

# - IDs
# - phone numbers
# - order numbers
# - customer IDs
# - product IDs

# as business measures.


# ==============================
# CHART REQUIREMENTS
# ==============================

# Allowed chart types:

# - bar
# - line
# - pie
# - scatter


# Try to create different types of analysis:

# 1. Trend analysis
#    Use a date column and numerical column.
#    Prefer a line chart.

# 2. Category comparison
#    Use a categorical column and numerical column.
#    Prefer a bar chart.

# 3. Regional/category performance
#    Use another useful categorical column.

# 4. Distribution or relationship
#    Use pie or scatter when appropriate.


# Do not create duplicate charts.

# Choose the BEST charts rather than random charts.


# ==============================
# FILTER REQUIREMENTS
# ==============================

# Select up to 3 useful filters.

# Prefer:

# - categorical columns
# - date columns

# Do NOT use:

# - identifiers
# - order IDs
# - customer IDs
# - product IDs
# - phone numbers
# - columns with too many unique values

# For categorical filters, prefer columns
# with a reasonable number of categories.


# ==============================
# IMPORTANT RULES
# ==============================

# - Use ONLY columns that actually exist.
# - Never invent column names.
# - Do not use identifiers as business measures.
# - Use numerical columns for KPIs.
# - Use categorical columns for category analysis.
# - Use date columns for trend analysis.
# - Keep titles simple.
# - Make the dashboard understandable to
#   a non-technical user.


# ==============================
# OUTPUT FORMAT
# ==============================

# Return ONLY valid JSON.

# Do NOT return markdown.
# Do NOT return ```json.
# Do NOT return explanations.

# Use exactly this structure:

# {{
#     "title": "Dashboard Title",

#     "kpis": [
#         {{
#             "label": "KPI name",
#             "column": "column name",
#             "calculation": "sum"
#         }}
#     ],

#     "filters": [
#         {{
#             "column": "Region",
#             "type": "categorical"
#         }},
#         {{
#             "column": "OrderDate",
#             "type": "date"
#         }}
#     ],

#     "charts": [
#         {{
#             "type": "line",
#             "x": "OrderDate",
#             "y": "Sales",
#             "title": "Sales Over Time"
#         }},
#         {{
#             "type": "bar",
#             "x": "Region",
#             "y": "Sales",
#             "title": "Sales by Region"
#         }},
#         {{
#             "type": "bar",
#             "x": "Category",
#             "y": "Profit",
#             "title": "Profit by Category"
#         }},
#         {{
#             "type": "pie",
#             "x": "Category",
#             "y": "Sales",
#             "title": "Sales Contribution"
#         }}
#     ]
# }}
# """

#     # --------------------------------------------------
#     # GEMINI REQUEST
#     # --------------------------------------------------

#     response = client.models.generate_content(
#         model="gemini-3.5-flash",
#         contents=prompt
#     )

#     # --------------------------------------------------
#     # GET RESPONSE
#     # --------------------------------------------------

#     result = response.text.strip()



#     # --------------------------------------------------
#     # REMOVE MARKDOWN CODE BLOCK
#     # --------------------------------------------------

#     if result.startswith("```"):

#         result = result.replace(
#             "```json",
#             ""
#         )

#         result = result.replace(
#             "```",
#             ""
#         )

#         result = result.strip()

#     # --------------------------------------------------
#     # CONVERT JSON
#     # --------------------------------------------------

#     dashboard_plan = json.loads(result)

#     return dashboard_plan