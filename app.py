import random
from flask import request, session, redirect, url_for, flash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_type = request.form.get('login_type', 'regular')
        
        if login_type == 'guest':
            # Generate a random guest username
            guest_number = random.randint(1000, 9999)
            username = f"Guest_{guest_number}"
            session['username'] = username
            session['role'] = "guest"
            append_chat_history(username, f"Guest user {username} logged in.")
            return redirect(url_for('chat'))
        
        # Regular login
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