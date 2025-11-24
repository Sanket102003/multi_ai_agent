import os
import google.generativeai as genai
import json

genai.configure(api_key="AIzaSyAdfaCDVqbNiRUX6_nURsm0QW_APfliMcA")


model = genai.GenerativeModel("gemini-1.5-flash")

class RecommendationAgent:

    def recommend(self, best_college):
        if not best_college:
            return "No recommendation."

        json_data = json.dumps(best_college)

        prompt = (
            "Write a short 3-line recommendation for this college:\n"
            f"{json_data}"
        )

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print("Recommend error:", e)
            return "Recommendation failed."
