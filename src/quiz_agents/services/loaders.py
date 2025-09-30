import json, random
from quiz_agents.config import settings

def load_quizzes(count: int) -> list[dict]:
    with open(settings.QUIZ_FILE, "r", encoding="utf-8") as f:
        all_q = json.load(f)
    return random.sample(all_q, min(count, len(all_q)))

def load_applicants() -> list[dict]:
    with open(settings.APPLICANT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
