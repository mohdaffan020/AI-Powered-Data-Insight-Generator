# import pandas as pd
# import numpy as np
# import difflib
# import re
# from datetime import datetime

# from utils.data_types import detect_column_types


# # ============================================================
# # BASIC CLEANING OPERATIONS
# # ============================================================

# def remove_duplicates(df):
#     """
#     Remove duplicate rows.
#     """

#     return df.drop_duplicates().reset_index(drop=True)


# def remove_empty_rows(df):
#     """
#     Remove completely empty rows.
#     """

#     return df.dropna(
#         how="all"
#     ).reset_index(drop=True)


# def remove_empty_columns(df):
#     """
#     Remove completely empty columns.
#     """

#     return df.dropna(
#         axis=1,
#         how="all"
#     )


# # ============================================================
# # MISSING VALUE HANDLING
# # ============================================================

# def fill_missing_values(df):
#     """
#     Fill missing values intelligently.

#     Numeric:
#         Median

#     Categorical:
#         Unknown
#     """

#     cleaned_df = df.copy()

#     numeric_columns = cleaned_df.select_dtypes(
#         include="number"
#     ).columns

#     for column in numeric_columns:

#         if cleaned_df[column].isna().any():

#             median_value = cleaned_df[
#                 column
#             ].median()

#             cleaned_df[column] = (
#                 cleaned_df[column].fillna(
#                     median_value
#                 )
#             )


#     categorical_columns = cleaned_df.select_dtypes(
#         include=["object", "category"]
#     ).columns

#     for column in categorical_columns:

#         if cleaned_df[column].isna().any():

#             cleaned_df[column] = (
#                 cleaned_df[column].fillna(
#                     "Unknown"
#                 )
#             )


#     return cleaned_df


# # ============================================================
# # TEXT CLEANING
# # ============================================================

# def trim_spaces(df):
#     """
#     Remove unnecessary spaces from text columns.
#     """

#     cleaned_df = df.copy()

#     text_columns = cleaned_df.select_dtypes(
#         include=["object", "string"]
#     ).columns

#     for column in text_columns:

#         cleaned_df[column] = (
#             cleaned_df[column]
#             .astype("string")
#             .str.strip()
#         )

#     return cleaned_df


# def standardize_case(df):
#     """
#     Standardize text values.

#     Uses title case for text columns.
#     """

#     cleaned_df = df.copy()

#     text_columns = cleaned_df.select_dtypes(
#         include=["object", "string"]
#     ).columns

#     for column in text_columns:

#         cleaned_df[column] = (
#             cleaned_df[column]
#             .astype("string")
#             .str.strip()
#             .str.title()
#         )

#     return cleaned_df

# # ============================================================
# # CATEGORICAL VALUE STANDARDIZATION
# # ============================================================

# def standardize_categorical_values(df):
#     """
#     Standardize categorical values automatically.

#     Handles:
#         None / NaN / "None" / "nan" / "" -> "N/A"

#         Different capitalization:
#             west -> West
#             WEST -> West
#             food -> Food
#             CASH -> Cash

#         Common spelling mistakes:
#             wst -> West
#             Returinng -> Returning
#             Returing -> Returning

#     The function learns the correct category from
#     the values already present in the dataset.
#     """

#     cleaned_df = df.copy()

#     categorical_columns = cleaned_df.select_dtypes(
#         include=["object", "string", "category"]
#     ).columns

#     correction_log = []

#     for column in categorical_columns:

#         # ----------------------------------------------------
#         # Convert actual missing values to N/A
#         # ----------------------------------------------------

#         cleaned_df[column] = (
#             cleaned_df[column]
#             .replace(
#                 [
#                     None,
#                     "None",
#                     "none",
#                     "NONE",
#                     "nan",
#                     "NaN",
#                     "NAN",
#                     "",
#                     " ",
#                     "null",
#                     "NULL"
#                 ],
#                 pd.NA
#             )
#         )

#         cleaned_df[column] = (
#             cleaned_df[column]
#             .fillna("N/A")
#             .astype("string")
#             .str.strip()
#         )

#         # ----------------------------------------------------
#         # Standardize capitalization
#         # ----------------------------------------------------

#         cleaned_df[column] = (
#             cleaned_df[column]
#             .where(
#                 cleaned_df[column] == "N/A",
#                 cleaned_df[column].str.title()
#             )
#         )

#         # ----------------------------------------------------
#         # Build canonical category list
#         # ----------------------------------------------------

#         values = cleaned_df[column]

#         valid_values = values[
#             values != "N/A"
#         ]

#         if valid_values.empty:
#             continue

#         value_counts = (
#             valid_values
#             .value_counts()
#         )

#         canonical_values = (
#             value_counts.index.tolist()
#         )

#         # ----------------------------------------------------
#         # Correct similar values
#         # ----------------------------------------------------

#         for value in canonical_values:

#             # Don't modify N/A
#             if value == "N/A":
#                 continue

