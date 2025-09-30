import re, json
from quiz_agents.models import ReportRequest
from quiz_agents.nodes.state import AppState
from quiz_agents.services.db import save_report, fetch_quiz_results

def grade_report_saver(state: AppState) -> AppState:
    """채점 결과 DB 저장 (숫자 집계로 저장)"""
    applicant = state.get("applicant")
    final_report = state.get("final_report")
    if applicant and final_report and final_report.results:
        save_report(applicant, final_report)
        return {"chat_history": [("assistant", "채점 결과가 성공적으로 저장되었습니다.")]}
    else:
        return {"chat_history": [("assistant", "채점 결과를 저장하는 데 실패했습니다.")]}    

def report_request_parser(state: AppState) -> AppState:
    """리포트 요청 파싱"""
    user_input = state.get("user_input", "")
    date_match = re.search(r"(\d{4}[-/.]\d{2}[-/.]\d{2})", user_input)
    taken_date = date_match.group(1).replace(".", "-") if date_match else ""
    class_match = re.search(r"(\d+반)", user_input)
    student_class = class_match.group(1) if class_match else ""
    if "오답" in user_input:
        report_type = "오답"
    elif "성적" in user_input:
        report_type = "성적"
    else:
        report_type = "전체"
    report_request = ReportRequest(taken_date=taken_date, student_class=student_class, report_type=report_type)
    return {"report_request": report_request}

def _rank_table(rows: list) -> str:
    """성적 순위 테이블 생성"""
    parts = ["### 성적 순위 (높은 점수 우선)", "이름 | 학번 | 반 | 점수 | 일시", "---|---|---|---|---"]
    for s_name, s_id, s_class, t_score, t_count, _, taken_at in rows:
        parts.append(f"{s_name} | {s_id} | {s_class} | {t_score}/{t_count} | {taken_at}")
    return "\n".join(parts)

def _wrong_table(rows: list) -> str:
    """오답률 상위 문항 테이블 생성"""
    agg: dict[str, list[int]] = {}
    for *_, details_json, _ in rows:
        try:
            details = json.loads(details_json)
            for d in details:
                qid = f"{d.get('question_id', '?')}.{d.get('question', '')[:16]}"
                is_correct = d.get("is_correct", False)
                if qid not in agg:
                    agg[qid] = [0, 0]
                agg[qid][1] += 1
                if not is_correct:
                    agg[qid][0] += 1
        except Exception:
            continue
    items = []
    for qid, (wrong, total) in agg.items():
        rate = (wrong/total*100) if total else 0.0
        items.append({"qid": qid, "wrong": wrong, "total": total, "rate": rate})
    items.sort(key=lambda x: x["rate"], reverse=True)
    parts = ["\n### 오답률 상위 문항", "문항 | 오답수/응시수 | 오답률(%)", "---|---|---"]
    for it in items[:20]:
        parts.append(f"{it['qid']} | {it['wrong']}/{it['total']} | {it['rate']:.1f}")
    return "\n".join(parts)

def report_generater(state: AppState) -> AppState:
    """요청 조건에 맞는 리포트 생성"""
    report_request = state.get("report_request")
    if not report_request:
        return {"chat_history": [("assistant", "리포트 요청을 파싱하지 못했습니다.")]}
    quiz_results = fetch_quiz_results(report_request)
    if not quiz_results:
        return {"chat_history": [("assistant", "해당 조건의 응시 기록이 없습니다.")]}
    report_outputs = []
    report_type = report_request.report_type
    if report_type in ("성적", "전체"):
        report_outputs.append(_rank_table(quiz_results))
    if report_type in ("오답", "전체"):
        report_outputs.append(_wrong_table(quiz_results))
    final_report = "\n\n".join(report_outputs)
    return {"chat_history": [("assistant", final_report)]}
