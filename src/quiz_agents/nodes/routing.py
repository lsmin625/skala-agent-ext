from langchain_core.prompts import ChatPromptTemplate
from quiz_agents.config import settings
from quiz_agents.services.llm import llm_with_role_route
from quiz_agents.nodes.state import AppState

def classify_role(text: str) -> str:
    """ 사용자 입력을 분석하여 역할을 분류하는 함수입니다."""

    system_message = """  
    당신은 사용자 유형을 분류하는 매우 정확한 라우터입니다. 사용자의 입력을 보고 'student', 'professor', 'unknown' 중 하나로 분류해주세요.

    ## 분류 기준:
    1. 'student': 반, 이름, 학번 등 개인정보를 포함하여 퀴즈 응시를 시도하는 경우.
    2. 'professor': 날짜, 반, '리포트' 또는 '성적'과 같은 키워드를 포함하여 결과를 조회하려는 경우.
    3. 'unknown': 위 두 경우에 해당하지 않는 모든 애매한 경우.

    ## 예시:
    - 입력: "1반 홍길동 S25B001 010-1111-2222", 분류: 'student'
    - 입력: "2025-07-07 2반 성적 순위 리포트 좀 보여줘", 분류: 'professor'
    - 입력: "안녕하세요", 분류: 'unknown'
    - 입력: "퀴즈를 풀고 싶어요.", 분류: 'unknown'

    ## 출력 형식:
    JSON {{"role": "student|professor|unknown"}} 한 값만 주세요.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message.strip()),
        ("human", "{input_text}")
    ])
    try:
        response = (prompt | llm_with_role_route).invoke({"input_text": text})
        return response.role
    except Exception:
        return "unknown"

def entry_router(state: AppState) -> str:
    """역할 분류 및 진입점 라우터"""

    ui = state.get("user_input", "").strip()

    # 1) 퀴즈 시작 명령 우선
    if any(cmd == ui for cmd in settings.QUIZ_COMMANDS):
        return "quiz_entry"

    # 2) 문제 진행 중이면 답변 입력으로 라우팅
    qs = state.get("questions", [])
    qi = state.get("quiz_index", 0)
    if qs and (0 <= qi < len(qs)):
        return "answer_entry"

    # 3) 역할 분류
    role = classify_role(ui) if ui else "unknown"
    if role == "student":
        return "student_entry"
    elif role == "professor":
        return "professor_entry"
    else:
        return "unknown_entry"

def entry_helper(state: AppState) -> AppState:
    """알 수 없는 역할에 대한 도움말"""
    
    help_text = (
        "학생은 `1반 홍길동 S25B101 010-1111-1001` 처럼 본인 정보를 입력하세요.\n"
        "교수는 `2025-07-07 2반 리포트 출력`처럼 날짜와 반을 포함해 입력하세요.\n"
        "퀴즈를 시작하려면 `퀴즈 시작`이라고 입력하세요."
    )
    return {"chat_history": [("assistant", help_text)]}
