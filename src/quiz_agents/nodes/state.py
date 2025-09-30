from typing import Literal, TypedDict, Annotated
from quiz_agents.models import ApplicantInfo, FinalReport, ReportRequest

def reduce_list(left: list, right: list) -> list:
    """두 리스트를 합칩니다."""
    return left + right

# 애플리케이션 상태 모델 정의
# 모든 필드를 선택적(total=False)으로 관리 => 상태 관리에 적합한 방식
class AppState(TypedDict, total=False):
    """
    애플리케이션의 전체 상태를 관리하는 중앙 저장소.
    Annotated를 사용하여 각 필드에 대한 설명을 타입 힌트에 포함합니다.
    """
    
    # --- 공통 및 초기 필드 ---
    user_input: Annotated[str, "사용자의 현재 입력값"]
    chat_history: Annotated[list[tuple[str, str]], "UI용 대화 기록 리스트", reduce_list]
    role: Annotated[Literal["student", "professor", "unknown"], "현재 사용자의 역할"]

    # --- 응시자(student) 흐름 관련 필드 ---
    applicant: Annotated[ApplicantInfo, "응시자 정보"]
    questions: Annotated[list[dict], "생성된 퀴즈 질문 목록"]
    quiz_index: Annotated[int, "현재 진행 중인 퀴즈의 인덱스"]
    user_answers: Annotated[list[str], "사용자가 제출한 답변 목록", reduce_list]
    grading_prompt: Annotated[str, "채점을 위해 LLM에 전달할 프롬프트"]
    final_report: Annotated[FinalReport, "최종 채점 결과 보고서"]

    # --- 교수(professor) 리포트 흐름 관련 필드 ---
    report_request: Annotated[ReportRequest, "교수가 요청한 리포트 상세 정보"]