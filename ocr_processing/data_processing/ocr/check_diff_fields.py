import pandas as pd

FIELD_NAMES = [
    "DEG_NAME",
    "ISSUE_DATE",
    "V_DOB",
    "V_GENDER",
    "V_MODE",
    "V_NAME",
    "V_RANKING",
    "V_REF_NO",
    "V_SERIAL_NO",
    "V_SIGN_NAME",
]


for field_name in FIELD_NAMES:
    print(field_name)
    df1 = pd.read_excel("report_out.xlsx", sheet_name="Sheet1")
    df1 = df1[df1["field_name"] == field_name]

    df2 = pd.read_excel("~/Downloads/phase1.xlsx", sheet_name="Sheet1")
    df2 = df2[df2["field_name"] == field_name]

    for idx1, row1 in df1.iterrows():
        for idx2, row2 in df2.iterrows():
            if row1["file_name"] == row2["file_name"]:
                if row1["true_or_false"] != row2["true_or_false"] \
                   or row1["Number of letters"] != row2["Number of letters"] \
                   or row1["Correct letters"] != row2["Correct letters"] \
                   or row1["OCR letters"] != row2["OCR letters"] \
                   or row1["diff_str_len"] != row2["diff_str_len"]:
                    print(row1["file_name"])
