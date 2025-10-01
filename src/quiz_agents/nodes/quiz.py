from langchain_core.prompts import ChatPromptTemplate
from quiz_agents.models import FinalReport
from quiz_agents.nodes.state import AppState
from quiz_agents.services.loaders import load_quizzes
from quiz_agents.services.llm import llm_with_final_report


def quiz_setter(state: AppState) -> AppState:
    """퀴즈 문항 설정"""
    questions = load_quizzes()
    if not questions:
        return {
            "chat_history": [(
                "assistant",
                "퀴즈를 불러오는 데 실패했거나 풀 수 있는 문제가 없습니다."
            )],
            "questions": [],
        }
    return {
        "questions": questions,
        "quiz_index": 0,
        "user_answers": [],
        "final_report": None,
        "chat_history": [(
            "assistant",
            f"퀴즈를 시작합니다. 총 {len(questions)}문항입니다."
        )],
    }

def continue_quiz_condition(state: AppState) -> str:
    """퀴즈 계속/채점 분기 키 일치"""
    questions = state.get("questions", [])
    quiz_index = state.get("quiz_index", 0)
    if quiz_index < len(questions):
        return "continue_quiz"
    else:
        return "grade_quiz"

def quiz_popper(state: AppState) -> AppState:
    """현재 문제 출력"""
    quiz_index = state["quiz_index"]
    quiz = state["questions"][quiz_index]
    text = f"문제 {quiz_index + 1}: {quiz['question']}"
    if quiz["type"] == "multiple_choice":
        choices = [f"{i + 1}. {c}" for i, c in enumerate(quiz["choices"])]
        text += "\n" + "\n".join(choices)
    return {"chat_history": [("assistant", text)]}

def answer_collector(state: AppState) -> AppState:
    """답변 수집 및 다음 인덱스"""
    quiz_index = state.get("quiz_index", 0)
    quiz = state.get("questions", [])[quiz_index]
    user_input = state.get("user_input", "").strip()
    user_answers = state.get("user_answers", [])

    if not user_input:
        return {"chat_history": [("assistant", "답변을 입력해 주세요.")]}
    processed_answer = user_input
    if quiz["type"] == "multiple_choice":
        try:
            sel = int(user_input) - 1
            if 0 <= sel < len(quiz["choices"]):
                processed_answer = quiz["choices"][sel]
        except (ValueError, IndexError):
            pass

    user_answers.append(processed_answer)
    return {"user_answers": user_answers, "quiz_index": quiz_index + 1}

def grading_prompter(state: AppState) -> AppState:
    """채점 프롬프트 생성"""
    questions = state.get("questions", [])
    user_answers = state.get("user_answers", [])

    prompt_buff = ["지금부터 아래의 문제와 정답, 그리고 사용자의 답변을 보고 채점을 시작해주세요."]
    for i, (q, a) in enumerate(zip(questions, user_answers)):
        prompt_buff.append(f"\n--- 문제 {i + 1} ---")
        prompt_buff.append(f"문제: {q['question']}")
        if q["type"] == "multiple_choice":
            prompt_buff.append(f"선택지: {', '.join(q['choices'])}")
        prompt_buff.append(f"정답: {q['answer']}")
        prompt_buff.append(f"사용자 답변: {a}")

    return {
        "chat_history": [("assistant", "채점을 진행합니다...")],
        "grading_prompt": "\n".join(prompt_buff),
    }

def grade_reporter(state: AppState) -> AppState:
    """LLM 채점 → FinalReport 파싱"""
    system_message = """
    당신은 '명탐정 코난' 퀴즈의 전문 채점관입니다. 주어진 문제, 정답, 사용자 답변을 바탕으로 채점해주세요. 
    각 문제에 대해 정답 여부를 판단하고 친절한 해설을 덧붙여주세요. 
    모든 채점이 끝나면, 마지막에는 '총점: X/Y' 형식으로 최종 점수를 반드시 요약해서 보여줘야 합니다. 
    반드시 지정된 JSON 형식으로만 답변해야 합니다.
    """
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_message), ("human", "{grading_data}")]
    )
    try:
        chain = prompt | llm_with_final_report
        report = chain.invoke({"grading_data": state["grading_prompt"]})
        return {"final_report": report}
    except Exception as e:
        print(f"채점 중 오류 발생: {e}")
        error_report = FinalReport(results=[], total_score="채점 오류가 발생했습니다.")
        return {"final_report": error_report}

def report_formatter(state: AppState) -> AppState:
    """FinalReport → 사람이 읽을 수 있는 텍스트"""
    final_report = state["final_report"]
    report_buff = ["채점이 완료되었습니다! 🎉\n"]
    if final_report and final_report.results:
        for i, res in enumerate(final_report.results):
            is_correct_text = "✅ 정답" if res.is_correct else "❌ 오답"
            report_buff.append(f"--- 문제 {i + 1} ---")
            report_buff.append(f"문제: {res.question}")
            report_buff.append(f"정답: {res.correct_answer}")
            report_buff.append(f"제출한 답변: {res.user_answer}")
            report_buff.append(f"결과: {is_correct_text}")
            report_buff.append(f"해설: {res.explanation}\n")
        report_buff.append(f"**{final_report.total_score}**")
    else:
        report_buff.append("채점 결과를 생성하는 데 실패했습니다.")
    report_buff.append("\n퀴즈를 다시 시작하려면 '퀴즈 시작'이라고 입력해주세요.")
    return {"chat_history": [("assistant", "\n".join(report_buff))]}

