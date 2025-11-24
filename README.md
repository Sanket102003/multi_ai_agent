Multi-AI-Agent College Assistant (Dark Mode)
-------------------------------------------
This project is an updated version of your multi-agent system with:
- Separate agents in /agents
- Dark-mode Tkinter GUI (main_gui.py)
- Gemini model updated to 'gemini-1.5-flash'
- Safer JSON parsing and error handling
- Local CRUD stored in database/colleges.json

How to run:
1. Install dependencies:
   pip install -r requirements.txt
2. Set your Gemini API key (either export GEMINI_API_KEY or use Set API Key button in the app)
   On Windows (PowerShell): $env:GEMINI_API_KEY = "YOUR_KEY"
   On mac/Linux: export GEMINI_API_KEY="YOUR_KEY"
3. Run:
   python main_gui.py

Notes:
- The app attempts to parse JSON from Gemini responses. If Gemini returns non-JSON text, parsing may fail.
- Keep your API key private.
