# Sava Chatbot - Web Interface

A modern, interactive web-based chatbot built with Flask and Bootstrap. This chatbot features user authentication, role-based access control, learning capabilities, moderation tools, and built-in games.

## ✨ Features

- **Smart Conversations**: Chat with Sava and teach it new responses
- **Multi-language Greetings**: Support for Māori, Spanish, French, Hindi, Arabic, and Japanese
- **User Roles**: Admin, Moderator, and Regular User access levels
- **Moderation System**: Automatic bad word filtering, user banning, and muting
- **Built-in Wordle Game**: Interactive word guessing game
- **Chat History**: Persistent conversation logging
- **Learning System**: Users can teach the bot new responses
- **Modern UI**: Responsive design with Bootstrap 5

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Virtual environment (recommended)

### Installation

1. **Clone or download the project**
   ```bash
   cd savelii-chatbot
   ```

2. **Activate your virtual environment** (if not already active)
   ```bash
   # On macOS/Linux
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to: `http://localhost:5000`

## 👥 User Accounts

### Test Accounts

- **Admin Users:**
  - Username: `sava123` | Password: `admin123`
  - Username: `daniel.d` | Password: `admin123`
  - Username: `salman` | Password: `admin123`

- **Moderator Users:**
  - Username: `sava321` | Password: `admin123`
  - Username: `salman123` | Password: `admin123`

- **Regular Users:**
  - Any username without a password (leave password field empty)

## 🎯 How to Use

### For Regular Users

1. **Login** with any username (no password required for regular users)
2. **Chat** with Sava by typing messages
3. **Teach Sava** new responses when it doesn't understand something
4. **Play Wordle** game from the chat interface
5. **View your chat history** using the history button

### For Moderators

- Access the **Moderator Panel** from the navigation
- **View banned/muted users**
- **Unban or unmute users** as needed

### For Administrators

- Access the **Admin Panel** from the navigation
- **Manage all users** (ban, mute, unban, unmute)
- **Configure bad words filter**
- **View all learned responses**
- **Access full system controls**

## 🎮 Games

### Wordle

- Guess a 5-letter word in 6 tries
- Color-coded feedback:
  - 🟩 Green: Correct letter in correct position
  - 🟨 Yellow: Correct letter in wrong position
  - ⬜ Gray: Letter not in word

## 🔧 Configuration

### Moderation Settings

- **Ban Duration**: 10 minutes (configurable in `app.py`)
- **Mute Duration**: 5 minutes (configurable in `app.py`)
- **Bad Words**: Customizable through admin panel

### Database

- **SQLite** database for learned responses
- **Text files** for bans, mutes, and chat history
- Automatic database initialization on first run

## 🗂️ File Structure

```
savelii-chatbot/
├── app.py                 # Main Flask application
├── bot.py                 # Original command-line bot (reference)
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── login.html        # Login page
│   ├── chat.html         # Chat interface
│   ├── wordle.html       # Wordle game
│   ├── admin.html        # Admin panel
│   └── moderator.html    # Moderator panel
├── static/               # Static files
│   └── css/
│       └── style.css     # Custom styles
├── learned_responses.db  # SQLite database
└── venv/                 # Virtual environment
```

## 🛠️ Development

### Adding New Features

1. **New Routes**: Add to `app.py`
2. **New Templates**: Create in `templates/` directory
3. **Styling**: Modify `static/css/style.css`
4. **Bot Responses**: Update `chatbot_responses` dictionary in `app.py`

### Customization

- **Colors**: Modify CSS variables in `style.css`
- **Branding**: Update templates and navigation
- **Features**: Extend the Flask routes and templates

## 🔒 Security Notes

- Change the `secret_key` in `app.py` for production use
- Consider using environment variables for sensitive configuration
- The current setup is designed for local development and testing

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `app.py`: `app.run(port=5001)`

2. **Database errors**
   - Delete `learned_responses.db` to reset the database

3. **Permission errors**
   - Ensure you have write permissions in the project directory

### Support

If you encounter issues:
1. Check that all dependencies are installed
2. Verify Python version compatibility
3. Ensure the virtual environment is activated
4. Check console output for error messages

## 📝 License

This project is for educational and development purposes. Feel free to modify and extend as needed.

---

**Enjoy chatting with Sava! 🤖✨** 