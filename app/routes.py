from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, abort
from sqlalchemy import select
from flask_login import login_user, logout_user, login_required, current_user

from app.models import User, UserType

main = Blueprint('main', __name__)
# pull requestttt


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    login_val = request.form.get('login')
    password = request.form.get('password')
    if not login_val or not password:
        flash('Login and password required', 'error')
        return render_template('register.html', login=login_val)

    SessionLocal = current_app.db_session
    session = SessionLocal()
    try:
        existing = session.execute(select(User).where(User.login == login_val)).scalar_one_or_none()
        if existing:
            flash('User already exists', 'error')
            return render_template('register.html', login=login_val)

        user = User(login=login_val)
        user.set_password(password)
        # default type is PEASANT; allow passing 'type' in form if needed
        type_str = request.form.get('type')
        if type_str and type_str.upper() in UserType.__members__:
            user.type = UserType[type_str.upper()]

        session.add(user)
        session.commit()
        flash('User created, please log in', 'success')
        return redirect(url_for('main.login'))
    finally:
        session.close()


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    login_val = request.form.get('login')
    password = request.form.get('password')
    if not login_val or not password:
        flash('Login and password required', 'error')
        return render_template('login.html', login=login_val)

    SessionLocal = current_app.db_session
    session = SessionLocal()
    try:
        user = session.execute(select(User).where(User.login == login_val)).scalar_one_or_none()
        if not user or not user.check_password(password):
            flash('Invalid credentials', 'error')
            return render_template('login.html', login=login_val)

        login_user(user)
        flash('Logged in successfully', 'success')
        return redirect(url_for('main.index'))
    finally:
        session.close()


@main.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('main.index'))


@main.route('/admin')
@login_required
def admin():
    # simple role-based check
    if not current_user.is_authenticated or not getattr(current_user, 'type', None) == UserType.ADMIN:
        abort(403)
    return render_template('admin.html')


@main.route('/api/bug/divide')
def bug_divide():
    a = 10
    b = 1 
    result = a / b 
    return {'result': result}

