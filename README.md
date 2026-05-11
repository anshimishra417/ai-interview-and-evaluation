# AI Interview Preparation & Performance Evaluation System 🎯

A full-stack web application that simulates technical interviews, evaluates responses using NLP, and tracks performance over time — giving candidates a personal interview coach experience.

---

## What It Does

Users can practice both **theory** and **coding** interview questions, receive instant AI-based feedback on their answers, and track their improvement through a performance dashboard.

---

## Features

| Feature | Description |
|---|---|
| 🎤 Voice / Text Interview | Answer theory questions by speaking or typing |
| 🧠 NLP-Based Evaluation | Keyword matching + scoring engine evaluates answer quality |
| 💻 Coding Interview Mode | Company-specific coding questions (Amazon, Google, TCS) |
| 📊 Performance Graph | Visual score history plotted with Matplotlib |
| 🏢 Company Selection | Practice questions tailored to specific companies |
| 📁 Interview Records | Full history of all attempts with scores and feedback |
| 🔐 User Auth | Register/login system with session management |
| 📈 Difficulty Levels | Easy, Medium, Hard theory question tracks |

---

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** SQLite (`database.db`, `interviews.db`)
- **NLP / Evaluation:** Keyword-based scoring with TF-IDF logic
- **Data Visualization:** Matplotlib (performance graph)
- **Auth:** Flask sessions

---

## Project Structure

```
ai-interview-and-evaluation/
├── app.py                  # Main Flask app — all routes and logic
├── database.db             # User auth + interview records
├── interviews.db           # Interview session data
├── static/
│   ├── graph.png           # Generated performance graph
│   └── ...                 # CSS, JS assets
├── templates/
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── dashboard.html      # Main dashboard
│   ├── level.html          # Difficulty selection
│   ├── voice.html          # Theory interview (voice/text)
│   ├── company.html        # Company selection for coding round
│   ├── coding.html         # Coding question page
│   ├── coding_result.html  # Coding result + feedback
│   ├── records.html        # Past interview records
│   └── graph.html          # Performance graph view
```

---

## How It Works

### Theory Interview Flow

```
User selects difficulty (Easy / Medium / Hard)
        ↓
Random question served from question bank
        ↓
User answers via text or voice input
        ↓
NLP Evaluator matches keywords in answer
        ↓
Score (0-10) + detailed feedback generated
        ↓
Result saved to SQLite database
```

### Scoring Logic

The evaluation engine:
- Extracts keywords from the user's answer
- Matches against expected concept keywords for that question
- Calculates a base score: `(matched / total_keywords) × 10`
- Awards bonus points for detailed answers (word count > 20, > 50)
- Generates specific feedback listing missing concepts

**Remark bands:**
| Score | Remark |
|---|---|
| 8–10 | Excellent |
| 6–7 | Good |
| 4–5 | Needs Improvement |
| 0–3 | Poor |

### Sample Questions Covered

**Theory Topics:** DBMS, OS, CPU, ACID properties, Normalization, Indexing, CAP Theorem, Deadlock, Sharding

**Coding Topics:**
- Amazon: Two Sum, Sliding Window
- Google: Longest Substring, Merge Intervals
- TCS: Palindrome, Factorial

---

## Getting Started

### Requirements

```
Python 3.x
Flask
Matplotlib
```

### Installation

```bash
git clone https://github.com/anshimishra417/ai-interview-and-evaluation.git
cd ai-interview-and-evaluation
pip install flask matplotlib
```

### Run

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

### Usage

1. Register a new account
2. Login and go to the Dashboard
3. Choose **Theory Interview** → select difficulty → answer questions
4. Choose **Coding Interview** → select company → solve coding problems
5. View your **Records** and **Performance Graph** to track progress

---

## Screenshots

> *(Add screenshots of dashboard, interview screen, and performance graph here)*

---

## Future Improvements

- [ ] Add more companies and question categories
- [ ] Integrate actual speech-to-text (Web Speech API)
- [ ] Use cosine similarity / TF-IDF for smarter answer evaluation
- [ ] Deploy on Render or Railway for public access
- [ ] Add timer for each question to simulate real interview pressure

---

## Author

**Anshi Mishra**
B.Tech Computer Science — Graphic Era Hill University
[LinkedIn](https://www.linkedin.com/in/anshi-mishra-0718682b5/) • [GitHub] (https://github.com/anshimishra417)

---

## License

MIT License — free to use, modify, and build upon.
