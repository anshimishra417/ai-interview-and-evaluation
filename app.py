from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, random

app = Flask(__name__)
app.secret_key = "secret"


# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS records (
        username TEXT, question TEXT, answer TEXT, score TEXT, feedback TEXT
    )''')
    conn.commit()
    conn.close()

init_db()


# ---------- QUESTIONS ----------
# Dict format: {question_text: [keywords]}  — enables instant keyword lookup by question
theory = {
    "easy": {
        "What is DBMS?":  ["database", "data", "management", "system"],
        "What is OS?":    ["operating system", "hardware", "software", "process"],
        "What is CPU?":   ["processor", "execution", "instructions"]
    },
    "medium": {
        "Explain ACID properties": ["atomicity", "consistency", "isolation", "durability"],
        "What is normalization?":  ["redundancy", "tables", "normal form"],
        "What is indexing?":       ["search", "speed", "database"]
    },
    "hard": {
        "Explain CAP theorem": ["consistency", "availability", "partition"],
        "Explain deadlock":    ["process", "waiting", "resource"],
        "Explain sharding":    ["partition", "database", "scaling"]
    }
}

coding = {
    "Amazon": [
        ("Two Sum",        "Find two numbers that add to target"),
        ("Sliding Window", "Find max sum subarray")
    ],
    "Google": [
        ("Longest Substring", "Without repeating characters"),
        ("Merge Intervals",   "Merge overlapping intervals")
    ],
    "TCS": [
        ("Palindrome", "Check if string is palindrome"),
        ("Factorial",  "Find factorial using loop")
    ]
}


# ---------- EVALUATION ----------
def evaluate(question, keywords, answer):
    if not answer or not answer.strip():
        return 0, "No answer was provided. Please speak or type your answer.", "Poor"

    answer_lower = answer.strip().lower()

    if len(answer_lower) < 5:
        return 1, "Answer too short. Please elaborate on the topic.", "Poor"

    # Keyword matching
    matched     = [k for k in keywords if k.lower() in answer_lower]
    match_count = len(matched)
    score       = int((match_count / len(keywords)) * 10)

    # Bonus for detailed answer
    word_count = len(answer_lower.split())
    if word_count > 20:
        score += 1
    if word_count > 50:
        score += 1

    score = min(score, 10)

    missing = [k for k in keywords if k.lower() not in answer_lower]

    if score >= 8:
        remark   = "Excellent"
        feedback = (
            f"Great answer! You covered {match_count}/{len(keywords)} key concepts. "
            "Strong understanding demonstrated."
        )
    elif score >= 6:
        remark   = "Good"
        feedback = (
            f"Good answer. You covered {match_count}/{len(keywords)} concepts. "
            + (f"Try to also mention: {', '.join(missing[:2])}." if missing else "Add more detail.")
        )
    elif score >= 4:
        remark   = "Needs Improvement"
        feedback = (
            f"You covered {match_count}/{len(keywords)} concepts. "
            f"Key topics missing: {', '.join(missing)}. Elaborate more."
        )
    else:
        remark   = "Poor"
        feedback = (
            f"Only {match_count}/{len(keywords)} concepts matched. "
            f"Please study: {', '.join(missing)}."
        )

    return score, feedback, remark


# ---------- AUTH ----------
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = c.fetchone()
        conn.close()
        if user:
            session.clear()
            session['user'] = u
            return redirect('/dashboard')
        error = "Invalid username or password."
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?,?)", (u, p))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html', username=session['user'])


# ---------- LEVEL SELECTION ----------
@app.route('/select_level', methods=['GET', 'POST'])
def select_level():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        session['level']            = request.form.get('level', 'easy')
        session['asked_questions']  = []
        return redirect('/voice')
    return render_template('level.html')


# ---------- VOICE / THEORY INTERVIEW ----------
@app.route('/voice', methods=['GET', 'POST'])
def voice():
    if 'user' not in session:
        return redirect('/')

    level      = session.get('level', 'easy')
    level_pool = theory.get(level, theory['easy'])   # {question: keywords}

    # -------- SUBMIT ANSWER (AJAX POST) --------
    if request.method == 'POST':
        ans    = request.form.get('answer', '').strip()
        q_text = request.form.get('question', '').strip()

        # Direct dict lookup — guaranteed to work if question text matches exactly
        keywords = level_pool.get(q_text)

        if not keywords:
            return jsonify({
                "score":    0,
                "feedback": f"Question not recognized: '{q_text}'. Please refresh and try again.",
                "remark":   "Error"
            })

        score, feedback, remark = evaluate(q_text, keywords, ans)

        try:
            conn = sqlite3.connect('database.db')
            c    = conn.cursor()
            c.execute(
                "INSERT INTO records VALUES (?,?,?,?,?)",
                (session['user'], q_text, ans, str(score), remark + " — " + feedback)
            )
            conn.commit()
            conn.close()
        except Exception as db_err:
            print("DB ERROR:", db_err)

        return jsonify({
            "score":    score,
            "feedback": feedback,
            "remark":   remark
        })

    # -------- SERVE NEXT QUESTION (GET) --------
    all_questions = list(level_pool.keys())
    asked         = session.get('asked_questions', [])
    remaining     = [q for q in all_questions if q not in asked]

    if not remaining:
        asked     = []
        remaining = all_questions

    q_text = random.choice(remaining)
    session['asked_questions'] = asked + [q_text]   # reassign to force Flask session update

    return render_template('voice.html', question=q_text)


# ---------- COMPANY SELECTION ----------
@app.route('/coding', methods=['GET', 'POST'])
def coding_page():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        session['company'] = request.form.get('company', 'Amazon')
        return redirect('/coding_question')
    return render_template('company.html')


# ---------- CODING INTERVIEW ----------
@app.route('/coding_question', methods=['GET', 'POST'])
def coding_q():
    if 'user' not in session:
        return redirect('/')

    company = session.get('company', 'Amazon')
    q, desc = random.choice(coding[company])

    if request.method == 'POST':
        ans   = request.form.get('answer', '').strip()
        words = len(ans.split())

        score = min(words // 5, 8)
        code_keywords = ['def ', 'for ', 'while ', 'if ', 'return', 'int ', 'var ', '{', '[']
        if any(kw in ans for kw in code_keywords):
            score = min(score + 2, 10)

        if score >= 8:
            remark = "Excellent"
        elif score >= 5:
            remark = "Good"
        else:
            remark = "Needs Improvement"

        feedback = (
            f"{remark} attempt. "
            "Consider handling edge cases, optimizing time complexity, "
            "and using clean variable names."
        )

        try:
            conn = sqlite3.connect('database.db')
            c    = conn.cursor()
            c.execute(
                "INSERT INTO records VALUES (?,?,?,?,?)",
                (session['user'], f"{q} ({company})", ans, str(score), feedback)
            )
            conn.commit()
            conn.close()
        except Exception as db_err:
            print("DB ERROR:", db_err)

        return render_template('coding_result.html', question=q, score=score, feedback=feedback)

    return render_template('coding.html', q=q, desc=desc, company=company)


# ---------- RECORDS ----------
@app.route('/records')
def records():
    if 'user' not in session:
        return redirect('/')
    conn = sqlite3.connect('database.db')
    c    = conn.cursor()
    c.execute("SELECT * FROM records WHERE username=?", (session['user'],))
    data = c.fetchall()
    conn.close()
    return render_template('records.html', data=data)


# ---------- PERFORMANCE GRAPH ----------
@app.route('/graph')
def graph():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    c    = conn.cursor()
    c.execute("SELECT score FROM records WHERE username=?", (session['user'],))
    rows = c.fetchall()
    conn.close()

    scores = []
    for row in rows:
        try:
            scores.append(int(row[0]))
        except (ValueError, TypeError):
            scores.append(0)

    if not scores:
        scores = [0]

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 4))
    plt.plot(scores, marker='o', color='#4f46e5', linewidth=2, markersize=6)
    plt.fill_between(range(len(scores)), scores, alpha=0.15, color='#4f46e5')
    plt.title(f"Performance — {session['user']}", fontsize=14)
    plt.xlabel("Attempt #")
    plt.ylabel("Score (out of 10)")
    plt.ylim(0, 10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("static/graph.png")
    plt.close()

    return render_template('graph.html')


# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)