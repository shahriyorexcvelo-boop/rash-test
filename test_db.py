"""
Test Tekshirish Tizimi — SQLite Database moduli
"""
import sqlite3
import json
import time
from typing import Optional, List, Dict, Any

DB_FILE = os.getenv("DB_PATH", "test_system.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Foydalanuvchilar jadvali
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE NOT NULL,
        fullname TEXT NOT NULL,
        phone TEXT NOT NULL,
        username TEXT,
        status TEXT DEFAULT 'pending',
        registered_at INTEGER NOT NULL
    )
    """)
    
    # Mavjud jadvalga status ustunini xavfsiz qo'shish (agar yo'q bo'lsa)
    try:
        cur.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'approved'")
    except Exception:
        pass

    # 2. Testlar jadvali
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        subject TEXT DEFAULT 'Matematika',
        pdf_file_id TEXT,
        pdf_file_name TEXT,
        answers_json TEXT NOT NULL,
        total_questions INTEGER DEFAULT 45,
        time_limit_min INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        key_access_code TEXT,
        created_at INTEGER NOT NULL
    )
    """)

    # Eski DB uchun key_access_code ustunini qo'shish (agar yo'q bo'lsa)
    try:
        cur.execute("ALTER TABLE tests ADD COLUMN key_access_code TEXT")
    except sqlite3.OperationalError:
        pass  # Ustun allaqachon mavjud

    # 3. Natijalar / Submissions jadvali
    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER NOT NULL,
        test_code TEXT NOT NULL,
        user_tg_id INTEGER NOT NULL,
        fullname TEXT NOT NULL,
        phone TEXT NOT NULL,
        answers_json TEXT NOT NULL,
        score REAL NOT NULL,
        max_score REAL DEFAULT 100.0,
        correct_count INTEGER NOT NULL,
        total_count INTEGER DEFAULT 45,
        details_json TEXT NOT NULL,
        submitted_at INTEGER NOT NULL,
        FOREIGN KEY(test_id) REFERENCES tests(id)
    )
    """)

    # 4. Adminlar jadvali
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        tg_id INTEGER PRIMARY KEY,
        fullname TEXT,
        username TEXT,
        added_by INTEGER,
        created_at INTEGER NOT NULL
    )
    """)
    # Bosh adminni kiritib qo'yish
    cur.execute("""
    INSERT OR IGNORE INTO admins (tg_id, fullname, username, added_by, created_at)
    VALUES (8039427064, 'Bosh Admin', 'admin', 0, 1789300000)
    """)

    conn.commit()
    conn.close()

# ----------------- USERS & ACCESS -----------------
def add_or_update_user(tg_id: int, fullname: str, phone: str, username: Optional[str] = None, status: str = "pending") -> bool:
    conn = get_connection()
    cur = conn.cursor()
    now = int(time.time())
    try:
        cur.execute("""
        INSERT INTO users (tg_id, fullname, phone, username, status, registered_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(tg_id) DO UPDATE SET
            fullname=excluded.fullname,
            phone=excluded.phone,
            username=excluded.username,
            status=CASE WHEN users.status = 'approved' THEN 'approved' ELSE excluded.status END
        """, (tg_id, fullname, phone, username, status, now))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False
    finally:
        conn.close()

