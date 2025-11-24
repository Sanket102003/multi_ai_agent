
Multi-AI-Agent College Assistant — Streamlit version
===================================================
This project is a Streamlit re-implementation of your Tkinter UI using AGGrid for clickable table selection.
It preserves your agent logic (if you include the `agents/` package in the deployment) and uses the same DB path `database/colleges.json`.

How to run locally:
1. Install dependencies:
   pip install -r requirements.txt
2. Make sure you have your `agents/` folder (DataAgent, FilterAgent, CompareAgent, RecommendationAgent) present.
   If not present, the app will fall back to file-based behavior but won't call AI agents.
3. Run:
   streamlit run streamlit_app.py

Deployment notes (Streamlit Cloud):
- Include the full repo (this app + `agents/` folder + `database/colleges.json`) in your GitHub repo.
- Make sure `requirements.txt` lists all dependencies (this file includes streamlit-aggrid).
- Set the GEMINI_API_KEY in Streamlit secrets/environment variables, or use the Set API Key input in the app.

