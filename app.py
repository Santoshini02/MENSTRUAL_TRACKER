from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import hashlib
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'menstrual_tracker_secret_key_2024'

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tracker.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            age INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            symptoms TEXT,
            mood TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def compute_stats(cycles):
    if not cycles:
        return {'last_period': 'N/A', 'next_period': 'N/A', 'avg_cycle': 'N/A', 'count': 0}
    def val(c, key):
        return c[key] if isinstance(c, dict) else c[key]
    start_dates = [val(c, 'start_date') for c in cycles if val(c, 'start_date')]
    if not start_dates:
        return {'last_period': 'N/A', 'next_period': 'N/A', 'avg_cycle': 'N/A', 'count': len(cycles)}
    dates = sorted([datetime.strptime(d, '%Y-%m-%d') for d in start_dates])
    last = dates[-1]
    avg = 28
    if len(dates) >= 2:
        gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]
        avg = round(sum(gaps) / len(gaps))
    next_p = last + timedelta(days=avg)
    return {
        'last_period': last.strftime('%d %b %Y'),
        'next_period': next_p.strftime('%d %b %Y'),
        'avg_cycle':   avg,
        'count':       len(cycles)
    }

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if not email or not password:
            error = 'Please fill in all fields.'
        else:
            conn = get_db()
            user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
            conn.close()
            if user and user['password'] == hash_password(password):
                session['user_id']  = user['id']
                session['username'] = user['username']
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid email or password.'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        age      = request.form.get('age', '')
        if not username or not email or not password:
            error = 'Please fill in all required fields.'
        else:
            try:
                conn = get_db()
                conn.execute(
                    'INSERT INTO users (username, email, password, age) VALUES (?,?,?,?)',
                    (username, email, hash_password(password), age or None)
                )
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = 'Email or username already exists.'
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    uid    = session['user_id']
    conn   = get_db()
    cycles = conn.execute('SELECT * FROM cycles WHERE user_id=? ORDER BY start_date DESC', (uid,)).fetchall()
    conn.close()
    stats = compute_stats(cycles)
    return render_template('dashboard.html', username=session['username'], stats=stats, cycles=cycles[:5])

@app.route('/add_cycle', methods=['POST'])
@login_required
def add_cycle():
    uid      = session['user_id']
    start    = request.form.get('start_date')
    end      = request.form.get('end_date')
    symptoms = request.form.get('symptoms', '')
    mood     = request.form.get('mood', '')
    notes    = request.form.get('notes', '')
    if start:
        conn = get_db()
        conn.execute(
            'INSERT INTO cycles (user_id, start_date, end_date, symptoms, mood, notes) VALUES (?,?,?,?,?,?)',
            (uid, start, end or None, symptoms, mood, notes)
        )
        conn.commit()
        conn.close()
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/delete_cycle/<int:cid>')
@login_required
def delete_cycle(cid):
    uid  = session['user_id']
    conn = get_db()
    conn.execute('DELETE FROM cycles WHERE id=? AND user_id=?', (cid, uid))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/edit_cycle/<int:cid>', methods=['GET', 'POST'])