def get_user(tg_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def is_user_approved(tg_id: int, admin_id: int = 8039427064) -> bool:
    """Foydalanuvchiga botdan foydalanish ruxsati berilganligini tekshirish."""
    if is_admin(tg_id, admin_id):
        return True
    user = get_user(tg_id)
    if not user:
        return False
    return user.get("status") == "approved"

def approve_user(tg_id: int) -> bool:
    """Foydalanuvchiga botdan foydalanish huquqini berish."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET status = 'approved' WHERE tg_id = ?", (tg_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error approving user: {e}")
        return False
    finally:
        conn.close()

def reject_user(tg_id: int) -> bool:
    """Foydalanuvchi so'rovini rad etish."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET status = 'rejected' WHERE tg_id = ?", (tg_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error rejecting user: {e}")
        return False
    finally:
        conn.close()

def block_user(tg_id: int) -> bool:
    """Foydalanuvchini botdan chiqarib yuborish (bloklash / huquqini bekor qilish)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET status = 'blocked' WHERE tg_id = ?", (tg_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error blocking user: {e}")
        return False
    finally:
        conn.close()

def delete_user(tg_id: int) -> bool:
    """Foydalanuvchini butunlay bazadan o'chirish."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM submissions WHERE user_tg_id = ?", (tg_id,))
        cur.execute("DELETE FROM users WHERE tg_id = ?", (tg_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        conn.close()

def get_users_count() -> Dict[str, int]:
    """Foydalanuvchilar soni statistikasini qaytaradi."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM users")
    total = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) as approved FROM users WHERE status = 'approved'")
    approved = cur.fetchone()["approved"]
    cur.execute("SELECT COUNT(*) as pending FROM users WHERE status = 'pending'")
    pending = cur.fetchone()["pending"]
    cur.execute("SELECT COUNT(*) as blocked FROM users WHERE status = 'blocked'")
    blocked = cur.fetchone()["blocked"]
    conn.close()
    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "blocked": blocked
    }

# ----------------- TESTS -----------------
def create_test(test_code: str, title: str, subject: str, answers: Dict[str, Any],
                pdf_file_id: Optional[str] = None, pdf_file_name: Optional[str] = None,
                time_limit_min: int = 0, key_access_code: str = "") -> bool:
    conn = get_connection()
    cur = conn.cursor()
    now = int(time.time())
    try:
        cur.execute("""
        INSERT INTO tests (test_code, title, subject, pdf_file_id, pdf_file_name, answers_json, total_questions, time_limit_min, is_active, key_access_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        ON CONFLICT(test_code) DO UPDATE SET
            title=excluded.title,
            subject=excluded.subject,
            pdf_file_id=COALESCE(excluded.pdf_file_id, tests.pdf_file_id),
            pdf_file_name=COALESCE(excluded.pdf_file_name, tests.pdf_file_name),
            answers_json=excluded.answers_json,
            time_limit_min=excluded.time_limit_min,
            key_access_code=excluded.key_access_code,
            is_active=1
        """, (test_code, title, subject, pdf_file_id, pdf_file_name, json.dumps(answers, ensure_ascii=False), 45, time_limit_min, key_access_code, now))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating/updating test: {e}")
        return False
    finally:
        conn.close()

def update_test_pdf(test_id: int, pdf_file_id: str, pdf_file_name: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE tests SET pdf_file_id = ?, pdf_file_name = ? WHERE id = ?", (pdf_file_id, pdf_file_name, test_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating test pdf: {e}")
        return False
    finally:
        conn.close()

def get_active_tests() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tests WHERE is_active = 1 ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_test_by_code(test_code: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tests WHERE test_code = ?", (test_code,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_test_by_id(test_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tests WHERE id = ?", (test_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

get_test = get_test_by_id

def get_all_tests() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tests ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def toggle_test_status(test_id: int) -> Optional[int]:
    """Test holatini faol (1) yoki to'xtatilgan (0) ga almashtiradi."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT is_active FROM tests WHERE id = ?", (test_id,))
        row = cur.fetchone()
        if not row:
            return None
        new_status = 0 if row["is_active"] == 1 else 1
        cur.execute("UPDATE tests SET is_active = ? WHERE id = ?", (new_status, test_id))
        conn.commit()
        return new_status
    except Exception as e:
        print(f"Error toggling test: {e}")
        return None
    finally:
        conn.close()

def update_test_time_limit(test_id: int, time_limit_min: int) -> bool:
    """Test vaqt chegarasini yangilash (daqiqa). 0 bo'lsa cheksiz."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE tests SET time_limit_min = ? WHERE id = ?", (time_limit_min, test_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating test time limit: {e}")
        return False
    finally:
        conn.close()

def delete_test(test_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM submissions WHERE test_id = ?", (test_id,))
        cur.execute("DELETE FROM tests WHERE id = ?", (test_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

# ----------------- ADMINS & USERS -----------------
def is_admin(tg_id: int, super_admin_id: int = 8039427064) -> bool:
    if tg_id == super_admin_id:
        return True
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT tg_id FROM admins WHERE tg_id = ?", (tg_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row)

def add_admin(tg_id: int, fullname: str = "Admin", username: Optional[str] = None, added_by: int = 0) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    now = int(time.time())
    try:
        cur.execute("""
        INSERT INTO admins (tg_id, fullname, username, added_by, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(tg_id) DO UPDATE SET
            fullname=excluded.fullname,
            username=excluded.username
        """, (tg_id, fullname, username, added_by, now))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding admin: {e}")
        return False
    finally:
        conn.close()

def remove_admin(tg_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM admins WHERE tg_id = ?", (tg_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_all_admins() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admins ORDER BY created_at ASC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_users() -> List[Dict[str, Any]]:
    """Barcha ro'yxatdan o'tgan foydalanuvchilar va ularning yechgan testlar soni"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT u.*, COUNT(s.id) as tests_count, MAX(s.submitted_at) as last_test_at
    FROM users u
    LEFT JOIN submissions s ON u.tg_id = s.user_tg_id
    GROUP BY u.tg_id
    ORDER BY u.registered_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ----------------- SUBMISSIONS / RESULTS -----------------
def normalize_answer(ans: Any) -> str:
    """Ochiq va yopiq javoblarni moslashtirish: har qanday belgi, son, ildiz, kasr, daraja va amallarni to'g'ri qabul qiladi."""
    if ans is None:
        return ""
    res = str(ans).strip().lower()
    res = res.replace(" ", "")
    res = res.replace(",", ".")
    res = res.replace("·", "*").replace("×", "*")
    res = res.replace("²", "^2").replace("³", "^3")
    res = res.replace("sqrt", "√")
    return res

def parse_numeric_or_fraction(val: str) -> Optional[float]:
    try:
        if "/" in val:
            parts = val.split("/")
            if len(parts) == 2:
                num = float(parts[0])
                den = float(parts[1])
                if den != 0:
                    return num / den
        return float(val)
    except Exception:
        return None

def is_answer_matching(user_ans: Any, correct_ans: Any) -> bool:
    u = normalize_answer(user_ans)
    c = normalize_answer(correct_ans)
    if not u or not c:
        return False
    if u == c:
        return True
    
    num_u = parse_numeric_or_fraction(u)
    num_c = parse_numeric_or_fraction(c)
    if num_u is not None and num_c is not None:
        if abs(num_u - num_c) < 1e-5:
            return True
            
    return False

def get_user_submission_for_test(test_id: int, user_tg_id: int) -> Optional[Dict[str, Any]]:
    """Foydalanuvchi ushbu testni avval topshirganligini tekshirish."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM submissions WHERE test_id = ? AND user_tg_id = ?", (test_id, user_tg_id))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_key_and_score(q_data: Any, default_score: float) -> tuple[str, float]:
    """Kalit va savolga ajratilgan ballni ajratib oladi."""
    if isinstance(q_data, dict):
        ans = str(q_data.get("ans", q_data.get("answer", "")))
        try:
            score = float(q_data.get("score", q_data.get("ball", default_score)))
        except (ValueError, TypeError):
            score = default_score
        return ans, score
    else:
        return str(q_data or ""), default_score

def calculate_grade(score: float) -> str:
    """Test natijasi bali bo'yicha Milliy sertifikat darajasini aniqlash."""
    if score >= 70.0:
        return "A+"
    elif score >= 65.0:
        return "A"
    elif score >= 60.0:
        return "B+"
    elif score >= 55.0:
        return "B"
    elif score >= 50.0:
        return "C+"
    elif score >= 46.0:
        return "C"
    else:
        return "— (Yetarli emas)"

def check_and_save_submission(test_id: int, user_tg_id: int, user_answers: Dict[str, str]) -> Dict[str, Any]:
    test = get_test_by_id(test_id)
    if not test:
        raise ValueError("Test topilmadi!")

    # Qayta ishlash huquqini cheklash
    if user_tg_id:
        existing = get_user_submission_for_test(test_id, user_tg_id)
        if existing:
            raise ValueError("Siz ushbu testni allaqachon topshirgansiz! Qayta topshirish mumkin emas.")

    user = get_user(user_tg_id) if user_tg_id else None
    fullname = user["fullname"] if user else "Foydalanuvchi"
    phone = user["phone"] if user else "-"

    correct_answers_raw = json.loads(test["answers_json"])
    
    total_questions = 55
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    
    details = {}
    earned_score = 0.0
    total_possible_score = 0.0
    
    # 1. 1-32 savollar (4 ta variant: A, B, C, D — default 2.0 ball)
    for q in range(1, 33):
        key = str(q)
        q_raw = correct_answers_raw.get(key, "A")
        correct_ans, q_score = get_key_and_score(q_raw, default_score=2.0)
        total_possible_score += q_score

        user_val = user_answers.get(key, "")
        
        is_corr = False
        if not user_val or not str(user_val).strip():
            status = "unanswered"
            unanswered_count += 1
        elif is_answer_matching(user_val, correct_ans):
            is_corr = True
            status = "correct"
            correct_count += 1
            earned_score += q_score
        else:
            status = "incorrect"
            incorrect_count += 1
            
        details[key] = {
            "num": f"{q}-savol",
            "type": "choice_4",
            "user": user_val,
            "correct": correct_ans,
            "status": status,
            "score": q_score if is_corr else 0.0,
            "max_score": q_score
        }

    # 2. 33, 34, 35 savollar (6 ta variant: A, B, C, D, E, F — default 2.0 ball)
    for q in [33, 34, 35]:
        key = str(q)
        q_raw = correct_answers_raw.get(key, "A")
        correct_ans, q_score = get_key_and_score(q_raw, default_score=2.0)
        total_possible_score += q_score

        user_val = user_answers.get(key, "")
        
        is_corr = False
        if not user_val or not str(user_val).strip():
            status = "unanswered"
            unanswered_count += 1
        elif is_answer_matching(user_val, correct_ans):
            is_corr = True
            status = "correct"
            correct_count += 1
            earned_score += q_score
        else:
            status = "incorrect"
            incorrect_count += 1
            
        details[key] = {
            "num": f"{q}-savol",
            "type": "choice_6",
            "user": user_val,
            "correct": correct_ans,
            "status": status,
            "score": q_score if is_corr else 0.0,
            "max_score": q_score
        }

    # 3. 36a dan 45b gacha ochiq/yopiq savollar (20 ta savol — default 1.5 ball)
    for q in range(36, 46):
        for sub in ["a", "b"]:
            key = f"{q}{sub}"
            q_raw = correct_answers_raw.get(key, "1")
            correct_ans, q_score = get_key_and_score(q_raw, default_score=1.5)
            total_possible_score += q_score

            user_val = user_answers.get(key, "")
            
            is_corr = False
            if not user_val or not str(user_val).strip():
                status = "unanswered"
                unanswered_count += 1
            elif is_answer_matching(user_val, correct_ans):
                is_corr = True
                status = "correct"
                correct_count += 1
                earned_score += q_score
            else:
                status = "incorrect"
                incorrect_count += 1
                
            details[key] = {
                "num": f"{key}-savol",
                "type": "open",
                "user": user_val,
                "correct": correct_ans,
                "status": status,
                "score": q_score if is_corr else 0.0,
                "max_score": q_score
            }

    earned_score = round(earned_score, 1)
    total_possible_score = round(total_possible_score, 1) or 100.0
    percentage = round((earned_score / total_possible_score) * 100, 1)
    grade = calculate_grade(earned_score)

    now = int(time.time())
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO submissions (
        test_id, test_code, user_tg_id, fullname, phone,
        answers_json, score, max_score, correct_count, total_count,
        details_json, submitted_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        test["id"], test["test_code"], user_tg_id, fullname, phone,
        json.dumps(user_answers, ensure_ascii=False), earned_score, total_possible_score,
        correct_count, 55,
        json.dumps(details, ensure_ascii=False), now
    ))
    submission_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        "submission_id": submission_id,
        "test_title": test["title"],
        "test_code": test["test_code"],
        "fullname": fullname,
        "score": earned_score,
        "max_score": total_possible_score,
        "percentage": percentage,
        "grade": grade,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "unanswered_count": unanswered_count,
        "details": details,
        "submitted_at": now
    }

def get_user_submissions(user_tg_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT s.*, t.title as test_title FROM submissions s
    JOIN tests t ON s.test_id = t.id
    WHERE s.user_tg_id = ? ORDER BY s.id DESC
    """, (user_tg_id,))
    rows = cur.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d["grade"] = calculate_grade(d.get("score", 0))
        results.append(d)
    return results

def get_test_results_leaderboard(test_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT fullname, phone, score, correct_count, submitted_at
    FROM submissions WHERE test_id = ? ORDER BY score DESC, submitted_at ASC
    """, (test_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_tests_with_stats() -> List[Dict[str, Any]]:
    """Admin uchun barcha testlar va ularni necha kishi ishlagani statistikasi."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT t.*, COUNT(s.id) as submissions_count, COALESCE(AVG(s.score), 0) as avg_score, COALESCE(MAX(s.score), 0) as max_score_achieved
    FROM tests t
    LEFT JOIN submissions s ON t.id = s.test_id
    GROUP BY t.id
    ORDER BY t.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def generate_test_results_pdf(test_id: int) -> Optional[str]:
    """Test natijalari bo'yicha rasmiy PDF reyting jadvali generatsiya qiladi."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        import os

        test = get_test_by_id(test_id)
        if not test:
            return None

        results = get_test_results_leaderboard(test_id)
        
        pdf_filename = f"test_result_{test_id}_{int(time.time())}.pdf"
        pdf_path = os.path.join(os.path.dirname(__file__), pdf_filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            leftMargin=30,
            rightMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#1E3A8A"),
            alignment=1
        )
        
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569"),
            alignment=1
        )

        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=11
        )

        cell_bold = ParagraphStyle(
            'CellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11
        )

        elements = []
        elements.append(Paragraph("BUXORIYLAR MAKTABI — BM RASH TEST", title_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"Test: <b>{test['title']}</b> | Fan: {test.get('subject', 'Matematika')}", subtitle_style))
        elements.append(Paragraph(f"Jami ishtirokchilar soni: <b>{len(results)} nafar</b> | Sana: {time.strftime('%d.%m.%Y %H:%M')}", subtitle_style))
        elements.append(Spacer(1, 14))

        # Jadval ma'lumotlari
        table_data = [
            [
                Paragraph("<b>O'rin</b>", cell_bold),
                Paragraph("<b>Ism va Familiya</b>", cell_bold),
                Paragraph("<b>Telefon</b>", cell_bold),
                Paragraph("<b>To'plangan Ball</b>", cell_bold),
                Paragraph("<b>Daraja</b>", cell_bold),
                Paragraph("<b>To'g'ri</b>", cell_bold),
                Paragraph("<b>Vaqt</b>", cell_bold)
            ]
        ]

        for rank, r in enumerate(results, 1):
            dt = time.strftime("%d.%m %H:%M", time.localtime(r["submitted_at"]))
            grade = calculate_grade(r["score"])
            table_data.append([
                Paragraph(f"<b>#{rank}</b>", cell_bold),
                Paragraph(r["fullname"] or "Foydalanuvchi", cell_style),
                Paragraph(r["phone"] or "-", cell_style),
                Paragraph(f"<b>{r['score']} ball</b>", cell_bold),
                Paragraph(f"<b>{grade}</b>", cell_style),
                Paragraph(f"{r['correct_count']} ta", cell_style),
                Paragraph(dt, cell_style)
            ])

        col_widths = [35, 140, 85, 75, 70, 50, 75]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(t)
        doc.build(elements)
        return pdf_path
    except Exception as e:
        print(f"PDF Error: {e}")
        return None

# Baza inicializatsiyasi
init_db()
