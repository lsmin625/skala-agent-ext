from langgraph.graph import StateGraph, END
from quiz_agents.nodes.state import AppState
from quiz_agents.nodes.routing import entry_router, entry_helper
from quiz_agents.nodes.applicant import applicant_validator
from quiz_agents.nodes.quiz import (
    quiz_setter, quiz_popper, answer_collector,
    continue_quiz_condition, grading_prompter, grade_reporter, report_formatter
)
from quiz_agents.nodes.report import grade_report_saver, report_request_parser, report_generater

def build_graph():
    graph = StateGraph(AppState)

    # 노드 추가
    graph.add_node("entry_helper", entry_helper)
    graph.add_node("applicant_validator", applicant_validator)
    graph.add_node("quiz_setter", quiz_setter)
    graph.add_node("quiz_popper", quiz_popper)
    graph.add_node("answer_collector", answer_collector)
    graph.add_node("grading_prompter", grading_prompter)
    graph.add_node("grade_reporter", grade_reporter)
    graph.add_node("grade_report_saver", grade_report_saver)
    graph.add_node("report_formatter", report_formatter)
    graph.add_node("report_request_parser", report_request_parser)
    graph.add_node("report_generater", report_generater)

    # 조건부 엔트리
    graph.set_conditional_entry_point(
        entry_router,
        {
            "quiz_entry": "quiz_setter",
            "answer_entry": "answer_collector",
            "student_entry": "applicant_validator",
            "professor_entry": "report_request_parser",
            "unknown_entry": "entry_helper",
        },
    )

    # 엣지
    graph.add_edge("quiz_setter", "quiz_popper")
    graph.add_edge("quiz_popper", END)  # 문제 출력 후 턴 종료
    graph.add_edge("entry_helper", END)

    graph.add_conditional_edges(
        "answer_collector",
        continue_quiz_condition,
        {"continue_quiz": "quiz_popper", "grade_quiz": "grading_prompter"},
    )
    graph.add_edge("grading_prompter", "grade_reporter")
    graph.add_edge("grade_reporter", "grade_report_saver")
    graph.add_edge("grade_report_saver", "report_formatter")
    graph.add_edge("report_request_parser", "report_generater")
    graph.add_edge("report_formatter", END)
    graph.add_edge("report_generater", END)

    return graph.compile()
