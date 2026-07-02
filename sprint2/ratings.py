"""
Sprint 2 - Ratings Blueprint
Handles: Rate users, View ratings
"""
from flask import Blueprint, request, redirect, url_for, flash, session
from models.rating_model import add_rating, get_user_rating
from models.user_model import get_user_by_id
from utils.security import login_required

ratings_bp = Blueprint('sprint2_ratings', __name__, template_folder='templates')


@ratings_bp.route('/rate/<int:user_id>', methods=['POST'])
@login_required
def rate_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot rate yourself.', 'warning')
        return redirect(url_for('sprint1_auth.public_profile', user_id=user_id))

    user = get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'warning')
        return redirect(url_for('sprint1_listings.browse'))

    rating_val = request.form.get('rating', 0, type=int)
    review = request.form.get('review', '').strip()

    if rating_val < 1 or rating_val > 5:
        flash('Rating must be between 1 and 5.', 'danger')
        return redirect(url_for('sprint1_auth.public_profile', user_id=user_id))

    if add_rating(session['user_id'], user_id, rating_val, review):
        flash('Rating submitted!', 'success')
    else:
        flash('Failed to submit rating.', 'danger')

    return redirect(url_for('sprint1_auth.public_profile', user_id=user_id))
