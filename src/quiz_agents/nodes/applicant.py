from langchain_core.prompts import ChatPromptTemplate
from quiz_agents.models import ApplicantInfo
from quiz_agents.nodes.state import AppState
from quiz_agents.services.loaders import load_applicants
from quiz_agents.services.llm import llm_with_applicant_info
from quiz_agents.services.db import fetch_quiz_applicant_taken


def parse_applicant_info(text: str) -> ApplicantInfo | None:
    """사용자 입력에서 지원자 정보를 추출"""

    system_message = """  
    아래 문장에서 반(student_class), 이름(student_name), 학번(student_id), 전화번호(student_phone)을 추출하세요.
    - 반: 숫자와 '반'이 포함된 문자열 (예: '1반', '2반') 
    - 이름: 한글로 된 이름
    - 학번: 'S'로 시작하는 영문자와 숫자의 조합    
    - 전화번호: 하이픈(-)이 포함될 수 있는 8개 이상의 숫자 형식

    ## 예시:
    - 입력: "1반 홍길동 S25B001 010-1111-2222"
    - 출력: JSON {{"student_class": "1반", "student_name": "홍길동", "student_id": "S25B001", "student_phone": "010-1111-2222"}}
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message.strip()),
        ("human", "{input_text}")
    ])

    try:
        response = (prompt | llm_with_applicant_info).invoke({"input_text": text})
        if not response.student_name or not response.student_id:
            return None
        return response
    except Exception:
        return None

def applicant_validator(state: AppState) -> AppState:
    """응시자 정보 검증 & 중복 응시 확인"""
    user_input = state.get("user_input", "")
    applicant = parse_applicant_info(user_input)
    if not applicant:
        return {"chat_history": [("assistant", "응시자 정보를 인식하지 못했습니다. 예) 1반 홍길동 S25B101 010-1111-1001")]}

    try:
        roster = load_applicants()
    except Exception:
        roster = []

    exists = next((r for r in roster if r.get("student_id") == applicant.student_id), None)
    if not exists:
        return {"chat_history": [("assistant", f"등록된 응시자가 없습니다: {applicant.student_id}")]}

    row = fetch_quiz_applicant_taken(applicant)
    if row:
        return {"chat_history": [("assistant", f"이미 응시 기록이 있습니다. 응시일자: {row['taken_at']}, 점수: {row['total_score']}")]}

    return {
        "applicant": applicant,
        "chat_history": [("assistant", f"{applicant.student_class} {applicant.student_name}님, '퀴즈 시작'이라고 입력하세요.")]
    }