#             matches = difflib.get_close_matches(
#                 value,
#                 canonical_values,
#                 n=2,
#                 cutoff=0.80
#             )

#             if not matches:
#                 continue

#             best_match = matches[0]

#             if best_match == value:
#                 continue

#             # Only replace a less frequent value
#             # with a more frequent value.
#             current_frequency = (
#                 value_counts.get(
#                     value,
#                     0
#                 )
#             )

#             best_frequency = (
#                 value_counts.get(
#                     best_match,
#                     0
#                 )
#             )

#             if best_frequency > current_frequency:

#                 mask = (
#                     cleaned_df[column]
#                     == value
#                 )

#                 affected_rows = int(
#                     mask.sum()
#                 )

#                 if affected_rows > 0:

#                     cleaned_df.loc[
#                         mask,
#                         column
#                     ] = best_match

#                     correction_log.append(
#                         {
#                             "Column": column,
#                             "Original Value": value,
#                             "Corrected Value": best_match,
#                             "Rows Changed": affected_rows
#                         }
#                     )

#     return (
#         cleaned_df,
#         correction_log
#     )

# # ============================================================
# # COLUMN NAME CLEANING
# # ============================================================

# def clean_column_names(df):
#     """
#     Standardize column names.

#     Example:

#         Customer Name
#         →
#         customer_name
#     """

#     cleaned_df = df.copy()

#     cleaned_df.columns = (
#         cleaned_df.columns
#         .astype(str)
#         .str.strip()
#         .str.lower()
#         .str.replace(
#             r"[^a-zA-Z0-9]+",
#             "_",
#             regex=True
#         )
#         .str.strip("_")
#     )

#     return cleaned_df


# # ============================================================
# # NUMERIC VALUE PARSER
# # ============================================================

# def parse_numeric_value(value):
#     """
#     Convert business-formatted numeric values into numbers.

#     Handles:

#         1,250
#         ₹500
#         ₹-500
#         Rs 176.00
#         INR 500
#         $1,200
#         (500)
#         500.25
#     """

#     if pd.isna(value):

#         return np.nan


#     value = str(value).strip()


#     if value == "":
#         return np.nan


#     # Negative numbers written as:
#     # (500)

#     is_parentheses_negative = (
#         value.startswith("(")
#         and value.endswith(")")
#     )


#     # Remove currency symbols/text

#     value = re.sub(
#         r"(₹|Rs\.?|INR|\$|€|£)",
#         "",
#         value,
#         flags=re.IGNORECASE
#     )


#     # Remove commas

#     value = value.replace(
#         ",",
#         ""
#     )


#     # Remove spaces

#     value = value.strip()


#     # Remove parentheses

#     value = value.replace(
#         "(",
#         ""
#     ).replace(
#         ")",
#         ""
#     )


#     try:

#         number = float(value)

#     except (
#         ValueError,
#         TypeError
#     ):

#         return np.nan


#     if is_parentheses_negative:

#         number = -abs(number)


#     return number


# # ============================================================
# # PERCENTAGE PARSER
# # ============================================================

# def parse_percentage_value(value):
#     """
#     Convert percentage values to decimal form.

#     Examples:

#         10%   -> 0.10
#         25%   -> 0.25
#         125%  -> 1.25
#         0.05  -> 0.05

#     This creates a consistent numeric representation.
#     """

#     if pd.isna(value):

#         return np.nan


#     value = str(value).strip()


#     if value == "":

#         return np.nan


#     has_percentage_symbol = "%" in value


#     # Remove currency symbols if accidentally present

#     value = re.sub(
#         r"(₹|Rs\.?|INR|\$|€|£)",
#         "",
#         value,
#         flags=re.IGNORECASE
#     )


#     value = value.replace(
#         ",",
#         ""
#     )


#     value = value.replace(
#         "%",
#         ""
#     )


#     value = value.strip()


#     try:

#         number = float(value)

#     except (
#         ValueError,
#         TypeError
#     ):

#         return np.nan


#     if has_percentage_symbol:

#         number = number / 100


#     return number


# # ============================================================
# # DATE PARSER
# # ============================================================

# def parse_date_column(series):
#     """
#     Convert mixed date formats into datetime.

#     Handles common formats such as:

#         2025-04-22
#         2025/04/22
#         22-04-2025
#         22/04/2025
#         04/22/2025
#         22 Apr 2025
#         April 22, 2025
#         2025-04-22 14:30
#         ISO timestamps
#     """

#     values = series.copy()


#     # Already datetime

#     if pd.api.types.is_datetime64_any_dtype(
#         values
#     ):

#         return values


#     non_null = values.dropna()


#     if len(non_null) == 0:

#         return pd.to_datetime(
#             values,
#             errors="coerce"
#         )


#     # --------------------------------------------------------
#     # Try standard mixed parser
#     # --------------------------------------------------------

#     try:

#         parsed_normal = pd.to_datetime(
#             values,
#             errors="coerce",
#             format="mixed"
#         )

