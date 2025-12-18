import csv
import json
from io import StringIO

import streamlit as st

from csv_profiler.profiling import profile_rows
from csv_profiler.render import write_markdown



st.set_page_config(page_title="CSV Profiler", layout="wide")
st.title("CSV Profiler")

# ========== SIDEBAR ==========
st.sidebar.header("Upload CSV")
uploaded = st.sidebar.file_uploader(
    "Upload CSV",
    type=["csv"],
    help="Upload a CSV file to profile",
)

# ========== PREVIEW ==========
if uploaded:
    text = uploaded.getvalue().decode("utf-8", errors="replace")
    rows = list(csv.DictReader(StringIO(text)))

    st.subheader("Data Preview")
    st.dataframe(rows[:5], use_container_width=True)

    if st.button("Generate Profile"):
        st.session_state["profile"] = profile_rows(rows)

# ========== RESULTS ==========
if "profile" in st.session_state:
    profile = st.session_state["profile"]

    st.subheader("Dataset Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", profile["n_rows"])
    c2.metric("Columns", profile["n_cols"])
    c3.metric(
        "Missing Cells",
        sum(col["missing"] for col in profile["columns"]),
    )

    st.subheader("Column Details")
    st.dataframe(profile["columns"], use_container_width=True)

    st.subheader("Downloads")

    json_data = json.dumps(profile, indent=2, ensure_ascii=False)

    # توليد Markdown بنفس renderer حقك
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as tmp:
        write_markdown(profile, tmp.name)
        md_data = open(tmp.name, encoding="utf-8").read()
        os.unlink(tmp.name)

    d1, d2 = st.columns(2)
    d1.download_button(
        "Download JSON",
        data=json_data,
        file_name="profile.json",
        mime="application/json",
        use_container_width=True,
    )
    d2.download_button(
        "Download Markdown",
        data=md_data,
        file_name="profile.md",
        mime="text/markdown",
        use_container_width=True,
    )

else:
    st.info("Upload a CSV file from the sidebar to begin")

