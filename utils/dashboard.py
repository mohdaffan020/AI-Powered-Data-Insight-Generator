# import pandas as pd
# import plotly.express as px
# import streamlit as st


# # ==================================================
# # CALCULATE KPI
# # ==================================================

# def calculate_kpi(df, column, calculation):

#     if calculation == "sum":

#         return df[column].sum()


#     elif calculation == "average":

#         return df[column].mean()


#     elif calculation == "count":

#         return df[column].count()


#     elif calculation == "unique_count":

#         return df[column].nunique()


#     elif calculation == "minimum":

#         return df[column].min()


#     elif calculation == "maximum":

#         return df[column].max()


#     return 0


# # ==================================================
# # SHOW KPI
# # ==================================================

# def show_kpis(df, kpis):

#     columns = st.columns(
#         len(kpis)
#     )


#     for i, kpi in enumerate(kpis):

#         column = kpi["column"]

#         calculation = kpi["calculation"]

#         label = kpi["label"]


#         value = calculate_kpi(
#             df,
#             column,
#             calculation
#         )


#         with columns[i]:

#             if isinstance(value, (int, float)):

#                 value = f"{value:,.2f}"

#             else:

#                 value = str(value)


#             st.metric(
#                 label,
#                 value
#             )


# # ==================================================
# # CREATE CHART
# # ==================================================

# def create_chart(df, chart):

#     chart_type = chart["type"]

#     x = chart["x"]

#     y = chart["y"]

#     title = chart["title"]


#     # --------------------------------------------------
#     # BAR CHART
#     # --------------------------------------------------

#     if chart_type == "bar":

#         chart_data = (
#             df.groupby(x)[y]
#             .sum()
#             .sort_values(
#                 ascending=False
#             )
#             .head(10)
#             .reset_index()
#         )


#         fig = px.bar(
#             chart_data,
#             x=x,
#             y=y,
#             title=title
#         )


#     # --------------------------------------------------
#     # LINE CHART
#     # --------------------------------------------------

#     elif chart_type == "line":

#         chart_data = (
#             df.groupby(x)[y]
#             .sum()
#             .reset_index()
#             .sort_values(x)
#         )


#         fig = px.line(
#             chart_data,
#             x=x,
#             y=y,
#             title=title
#         )


#     # --------------------------------------------------
#     # PIE CHART
#     # --------------------------------------------------

#     elif chart_type == "pie":

#         chart_data = (
#             df.groupby(x)[y]
#             .sum()
#             .sort_values(
#                 ascending=False
#             )
#             .head(10)
#             .reset_index()
#         )


#         fig = px.pie(
#             chart_data,
#             names=x,
#             values=y,
#             title=title
#         )


#     # --------------------------------------------------
#     # SCATTER CHART
#     # --------------------------------------------------

#     elif chart_type == "scatter":

#         fig = px.scatter(
#             df,
#             x=x,
#             y=y,
#             title=title
#         )


#     else:

#         return


#     # --------------------------------------------------
#     # SHOW CHART
#     # --------------------------------------------------

#     st.plotly_chart(
#         fig,
#         use_container_width=True
#     )