"""
Sprint 1 - Authentication Blueprint
Handles: Registration, Login, Logout, Profile, Session Management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user_model import create_user, get_user_by_username, get_user_by_email, get_user_by_id, update_user
from utils.security import hash_password, verify_password, login_required

auth_bp = Blueprint('sprint1_auth', __name__, template_folder='templates')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        city = request.form.get('city', '').strip()

        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Valid email is required.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if get_user_by_username(username):
            errors.append('Username already taken.')
        if get_user_by_email(email):
            errors.append('Email already registered.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('sprint1/register.html', username=username, email=email, city=city)

        if create_user(username, email, hash_password(password), city):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('sprint1_auth.login'))
        else:
            flash('Registration failed. Please try again.', 'danger')

    return render_template('sprint1/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = get_user_by_username(username)
        if user and verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            # Log activity if sprint2 is enabled
            try:
                from feature_flags import resolve_flags
                _, s2, _ = resolve_flags()
                if s2:
                    from models.activity_model import log_activity
                    log_activity(user['id'], 'login', f"User {user['username']} logged in")
            except Exception:
                pass

            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('sprint1_listings.browse'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('sprint1/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('sprint1_auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    from models.listing_model import get_listings
    my_listings, total, _ = get_listings(owner_id=session['user_id'], per_page=100, status='active')
    from models.wish_model import get_user_wishes
    from models.donation_model import get_user_campaigns
    my_wishes = get_user_wishes(session['user_id'])
    my_campaigns = get_user_campaigns(session['user_id'])
    return render_template('sprint1/profile.html', user=user,
        listings=my_listings, total=total,
        wishes=my_wishes, campaigns=my_campaigns)


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = get_user_by_id(session['user_id'])
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        email = request.form.get('email', '').strip()

        if email and email != user['email']:
            existing = get_user_by_email(email)
            if existing:
                flash('Email already in use.', 'danger')
                return render_template('sprint1/edit_profile.html', user=user)

        update_user(session['user_id'], city=city, email=email)
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('sprint1_auth.profile'))

    return render_template('sprint1/edit_profile.html', user=user)


@auth_bp.route('/user/<int:user_id>')
def public_profile(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'warning')
        return redirect(url_for('sprint1_listings.browse'))

    from models.listing_model import get_listings
    listings, total, _ = get_listings(owner_id=user_id, per_page=100, status='active')
    return render_template('sprint1/public_profile.html', profile_user=user, listings=listings, total=total)