#     except TypeError:

#         parsed_normal = pd.to_datetime(
#             values,
#             errors="coerce"
#         )


#     normal_success = (
#         parsed_normal.notna().mean()
#     )


#     # --------------------------------------------------------
#     # Try day-first parser
#     # --------------------------------------------------------

#     try:

#         parsed_dayfirst = pd.to_datetime(
#             values,
#             errors="coerce",
#             format="mixed",
#             dayfirst=True
#         )

#     except TypeError:

#         parsed_dayfirst = pd.to_datetime(
#             values,
#             errors="coerce",
#             dayfirst=True
#         )


#     dayfirst_success = (
#         parsed_dayfirst.notna().mean()
#     )


#     # Use whichever interpretation successfully
#     # parses more values.

#     if dayfirst_success > normal_success:

#         return parsed_dayfirst


#     return parsed_normal


# # ============================================================
# # DATA TYPE CONVERSION
# # ============================================================

# def convert_data_types(df):
#     """
#     Convert columns according to semantic types.

#     Semantic types come from:

#         utils.data_types.detect_column_types()

#     Rules:

#         Identifier   → keep as text
#         Date         → datetime
#         Currency     → numeric
#         Percentage   → decimal numeric
#         Numeric      → numeric
#         Categorical  → keep as text
#     """

#     cleaned_df = df.copy()


#     detected_types = detect_column_types(
#         cleaned_df
#     )


#     conversion_log = []


#     for column in cleaned_df.columns:

#         detected_type = detected_types.get(
#             column,
#             "Categorical"
#         )


#         before_dtype = str(
#             cleaned_df[column].dtype
#         )


#         # ====================================================
#         # DATE
#         # ====================================================

#         if detected_type == "Date":

#             converted = parse_date_column(
#                 cleaned_df[column]
#             )

#             cleaned_df[column] = converted


#         # ====================================================
#         # CURRENCY
#         # ====================================================

#         elif detected_type == "Currency":

#             cleaned_df[column] = (
#                 cleaned_df[column]
#                 .apply(parse_numeric_value)
#             )


#         # ====================================================
#         # PERCENTAGE
#         # ====================================================

#         elif detected_type == "Percentage":

#             cleaned_df[column] = (
#                 cleaned_df[column]
#                 .apply(parse_percentage_value)
#             )


#         # ====================================================
#         # NUMERIC
#         # ====================================================

#         elif detected_type == "Numeric":

#             cleaned_df[column] = (
#                 cleaned_df[column]
#                 .apply(parse_numeric_value)
#             )


#         # ====================================================
#         # IDENTIFIER
#         # ====================================================

#         elif detected_type == "Identifier":

#             cleaned_df[column] = (
#                 cleaned_df[column]
#                 .astype("string")
#                 .str.strip()
#             )


#         # ====================================================
#         # CATEGORICAL
#         # ====================================================

#         elif detected_type == "Categorical":

#             # Keep categorical/text fields as text.
#             cleaned_df[column] = (
#                 cleaned_df[column]
#                 .astype("string")
#                 .str.strip()
#             )


#         after_dtype = str(
#             cleaned_df[column].dtype
#         )


#         # ====================================================
#         # LOG ACTUAL CHANGES
#         # ====================================================

#         if before_dtype != after_dtype:

#             conversion_log.append(
#                 {
#                     "Column": column,
#                     "Detected Type": detected_type,
#                     "Before": before_dtype,
#                     "After": after_dtype
#                 }
#             )


#     return (
#         cleaned_df,
#         conversion_log
#     )


# # ============================================================
# # CLEANING SUMMARY
# # ============================================================

# def get_dataset_summary(df):
#     """
#     Return important dataset statistics.
#     """

#     return {
#         "rows": len(df),

#         "columns": len(df.columns),

#         "missing_values": int(
#             df.isnull().sum().sum()
#         ),

#         "duplicate_rows": int(
#             df.duplicated().sum()
#         ),

#         "numeric_columns": len(
#             df.select_dtypes(
#                 include="number"
#             ).columns
#         ),

#         "date_columns": len(
#             df.select_dtypes(
#                 include=["datetime"]
#             ).columns
#         ),
#     }


# # ============================================================
# # CLEANING HISTORY ENTRY
# # ============================================================

# def create_cleaning_history_entry(
#     operation,
#     before,
#     after,
#     details=""
# ):
#     """
#     Create one cleaning history record.
#     """

#     return {
#         "Time": datetime.now().strftime(
#             "%H:%M:%S"
#         ),

#         "Operation": operation,

#         "Rows Before": before["rows"],

#         "Rows After": after["rows"],

#         "Missing Before": (
#             before["missing_values"]
#         ),

#         "Missing After": (
#             after["missing_values"]
#         ),

#         "Duplicates Before": (
#             before["duplicate_rows"]
#         ),

#         "Duplicates After": (
#             after["duplicate_rows"]
#         ),

#         "Details": details,
#     }