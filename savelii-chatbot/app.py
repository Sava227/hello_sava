from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import time
import random
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
BAN_FILE = "banned_users.txt"
MUTE_FILE = "muted_users.txt"
BAD_WORDS_FILE = "bad_words.txt"
BAN_DURATION = 10 * 60
MUTE_DURATION = 5 * 60

# Database setup
def init_db():
    conn = sqlite3.connect("learned_responses.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS learned_responses (
        question TEXT PRIMARY KEY,
        answer TEXT,
        keyword TEXT
    )
    ''')
    conn.commit()
    conn.close()

# User data
users = {
    "sava123": {"role": "admin", "password": "admin123"},
    "daniel.d": {"role": "admin", "password": "admin123"},
    "salman": {"role": "admin", "password": "admin123"},
    "sava321": {"role": "moderator", "password": "admin123"},
    "salman123": {"role": "moderator", "password": "admin123"},
    "user1": {"role": "user", "password": "userpass"}
}

# Helper functions
def load_bans():
    bans = {}
    if os.path.exists(BAN_FILE):
        with open(BAN_FILE, "r") as f:
            for line in f:
                if line.strip():
                    user, ts = line.strip().split(",")
                    bans[user] = float(ts)
    return bans

def save_bans(bans):
    with open(BAN_FILE, "w") as f:
        for user, ts in bans.items():
            f.write("{},{}\n".format(user, ts))

def load_mutes():
    mutes = {}
    if os.path.exists(MUTE_FILE):
        with open(MUTE_FILE, "r") as f:
            for line in f:
                if line.strip():
                    user, ts = line.strip().split(",")
                    mutes[user] = float(ts)
    return mutes

def save_mutes(mutes):
    with open(MUTE_FILE, "w") as f:
        for user, ts in mutes.items():
            f.write("{},{}\n".format(user, ts))

def load_bad_words():
    if os.path.exists(BAD_WORDS_FILE):
        with open(BAD_WORDS_FILE, "r") as f:
            return [word.strip().lower() for word in f.readlines()]
    else:
        return ["bastard", "damn", "hell", "shit", "fuck", "bitch", "ass", "god damn", "goddamn", "dumass"]

def save_bad_words(words):
    with open(BAD_WORDS_FILE, "w") as f:
        for w in words:
            f.write(w + "\n")

def is_banned(name):
    bans = load_bans()
    now = time.time()
    if name in bans:
        if now < bans[name]:
            return True, int((bans[name] - now) // 60) + 1
        else:
            del bans[name]
            save_bans(bans)
    return False, 0

def is_muted(name):
    mutes = load_mutes()
    now = time.time()
    if name in mutes:
        if now < mutes[name]:
            return True, int((mutes[name] - now) // 60) + 1
        else:
            del mutes[name]
            save_mutes(mutes)
    return False, 0

def chat_history_file(username):
    return "chat_history_{}.txt".format(username)

def append_chat_history(username, message):
    with open(chat_history_file(username), "a", encoding="utf-8") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write("[{}] {}\n".format(timestamp, message))

def read_chat_history(username):
    filename = chat_history_file(username)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    return "(No chat history found for this user.)"

def load_learned_responses():
    responses = {}
    conn = sqlite3.connect("learned_responses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer, keyword FROM learned_responses")
    rows = cursor.fetchall()
    for question, answer, keyword in rows:
        responses[question] = {"answer": answer, "keyword": keyword}
    conn.close()
    return responses

def save_learned_responses(responses):
    conn = sqlite3.connect("learned_responses.db")
    cursor = conn.cursor()
    for question, data in responses.items():
        cursor.execute("INSERT OR REPLACE INTO learned_responses (question, answer, keyword) VALUES (?, ?, ?)",
                       (question, data['answer'], data['keyword']))
    conn.commit()
    conn.close()

def find_response(msg, learned_responses, chatbot_responses):
    msg_lower = msg.lower()
    if msg_lower in learned_responses:
        return learned_responses[msg_lower]['answer']
    for q, data in learned_responses.items():
        if data['keyword'].lower() in msg_lower:
            return data['answer']
    for word in msg_lower.split():
        if word in chatbot_responses:
            return chatbot_responses[word]
    return None

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            flash('Admin access required')
            return redirect(url_for('chat'))
        return f(*args, **kwargs)
    return decorated_function

def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') not in ['admin', 'moderator']:
            flash('Moderator access required')
            return redirect(url_for('chat'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form.get('password', '').strip()
        
        if username in users:
            user_data = users[username]
            if user_data["role"] in ["admin", "moderator"]:
                if user_data["password"] == password:
                    session['username'] = username
                    session['role'] = user_data["role"]
                else:
                    flash('Incorrect password. Logging in as regular user.')
                    session['username'] = username
                    session['role'] = "user"
            else:
                session['username'] = username
                session['role'] = user_data["role"]
        else:
            session['username'] = username
            session['role'] = "user"
        
        # Check if user is banned
        banned, ban_mins = is_banned(username)
        if banned:
            flash('You are banned for another {} minutes.'.format(ban_mins))
            session.clear()
            return render_template('login.html')
        
        append_chat_history(username, "User {} logged in with role {}.".format(username, session['role']))
        return redirect(url_for('chat'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/chat')
@login_required
def chat():
    username = session['username']
    banned, ban_mins = is_banned(username)
    if banned:
        flash('You are banned for another {} minutes.'.format(ban_mins))
        return redirect(url_for('logout'))
    
    muted, mute_mins = is_muted(username)
    history = read_chat_history(username)
    
    return render_template('chat.html', 
                         username=username, 
                         role=session['role'],
                         muted=muted,
                         mute_mins=mute_mins,
                         history=history)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    username = session['username']
    message = request.json.get('message', '').strip()
    
    # Check ban/mute status
    banned, ban_mins = is_banned(username)
    if banned:
        return jsonify({'error': 'You are banned for another {} minutes.'.format(ban_mins)})
    
    muted, mute_mins = is_muted(username)
    if muted:
        return jsonify({'error': 'You are muted for another {} minutes.'.format(mute_mins)})
    
    # Check for bad words
    bad_words = load_bad_words()
    if any(bw in message.lower() for bw in bad_words):
        bans = load_bans()
        bans[username] = time.time() + BAN_DURATION
        save_bans(bans)
        return jsonify({'error': 'You used inappropriate language and have been banned for 10 minutes.'})
    
    # Process message
    chatbot_responses = {
        "hello": "Hello! How can I assist you today?",
        "hi": "Hi there! What can I do for you?",
        "how are you": "I'm a bot, so I'm always good. Thanks for asking!",
        "what's your name": "My name is Sava, your friendly chatbot.",
        "help": "You can chat with me or play games. Try typing 'wordle' to play!",
        "bye": "Goodbye! Have a great day!",
        "thank you": "You're welcome!"
    }
    
    learned_responses = load_learned_responses()
    response = find_response(message, learned_responses, chatbot_responses)
    
    if response:
        append_chat_history(username, "User: {}".format(message))
        append_chat_history(username, "Sava: {}".format(response))
        return jsonify({'response': response})
    else:
        append_chat_history(username, "User: {}".format(message))
        return jsonify({'response': None, 'learn': True})

@app.route('/learn_response', methods=['POST'])
@login_required
def learn_response():
    data = request.json
    question = data.get('question', '').strip().lower()
    answer = data.get('answer', '').strip()
    keyword = data.get('keyword', '').strip().lower()
    
    learned_responses = load_learned_responses()
    learned_responses[question] = {"answer": answer, "keyword": keyword}
    save_learned_responses(learned_responses)
    
    append_chat_history(session['username'], "Sava learned: {} -> {}".format(question, answer))
    return jsonify({'success': True})

@app.route('/wordle')
@login_required
def wordle():
    word_list = [
        "apple", "grape", "table", "chair", "plant", "brick", "smile", "light", "spine", "plane", "beach", "ducat",
        "youth", "books", "couch", "tried", "stone", "pride", "level", "jelly", "mango", "grind", "shine", "piano",
        "grain", "eagle", "candy", "lemon", "zebra", "spoon", "glass", "brush", "sugar", "bliss", "storm", "flame"
    ]
    target = random.choice(word_list)
    session['wordle_word'] = target
    session['wordle_attempts'] = 6
    return render_template('wordle.html')

@app.route('/wordle_guess', methods=['POST'])
@login_required
def wordle_guess():
    guess = request.json.get('guess', '').lower()
    target = session.get('wordle_word', '')
    attempts = session.get('wordle_attempts', 0)
    
    if len(guess) != 5 or not guess.isalpha():
        return jsonify({'error': 'Please enter a valid 5-letter word.'})
    
    if guess == target:
        session.pop('wordle_word', None)
        session.pop('wordle_attempts', None)
        return jsonify({'success': True, 'message': 'Congratulations! You guessed the word!'})
    
    feedback = []
    for i in range(5):
        if guess[i] == target[i]:
            feedback.append('correct')
        elif guess[i] in target:
            feedback.append('present')
        else:
            feedback.append('absent')
    
    attempts -= 1
    session['wordle_attempts'] = attempts
    
    if attempts == 0:
        session.pop('wordle_word', None)
        session.pop('wordle_attempts', None)
        return jsonify({'game_over': True, 'word': target})
    
    return jsonify({'feedback': feedback, 'attempts': attempts})

@app.route('/admin')
@admin_required
def admin():
    now = time.time()
    bans = load_bans()
    mutes = load_mutes()
    bad_words = load_bad_words()
    learned_responses = load_learned_responses()
    
    # Format bans and mutes with remaining time
    formatted_bans = {}
    for user, timestamp in bans.items():
        if timestamp > now:
            formatted_bans[user] = int((timestamp - now) // 60) + 1
    
    formatted_mutes = {}
    for user, timestamp in mutes.items():
        if timestamp > now:
            formatted_mutes[user] = int((timestamp - now) // 60) + 1
    
    return render_template('admin.html', 
                         bans=formatted_bans, 
                         mutes=formatted_mutes, 
                         bad_words=bad_words,
                         learned_responses=learned_responses)

@app.route('/moderator')
@moderator_required
def moderator():
    now = time.time()
    bans = load_bans()
    mutes = load_mutes()
    
    # Format bans and mutes with remaining time
    formatted_bans = {}
    for user, timestamp in bans.items():
        if timestamp > now:
            formatted_bans[user] = int((timestamp - now) // 60) + 1
    
    formatted_mutes = {}
    for user, timestamp in mutes.items():
        if timestamp > now:
            formatted_mutes[user] = int((timestamp - now) // 60) + 1
    
    return render_template('moderator.html', bans=formatted_bans, mutes=formatted_mutes)

@app.route('/admin/unban', methods=['POST'])
@admin_required
def admin_unban():
    username = request.form['username']
    bans = load_bans()
    if username in bans:
        del bans[username]
        save_bans(bans)
        flash('{} has been unbanned.'.format(username))
    else:
        flash('User is not banned.')
    return redirect(url_for('admin'))

@app.route('/admin/unmute', methods=['POST'])
@admin_required
def admin_unmute():
    username = request.form['username']
    mutes = load_mutes()
    if username in mutes:
        del mutes[username]
        save_mutes(mutes)
        flash('{} has been unmuted.'.format(username))
    else:
        flash('User is not muted.')
    return redirect(url_for('admin'))

@app.route('/admin/mute', methods=['POST'])
@admin_required
def admin_mute():
    username = request.form['username']
    duration = int(request.form.get('duration', 5))
    mutes = load_mutes()
    mutes[username] = time.time() + duration * 60
    save_mutes(mutes)
    flash('{} has been muted for {} minutes.'.format(username, duration))
    return redirect(url_for('admin'))

@app.route('/admin/update_bad_words', methods=['POST'])
@admin_required
def update_bad_words():
    words = request.form['words'].split(',')
    clean_words = [w.strip().lower() for w in words if w.strip()]
    save_bad_words(clean_words)
    flash('Bad words list updated.')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001) 