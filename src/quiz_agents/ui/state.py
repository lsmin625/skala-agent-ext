def init_state() -> dict:
    """초기 상태를 설정합니다."""
    return {
        "app_state": {
            "chat_history": [],
            "role": "unknown",
            "questions": [],
            "quiz_index": 0,
            "user_answers": [],
        }
    }
