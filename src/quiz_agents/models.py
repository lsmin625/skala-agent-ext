from typing import Literal, Optional
from pydantic import BaseModel, Field

class RoleRoute(BaseModel):
    """역할 기반 접근 제어를 위한 경로 모델입니다."""
    role: Literal["student", "professor", "unknown"]

class ApplicantInfo(BaseModel):
    """지원자 정보를 담는 클래스입니다."""
    student_class: str = Field(description="지원자의 학급")
    student_name: str = Field(description="지원자의 이름")
    student_id: str = Field(description="지원자의 학번")
    student_phone: str = Field(description="지원자의 전화번호")

class GradingResult(BaseModel):
    """단일 문제에 대한 채점 결과를 상세히 담는 클래스입니다."""
    question_id: int = Field(description="문제의 고유 ID")
    question: str = Field(description="채점 대상 문제")
    correct_answer: str = Field(description="문제의 정답")
    user_answer: str = Field(description="사용자가 제출한 답변")
    is_correct: bool = Field(description="정답 여부")
    explanation: str = Field(description="정답에 대한 친절한 해설")

class FinalReport(BaseModel):
    """퀴즈의 모든 채점 결과와 최종 점수를 종합한 최종 보고서 클래스입니다."""
    results: list[GradingResult] = Field(description="각 문제별 채점 결과 리스트")
    total_score: str = Field(description="'총점: X/Y' 형식의 최종 점수 요약")

class ReportRequest(BaseModel):
    """최종 보고서 생성을 위한 요청 모델입니다."""
    taken_date: Optional[str] = Field(None, description="YYYY-MM-DD 또는 YYYY.MM.DD")
    student_class: Optional[str] = Field(None, description="반 (예: '2반')")
    report_type: Literal["오답", "성적", "전체"] = "전체"
