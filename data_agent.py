import json
import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyAdfaCDVqbNiRUX6_nURsm0QW_APfliMcA")


model = genai.GenerativeModel("gemini-1.5-flash")

class DataAgent:
    def __init__(self, db_path="database/colleges.json"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump([], f)

    def read_all(self):
        try:
            with open(self.db_path, "r") as f:
                return json.load(f)
        except:
            return []

    def create(self, college):
        data = self.read_all()
        data.append(college)
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=4)

    def fetch_from_ai(self, course, city, top_k=5):
        prompt = (
            "Provide a JSON array of top {n} colleges in India for the course '{c}' in '{city}'. "
            "Only output JSON.\n".format(n=top_k, c=course, city=city)
        )

        try:
            response = model.generate_content(prompt)
            text = response.text

            start = text.find("[")
            end = text.rfind("]")

            if start != -1 and end != -1:
                return json.loads(text[start:end+1])

            return json.loads(text)

        except Exception as e:
            print("AI JSON error:", e)
            return []
