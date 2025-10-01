import sqlite3
import json
from contextlib import closing
from datetime import datetime

from quiz_agents.config import settings
from quiz_agents.models import FinalReport, ApplicantInfo, ReportRequest


def ensure_db():
    """데이터베이스 및 테이블 생성"""
    with closing(sqlite3.connect(settings.DB_FILE)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                taken_at TEXT NOT NULL,
                student_class TEXT,
                student_name TEXT,
                student_id TEXT,
                student_phone TEXT,
                total_score INTEGER,
                total_count INTEGER,
                details_json TEXT
            )
        """)
        conn.commit()


def save_report(applicant: ApplicantInfo, final_report: FinalReport):
    """퀴즈 결과 저장"""
    correct = sum(1 for r in final_report.results if r.is_correct)
    total = len(final_report.results)
    details = [r.model_dump() for r in final_report.results]

    with closing(sqlite3.connect(settings.DB_FILE)) as conn:
        conn.execute("""
            INSERT INTO quiz_results (
                taken_at, student_class, student_name, student_id, student_phone,
                total_score, total_count, details_json
            ) VALUES (?,?,?,?,?,?,?,?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            applicant.student_class,
            applicant.student_name,
            applicant.student_id,
            applicant.student_phone,
            correct, total, json.dumps(details, ensure_ascii=False)
        ))
        conn.commit()

    return correct, total


def fetch_quiz_results(report_request: ReportRequest):
    """퀴즈 결과 조회"""
    taken_date = (report_request.taken_date or "").replace("/", "-").replace(".", "-")
    student_class = report_request.student_class or ""

    sql = """
        SELECT
            student_name, student_id, student_class,
            total_score, total_count, details_json, taken_at
        FROM quiz_results
        WHERE 1=1
    """
    params: list[str] = []

    if taken_date:
        sql += " AND taken_at LIKE ?"
        params.append(f"{taken_date}%")
    if student_class:
        sql += " AND student_class = ?"
        params.append(student_class)

    sql += " ORDER BY total_score DESC, taken_at ASC"

    with closing(sqlite3.connect(settings.DB_FILE)) as conn:
        rows = conn.execute(sql, params).fetchall()

    return rows


def fetch_quiz_applicant_taken(applicant: ApplicantInfo) -> dict | None:
    """응시자의 최근 퀴즈 결과 1건 조회 (있으면 taken_at/total_score 반환)"""
    query = """
        SELECT taken_at, total_score
        FROM quiz_results
        WHERE student_id = ?
        ORDER BY id DESC
        LIMIT 1
    """
    with closing(sqlite3.connect(settings.DB_FILE)) as conn:
        row = conn.execute(query, (applicant.student_id,)).fetchone()

    if row:
        taken_at, total_score = row
        return {"taken_at": taken_at, "total_score": total_score}
    return None


# 최초 실행 시 테이블 보장
ensure_db()
