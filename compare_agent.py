import json
import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyAdfaCDVqbNiRUX6_nURsm0QW_APfliMcA")


model = genai.GenerativeModel("gemini-1.5-flash")

class CompareAgent:

    def compare(self, colleges):
        if not colleges:
            return None

        json_data = json.dumps(colleges)

        prompt = (
            "Choose the BEST college from this list (JSON):\n"
            f"{json_data}\n\n"
            "Return ONLY JSON object:\n"
            '{"name": "...", "reason": "..."}'
        )

        try:
            response = model.generate_content(prompt)
            text = response.text

            start = text.find("{")
            end = text.rfind("}")

            return json.loads(text[start:end+1])

        except Exception as e:
            print("Compare error:", e)
            return None
