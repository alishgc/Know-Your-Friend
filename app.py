from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # For flash messages

db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if user is not logged in

# Database Models
class AdminUser(UserMixin, db.Model):  # Inherit from UserMixin to integrate with Flask-Login
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # In a real app, hash the password

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")  # Cascade delete

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    correct = db.Column(db.String(1), nullable=False)  # A, B, C, or D

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        quiz = Quiz()
        db.session.add(quiz)
        db.session.commit()

        # Add questions
        questions = zip(
            request.form.getlist('q_text[]'),
            request.form.getlist('q_a[]'),
            request.form.getlist('q_b[]'),
            request.form.getlist('q_c[]'),
            request.form.getlist('q_d[]'),
            request.form.getlist('q_correct[]')
        )

        for q_text, a, b, c, d, correct in questions:
            question = Question(
                quiz_id=quiz.id,
                text=q_text,
                option_a=a,
                option_b=b,
                option_c=c,
                option_d=d,
                correct=correct
            )
            db.session.add(question)

        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('share_quiz', quiz_id=quiz.id))

    return render_template('create.html')

@app.route('/quiz/<int:quiz_id>/<int:question_index>', methods=['GET', 'POST'])
def take_quiz(quiz_id, question_index):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    total_questions = len(questions)

    score = int(request.args.get('score', 0))

    if question_index >= total_questions:
        return redirect(url_for('result', quiz_id=quiz_id, score=score))

    question = questions[question_index]

    if request.method == 'POST':
        selected = request.form.get('q_answer')
        if selected == question.correct:
            score += 1
        return redirect(url_for('take_quiz', quiz_id=quiz_id, question_index=question_index + 1, score=score))

    return render_template('quiz.html',
                           question=question,
                           question_index=question_index,
                           total_questions=total_questions)

@app.route('/result/<int:quiz_id>/<int:score>')
def result(quiz_id, score):
    quiz = Quiz.query.get_or_404(quiz_id)
    total_questions = len(quiz.questions)

    messages = [
        "You're a mind reader!",
        "You know your friend so well!",
        "Not bad at all!",
        "You need to hang out more!",
        "Well... better luck next time!"
    ]

    if score == total_questions:
        msg = messages[0]
    elif score >= total_questions * 0.75:
        msg = messages[1]
    elif score >= total_questions * 0.5:
        msg = messages[2]
    elif score >= 1:
        msg = messages[3]
    else:
        msg = messages[4]

    return render_template('result.html', score=score, total=total_questions, message=msg)

@app.route('/share/<int:quiz_id>', methods=['GET', 'POST'])
def share_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    share_link = url_for('take_quiz', quiz_id=quiz.id, question_index=0, _external=True)
    return render_template('share_quiz.html', quiz_id=quiz.id, share_link=share_link)

# Admin Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = AdminUser.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    quizzes = Quiz.query.all()
    return render_template('admin/admin.html', quizzes=quizzes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = AdminUser.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
        else:
            new_user = AdminUser(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/admin/quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('admin/view_quiz.html', quiz=quiz)

# Admin - Manage Quizzes
@app.route('/admin/manage_quizzes')
@login_required
def manage_quizzes():
    quizzes = Quiz.query.all()  # Fetch quizzes from database directly
    return render_template('admin/manage_quizzes.html', quizzes=quizzes)

@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)  # Fetch quiz by ID
    if quiz:
        try:
            db.session.delete(quiz)  # Delete quiz (cascade delete for related questions)
            db.session.commit()  # Commit changes to the database
            flash('Quiz deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            flash(f'Error deleting quiz: {str(e)}', 'danger')
    else:
        flash('Quiz not found!', 'danger')
    return redirect(url_for('manage_quizzes'))

# Route to Edit Questions
@app.route('/admin/edit_question/<int:quiz_id>/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(quiz_id, question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        question.text = request.form['q_text']
        question.option_a = request.form['q_a']
        question.option_b = request.form['q_b']
        question.option_c = request.form['q_c']
        question.option_d = request.form['q_d']
        question.correct = request.form['q_correct']

        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('view_quiz', quiz_id=quiz_id))

    return render_template('admin/edit_question.html', question=question, quiz_id=quiz_id)

# Route to delete Questions
@app.route('/admin/delete_question/<int:quiz_id>/<int:question_id>', methods=['POST', 'GET'])
@login_required
def delete_question(quiz_id, question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('view_quiz', quiz_id=quiz_id))


# Helper functions
def get_all_quizzes():
    return Quiz.query.all()  # Fetch all quizzes from the database

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
