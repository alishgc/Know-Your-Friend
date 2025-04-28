# Know Your Friend

[![Python](https://img.shields.io/badge/python-3.x-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Know Your Friend** is a web-based application that lets users test how well they know their friends. It uses a database to store quiz questions and answers, offering an interactive experience. The app is built using Python for the backend and HTML/CSS for the frontend.

## Features
- **Web-based interface** for user-friendly interaction
- **Database** to store quiz questions and responses
- Dynamic scoring system to evaluate how well you know your friend
- Expandable with more questions, friends, and features

## How It Works
1. The app retrieves quiz questions from a database.
2. You answer multiple-choice questions.
3. After completion, the app calculates your score and provides feedback.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/alishgc/Know-Your-Friend.git
   ```

2. **Install dependencies** (in `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup the database**:  
   Ensure your database (e.g., SQLite, MySQL) is properly configured as specified in your app’s code.

4. **Run the app**:
   ```bash
   python app.py
   ```

## Project Structure
```
Know-Your-Friend/
│
├── app.py            # Main script to run the web app
├── static/           # Contains CSS and JS files
├── templates/        # Contains HTML templates
├── instance/         # Database scripts (e.g., SQL)
├── requirements.txt  # Project dependencies
├── README.md         # Project documentation
└── LICENSE           # License file
```

## Requirements
- Python 3.x
- Database (e.g., SQLite, MySQL)
- Required Python libraries (listed in `requirements.txt`)

## License

This project is licensed under the [MIT License](LICENSE).

## Future Improvements
- Add a feature to challenge multiple friends simultaneously
- Improve UI/UX with a modern front-end framework
- Implement personalized feedback based on quiz results