@login_required
def edit_cycle(cid):
    uid   = session['user_id']
    conn  = get_db()
    cycle = conn.execute('SELECT * FROM cycles WHERE id=? AND user_id=?', (cid, uid)).fetchone()
    if not cycle:
        conn.close()
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        start    = request.form.get('start_date')
        end      = request.form.get('end_date')
        symptoms = request.form.get('symptoms', '')
        mood     = request.form.get('mood', '')
        notes    = request.form.get('notes', '')
        conn.execute(
            'UPDATE cycles SET start_date=?, end_date=?, symptoms=?, mood=?, notes=? WHERE id=? AND user_id=?',
            (start, end or None, symptoms, mood, notes, cid, uid)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    conn.close()
    return render_template('edit_cycle.html', cycle=cycle)

@app.route('/api/cycles')
@login_required
def api_cycles():
    uid    = session['user_id']
    conn   = get_db()
    cycles = conn.execute('SELECT * FROM cycles WHERE user_id=? ORDER BY start_date', (uid,)).fetchall()
    conn.close()
    return jsonify([dict(c) for c in cycles])

@app.route('/api/trends')
@login_required
def api_trends():
    uid    = session['user_id']
    conn   = get_db()
    cycles = conn.execute('SELECT * FROM cycles WHERE user_id=? ORDER BY start_date', (uid,)).fetchall()
    conn.close()
    cycles = [dict(c) for c in cycles]

    dates = sorted([datetime.strptime(c['start_date'], '%Y-%m-%d') for c in cycles])
    cycle_lengths, labels = [], []
    for i in range(1, len(dates)):
        cycle_lengths.append((dates[i] - dates[i-1]).days)
        labels.append(dates[i].strftime('%b %Y'))

    sym_count, mood_count = {}, {}
    for c in cycles:
        if c['symptoms']:
            for s in c['symptoms'].split(','):
                s = s.strip().lower()
                if s:
                    sym_count[s] = sym_count.get(s, 0) + 1
        if c['mood']:
            m = c['mood'].strip()
            mood_count[m] = mood_count.get(m, 0) + 1

    avg       = round(sum(cycle_lengths) / len(cycle_lengths)) if cycle_lengths else 28
    irregular = [l for l in cycle_lengths if l > 35 or l < 21]

    return jsonify({
        'cycle_lengths':   cycle_lengths,
        'labels':          labels,
        'avg_cycle':       avg,
        'sym_count':       sym_count,
        'mood_count':      mood_count,
        'irregular_count': len(irregular),
        'total_cycles':    len(cycles)
    })

@app.route('/api/ai_insights')
@login_required
def api_ai_insights():
    uid    = session['user_id']
    conn   = get_db()
    cycles = conn.execute('SELECT * FROM cycles WHERE user_id=? ORDER BY start_date', (uid,)).fetchall()
    conn.close()
    cycles = [dict(c) for c in cycles]

    if len(cycles) < 2:
        return jsonify({
            'regularity':    'Not enough data',
            'avg_cycle':     'N/A',
            'next_period':   'N/A',
            'fertile_start': 'N/A',
            'fertile_end':   'N/A',
            'insights':      ['Log at least 2 cycles to get AI insights.'],
            'suggestions':   ['Start tracking your cycle to get personalized insights.']
        })

    dates   = sorted([datetime.strptime(c['start_date'], '%Y-%m-%d') for c in cycles])
    lengths = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]
    avg     = round(sum(lengths) / len(lengths))
    std     = (sum((l - avg) ** 2 for l in lengths) / len(lengths)) ** 0.5

    last          = dates[-1]
    next_p        = last + timedelta(days=avg)
    fertile_start = next_p - timedelta(days=18)
    fertile_end   = next_p - timedelta(days=11)

    regularity = 'Very Regular' if std < 3 else ('Moderately Regular' if std < 6 else 'Irregular')

    insights = [
        f"Your average cycle length is {avg} days.",
        f"Cycle regularity: {regularity} (variation: +/-{round(std, 1)} days).",
        f"Next predicted period: {next_p.strftime('%d %b %Y')}.",
        f"Estimated fertile window: {fertile_start.strftime('%d %b')} to {fertile_end.strftime('%d %b %Y')}."
    ]

    suggestions = []
    if avg < 21:
        suggestions.append("Your cycles are shorter than average. Consider consulting a gynaecologist.")
    elif avg > 35:
        suggestions.append("Your cycles are longer than average. This may indicate hormonal imbalances.")
    else:
        suggestions.append("Your cycle length is within the normal range (21-35 days).")

    if std >= 6:
        suggestions.append("Irregular cycles detected. Stress, diet, or hormonal factors may be involved.")
    else:
        suggestions.append("Your cycle is fairly regular. Keep tracking for better insights.")

    all_symptoms = []
    for c in cycles:
        if c['symptoms']:
            all_symptoms.extend([s.strip().lower() for s in c['symptoms'].split(',')])
    if 'cramps' in all_symptoms or 'cramping' in all_symptoms:
        suggestions.append("Frequent cramps noted. Light exercise and hydration can help.")
    if 'headache' in all_symptoms or 'headaches' in all_symptoms:
        suggestions.append("Headaches during your cycle may be hormone-related.")

    return jsonify({
        'regularity':    regularity,
        'avg_cycle':     avg,
        'next_period':   next_p.strftime('%d %b %Y'),
        'fertile_start': fertile_start.strftime('%d %b %Y'),
        'fertile_end':   fertile_end.strftime('%d %b %Y'),
        'insights':      insights,
        'suggestions':   suggestions
    })

