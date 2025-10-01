import json, random
from quiz_agents.config import settings

def load_quizzes() -> list[dict]:
    """퀴즈 데이터를 JSON 파일에서 불러와 무작위로 `count`개를 선택합니다."""

    with open(settings.QUIZ_FILE, "r", encoding="utf-8") as f:
        all_q = json.load(f)
    return random.sample(all_q, min(settings.QUIZ_COUNT, len(all_q)))

def load_applicants() -> list[dict]:
    """지원자 데이터를 JSON 파일에서 불러옵니다."""
    
    with open(settings.APPLICANT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
