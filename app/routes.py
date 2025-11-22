from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash
from sqlalchemy import select
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    # Render the main index template; pass current_user for conditional UI
    return render_template('index.html', user=current_user if current_user.is_authenticated else None)


@main.route('/register', methods=["GET", "POST"])
def register():
    SessionLocal = current_app.db_session
    if request.method == 'GET':
        return render_template('register.html')

    # POST: process form submission
    login_val = request.form.get('login')
    password = request.form.get('password')
    if not login_val or not password:
        flash('Login and password are required', 'error')
        return render_template('register.html', login=login_val)

    session = SessionLocal()
    try:
        from app.models import User, UserType

        existing = session.execute(select(User).where(User.login == login_val)).scalar_one_or_none()
        if existing:
            flash('User already exists', 'error')
            return render_template('register.html', login=login_val)

        user = User(login=login_val)
        user.set_password(password)
        type_str = request.form.get('type')
        if type_str and type_str.upper() in UserType.__members__:
            user.type = UserType[type_str.upper()]

        session.add(user)
        session.commit()
        flash('User created, please log in', 'success')
        return redirect(url_for('main.login'))
    finally:
        session.close()


@main.route('/login', methods=["GET", "POST"])
def login():
    SessionLocal = current_app.db_session
    if request.method == 'GET':
        return render_template('login.html')

    login_val = request.form.get('login')
    password = request.form.get('password')
    if not login_val or not password:
        flash('Login and password are required', 'error')
        return render_template('login.html', login=login_val)

    session = SessionLocal()
    try:
        from app.models import User

        user = session.execute(select(User).where(User.login == login_val)).scalar_one_or_none()
        if not user or not user.check_password(password):
            flash('Invalid credentials', 'error')
            return render_template('login.html', login=login_val)

        login_user(user)
        flash('Logged in successfully', 'success')
        return redirect(url_for('main.index'))
    finally:
        session.close()


@main.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('main.index'))