@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html', username=session['username'])

@app.route('/trends')
@login_required
def trends():
    return render_template('trends.html', username=session['username'])

@app.route('/symptoms')
@login_required
def symptoms():
    uid    = session['user_id']
    conn   = get_db()
    cycles = conn.execute('SELECT * FROM cycles WHERE user_id=? ORDER BY start_date DESC', (uid,)).fetchall()
    conn.close()
    return render_template('symptoms.html', username=session['username'], cycles=cycles)

@app.route('/health')
@login_required
def health():
    return render_template('health.html', username=session['username'])

@app.route('/ai')
@login_required
def ai():
    return render_template('ai.html', username=session['username'])

@app.route('/profile')
@login_required
def profile():
    uid    = session['user_id']
    conn   = get_db()
    user   = conn.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
    cycles = conn.execute('SELECT * FROM cycles WHERE user_id=? ORDER BY start_date DESC', (uid,)).fetchall()
    conn.close()
    # Convert user Row to dict safely; if not found, use session data
    if user is not None:
        user = dict(user)
    else:
        user = {'username': session.get('username', 'User'), 'email': '', 'age': None, 'created_at': ''}
    stats = compute_stats(cycles)
    return render_template('profile.html', username=session['username'], user=user, stats=stats)

@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot():
    msg = request.json.get('message', '').lower()
    responses = {
        'cycle':     "A typical menstrual cycle is 21-35 days. Yours will be shown in your AI insights.",
        'period':    "Periods usually last 3-7 days. Track your end date for accurate analysis.",
        'pain':      "Mild cramps are normal. Try heat therapy, hydration, and light exercise. If severe, consult a doctor.",
        'cramp':     "Heat pads, ibuprofen, and gentle yoga can help with cramps during your period.",
        'fertile':   "Your fertile window is typically 10-14 days before your next period.",
        'irregular': "Irregular cycles can be caused by stress, diet, or hormones. Track consistently and consult a doctor if needed.",
        'pms':       "PMS symptoms include mood swings, bloating, and fatigue. These are normal 1-2 weeks before your period.",
          'mood':      "Hormonal changes affect mood throughout your cycle. Tracking moods helps identify patterns.",
        'headache':  "Hormonal headaches are common before/during periods. Stay hydrated and note the pattern.",
        'predict':   "Your next period is predicted using your average cycle length. Log more cycles for better accuracy.",
        'hello':     "Hello! I am your AI cycle guide. Ask me about your cycle, symptoms, or health tips!",
        'hi':        "Hi there! How can I help you with your menstrual health today?",
        'help':      "I can answer questions about: cycle length, symptoms, cramps, fertile window, PMS, mood, and predictions.",
    }
    for key, response in responses.items():
        if key in msg:
            return jsonify({'reply': response})
    return jsonify({'reply': "I am not sure about that. Try asking about cycle length, symptoms, cramps, fertility, or predictions!"})
init_db()

if __name__ == '__main__':
    app.run(debug=True)