import os
from pathlib import Path
import streamlit as st
import pandas as pd
import json

st.set_page_config(layout="wide", page_title="Multi-AI College Assistant (Web)")

# --- Try to load agents (same logic you used) ---
AGENTS_AVAILABLE = True
try:
    from agents.data_agent import DataAgent
    from agents.filter_agent import FilterAgent
    from agents.compare_agent import CompareAgent
    from agents.recommend_agent import RecommendationAgent
except Exception as e:
    AGENTS_AVAILABLE = False
    st.warning(
        "Could not import agents package; falling back to file-based behavior.\n"
        "Make sure you upload the 'agents' folder when deploying.\n\n"
        f"Import error: {e}"
    )

# Database location
DB_DIR = Path("database")
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "colleges.json"


def read_db():
    if not DB_PATH.exists():
        return []
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to read DB: {e}")
        return []


def write_db(rows):
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Failed to write DB: {e}")


# Initialize agents
if AGENTS_AVAILABLE:
    data_agent = DataAgent(db_path=str(DB_PATH))
    filter_agent = FilterAgent()
    compare_agent = CompareAgent()
    recommend_agent = RecommendationAgent()
else:
    data_agent = None
    filter_agent = None
    compare_agent = None
    recommend_agent = None


# ---- Header (Dark mode like your Tkinter UI) ----
st.markdown(
    """
    <div style='background:#1e1e2f;padding:10px;border-radius:6px'>
    <h2 style='color:#e6e6e6;margin:0'>Multi-AI College Assistant (Web) — Dark Mode</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# ---- Top Inputs ----
col1, col2, col3, col4 = st.columns([2, 2, 1.2, 1.2])

course = col1.text_input("Course", "")
city = col2.text_input("City", "")
budget = col3.text_input("Budget (₹)", "")
api_key = col4.text_input("Set API Key (GEMINI_API_KEY)", type="password")

if api_key:
    os.environ["GEMINI_API_KEY"] = api_key
    st.success("API key set for this session.")


# ---- Buttons ----
b1, b2, b3, b4, b5, b6 = st.columns([1, 1, 1, 1, 1, 1])

fetch_clicked = b1.button("Fetch (AI)")
filter_clicked = b2.button("Filter")
compare_clicked = b3.button("Compare")
recommend_clicked = b4.button("Recommend")
load_clicked = b5.button("Load DB")
setkey_clicked = b6.button("Set API Key")


# ---- Main Body (Two Columns) ----
left, right = st.columns([1, 1])

# Load data
if AGENTS_AVAILABLE:
    data = data_agent.read_all()
else:
    data = read_db()

# Create dataframe
if isinstance(data, list):
    df = pd.DataFrame(data)
else:
    df = pd.DataFrame()

if df.empty:
    display_df = pd.DataFrame(columns=["index", "name", "city", "fees", "rating"])
else:
    display_df = df.copy()

    for col in ["name", "city", "fees", "rating"]:
        if col not in display_df.columns:
            display_df[col] = ""

    display_df["fees"] = display_df["fees"].astype(str)
    display_df["rating"] = display_df["rating"].astype(str)
    display_df.insert(0, "index", display_df.index.astype(int))


left.markdown("### Colleges")

# AGGrid table
selected_index = None
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_selection("single", use_checkbox=False)
    gb.configure_columns(["index"], editable=False)
    grid_options = gb.build()

    grid_response = AgGrid(
        display_df,
        gridOptions=grid_options,
        height=450,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True
    )

    selected_rows = grid_response.get("selected_rows", [])
    if selected_rows:
        selected_index = int(selected_rows[0]["index"])

except Exception as e:
    left.warning("AGGrid not installed. Falling back to a simple selectbox.")
    options = [
        f"{i}. {r['name']} — {r['city']} — ₹{r['fees']} — {r['rating']}"
        for i, r in display_df.iterrows()
    ]
    choice = left.selectbox("Select College", options) if options else None
    if choice:
        selected_index = int(choice.split(".")[0])


# ---- Button actions ----
if load_clicked:
    st.experimental_rerun()


# Fetch AI
if fetch_clicked:
    if not course or not city:
        st.warning("Enter Course and City first.")
    else:
        if AGENTS_AVAILABLE:
            with st.spinner("Fetching from Gemini AI..."):
                fetched = data_agent.fetch_from_ai(course, city, top_k=5)

                if fetched:
                    for c in fetched:

                        try:
                            c["fees"] = int(c.get("fees", 0))
                        except:
                            import re
                            s = str(c.get("fees", ""))
                            nums = re.findall(r"\d+", s)
                            c["fees"] = int(nums[0]) if nums else 0

                        try:
                            c["rating"] = float(c.get("rating", 0))
                        except:
                            c["rating"] = 0.0

                        data_agent.create(c)

                    st.success("Fetched & stored successfully.")
                    st.experimental_rerun()
                else:
                    st.info("No AI results. Check API key & internet.")
        else:
            st.error("Agents folder missing! Include it before deploying.")


# Filter
if filter_clicked:
    if not budget.isdigit():
        st.warning("Enter numeric budget.")
    else:
        if AGENTS_AVAILABLE:
            filtered = filter_agent.filter(data, int(budget))
        else:
            filtered = [
                c for c in data
                if isinstance(c.get("fees", 0), (int, float)) and c["fees"] <= int(budget)
            ]

        left.write(f"**{len(filtered)} colleges found.**")
        left.dataframe(pd.DataFrame(filtered))


# Compare
if compare_clicked:
    if selected_index is not None:
        colleges = [data[selected_index]]
    else:
        colleges = data

    if AGENTS_AVAILABLE:
        best = compare_agent.compare(colleges)
    else:
        best = None

    right.markdown("### Details / AI Output")

    if best:
        right.text_area("Output", f"Best: {best['name']}\nReason: {best['reason']}", height=300)
    else:
        right.text_area("Output", "No result.", height=300)


# Recommend
if recommend_clicked:
    if selected_index is None:
        st.info("Select a college first.")
    else:
        if AGENTS_AVAILABLE:
            reco = recommend_agent.recommend(data[selected_index])
            right.text_area("Recommendation", reco, height=300)
        else:
            right.text_area("Recommendation", "Agents missing.", height=300)


# ---- DB Preview ----
st.markdown("---")
st.markdown("#### Database Preview")
st.write(display_df)
st.caption(f"Database path: {DB_PATH}")

