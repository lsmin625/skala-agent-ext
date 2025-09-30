import sqlite3
import json
from datetime import datetime
from quiz_agents.config import settings
from quiz_agents.models import FinalReport, ApplicantInfo, ReportRequest

def ensure_db():
    """데이터베이스 및 테이블 생성"""

    connection = sqlite3.connect(settings.DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
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
    )""")
    connection.commit()
    connection.close()

def save_report(applicant: ApplicantInfo, final_report: FinalReport):
    """퀴즈 결과 저장"""

    correct = sum(1 for r in final_report.results if r.is_correct)
    total = len(final_report.results)
    details = [r.model_dump() for r in final_report.results]

    connection = sqlite3.connect(settings.DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
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
    connection.commit()
    connection.close()
    return correct, total

def fetch_quiz_results(report_request: ReportRequest):
    """퀴즈 결과 조회"""

    taken_date = (report_request.taken_date or "").replace("/", "-").replace(".", "-")
    student_class = report_request.student_class or ""

    connection = sqlite3.connect(settings.DB_FILE)
    cursor = connection.cursor()
    sql = "SELECT student_name, student_id, student_class, total_score, total_count, details_json, taken_at FROM quiz_results WHERE 1=1"
    params = []
    if taken_date:
        sql += " AND taken_at LIKE ?"
        params.append(f"{taken_date}%")
    if student_class:
        sql += " AND student_class = ?"
        params.append(student_class)

    cursor.execute(sql + " ORDER BY total_score DESC, taken_at ASC", params)
    rows = cursor.fetchall()
    cursor.close()
    return rows

def fetch_quiz_applicant_taken(applicant: ApplicantInfo) -> dict | None:
    """응시자의 퀴즈 결과 조회"""

    # 이미 응시했는지 확인
    connection = sqlite3.connect(settings.DB_FILE)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT taken_at,total_score FROM quiz_results WHERE student_id=? ORDER BY id DESC LIMIT 1",
        (applicant.student_id,),  # 단일 파라미터 튜플!
    )
    row = cursor.fetchone()
    connection.close()
    if row:
        taken_at, total_score = row
        return {"taken_at": taken_at, "total_score": total_score}
    return None

ensure_db()