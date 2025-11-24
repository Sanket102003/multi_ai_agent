
import os
import streamlit as st
import json
import pandas as pd
from pathlib import Path

st.set_page_config(layout="wide", page_title="Multi-AI College Assistant (Web)")

# Try to import agents; if they aren't available, we'll fall back to simple file-based operations.
try:
    from agents.data_agent import DataAgent
    from agents.filter_agent import FilterAgent
    from agents.compare_agent import CompareAgent
    from agents.recommend_agent import RecommendationAgent
    AGENTS_AVAILABLE = True
except Exception as e:
    AGENTS_AVAILABLE = False
    st.warning("Could not import agents package; falling back to local-file behavior. "
               "If you have an 'agents' folder, include it in the deployment.\n"
               f"Import error: {e}")

# Use database path compatible with original app
DB_DIR = Path("database")
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "colleges.json"

# Fallback simple functions if agents not available
def read_db():
    if not DB_PATH.exists():
        return []
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to read DB: {e}")
        return []

def write_db(items):
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Failed to write DB: {e}")

# Initialize agents if available
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

# --- UI reproducing Tkinter layout (top inputs, buttons, two columns) ---
st.markdown("<h2 style='color:#e6e6e6;background:#1e1e2f;padding:8px;border-radius:6px'>Multi-AI College Assistant (Web) — Dark Mode</h2>", unsafe_allow_html=True)
# top inputs
cols = st.columns([2,2,1,1])
course = cols[0].text_input("Course", "")
city = cols[1].text_input("City", "")
budget = cols[2].text_input("Budget (₹)", "")
api_key_input = cols[3].text_input("Set API Key (GEMINI_API_KEY)", type="password")

if api_key_input:
    os.environ["GEMINI_API_KEY"] = api_key_input
    st.success("API key set for this session.")

btn1, btn2, btn3, btn4, btn5, btn6 = st.columns([1,1,1,1,1,1])
fetch_clicked = btn1.button("Fetch (AI)")
filter_clicked = btn2.button("Filter")
compare_clicked = btn3.button("Compare")
recommend_clicked = btn4.button("Recommend")
load_clicked = btn5.button("Load DB")
setkey_clicked = btn6.button("Set API Key")  # duplicate UI for parity; no-op

# Body: two columns (left: table, right: output)
left, right = st.columns([1,1])

# Load data
if AGENTS_AVAILABLE:
    data = data_agent.read_all()
else:
    data = read_db()

df = pd.DataFrame(data)
if df.empty:
    df_display = pd.DataFrame(columns=["index","name","city","fees","rating"])
else:
    df_display = df.copy()
    # normalize fees and rating columns if present
    if "fees" in df_display.columns:
        df_display["fees"] = df_display["fees"].astype(str)
    if "rating" in df_display.columns:
        df_display["rating"] = df_display["rating"].astype(str)
    df_display.insert(0, "index", df_display.index.astype(int))

left.markdown("### Colleges")
# AG Grid integration
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    gb = GridOptionsBuilder.from_dataframe(df_display)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_columns(["index"], editable=False)
    grid_options = gb.build()
    grid_response = AgGrid(df_display, gridOptions=grid_options, height=400, update_mode=GridUpdateMode.SELECTION_CHANGED)
    selected = grid_response.get("selected_rows", [])
    selected_index = None
    if selected:
        selected_index = int(selected[0].get("index", 0))
except Exception as e:
    st.error("st_aggrid not available or failed to render. Ensure streamlit-aggrid is installed.")
    st.write(df_display)
    selected_index = None

# Buttons behavior
if load_clicked:
    st.experimental_rerun()

if fetch_clicked:
    if not course or not city:
        st.warning("Enter course and city first.")
    else:
        if AGENTS_AVAILABLE:
            with st.spinner("Fetching from Gemini AI..."):
                cols_fetched = data_agent.fetch_from_ai(course, city, top_k=5)
                if cols_fetched:
                    # sanitize and store
                    for c in cols_fetched:
                        try:
                            c['fees'] = int(c.get('fees', 0))
                        except:
                            import re
                            s = str(c.get('fees',''))
                            nums = re.findall(r'\d+', s)
                            c['fees'] = int(nums[0]) if nums else 0
                        try:
                            c['rating'] = float(c.get('rating', 0))
                        except:
                            c['rating'] = 0.0
                        data_agent.create(c)
                    st.success("Fetched and stored in local DB.")
                    st.experimental_rerun()
                else:
                    st.info("No AI results returned. Make sure your API key is set and internet works.")
        else:
            st.error("Agents not available in deployment. Please include the 'agents' folder.")

if filter_clicked:
    if not budget.isdigit():
        st.warning("Enter numeric budget.")
    else:
        if AGENTS_AVAILABLE:
            filtered = filter_agent.filter(data, int(budget))
        else:
            # naive local filter
            filtered = [c for c in data if isinstance(c.get("fees",0), (int,float)) and c.get("fees",0) <= int(budget)]
        # show filtered results in left panel
        left.write(f"**{len(filtered)} colleges match the budget.**")
        if filtered:
            left.dataframe(pd.DataFrame(filtered).assign(index=lambda df: df.index))
        else:
            left.write("No matches.")

if compare_clicked:
    if selected_index is not None:
        colleges = [data[selected_index]] if 0 <= selected_index < len(data) else data
    else:
        colleges = data
    if AGENTS_AVAILABLE:
        best = compare_agent.compare(colleges)
    else:
        # simple compare fallback: pick max rating then min fees
        best = None
        for c in colleges:
            if not best:
                best = {"name": c.get("name"), "reason": "fallback compare"}
        # no strong logic in fallback
    right.markdown("### Details / AI Output")
    if best:
        right.text_area("Output", value=f"Best: {best.get('name')}\nReason: {best.get('reason')}", height=300)
    else:
        right.text_area("Output", value='Comparison failed or returned no result.', height=300)

if recommend_clicked:
    if selected_index is None:
        st.info("Select a college from the table first.")
    else:
        if AGENTS_AVAILABLE:
            candidate = data[selected_index]
            reco = recommend_agent.recommend(candidate)
            right.text_area("Recommendation", value=reco, height=300)
        else:
            right.text_area("Recommendation", value="Recommend agent not available in deployment.", height=300)

# Show DB below for convenience
st.markdown("---")
st.markdown("#### Current DB preview")
st.write(df_display)
st.caption(f"Database path: {DB_PATH}")
