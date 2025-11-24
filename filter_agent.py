class FilterAgent:
    def filter(self, colleges, budget):
        try:
            return [c for c in colleges if int(c.get("fees", 10**9)) <= int(budget)]
        except Exception:
            return []
