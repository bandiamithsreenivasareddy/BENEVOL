"""Sprint 1 - Wishes Blueprint (Make a Wish / community item requests)."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.wish_model import (
    create_wish, get_wishes, get_wish_by_id, mark_fulfilled, delete_wish,
    get_wish_cities, WISH_CATEGORIES, URGENCY_LEVELS
)
from utils.security import login_required

wishes_bp = Blueprint('sprint1_wishes', __name__)


@wishes_bp.route('/wishes')
def wishes():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    urgency = request.args.get('urgency', '')
    wishlist, total, total_pages = get_wishes(category=category, urgency=urgency, page=page)
    return render_template('sprint1/wishes.html',
        wishes=wishlist, total=total, page=page, total_pages=total_pages,
        category=category, urgency=urgency,
        categories=WISH_CATEGORIES, urgency_levels=URGENCY_LEVELS)


@wishes_bp.route('/wishes/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        category    = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        city        = request.form.get('city', '').strip()
        contact     = request.form.get('contact', '').strip()
        urgency     = request.form.get('urgency', 'Normal').strip()

        if urgency not in URGENCY_LEVELS:
            urgency = 'Normal'

        if not all([title, category, description, city, contact]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('sprint1/create_wish.html',
                categories=WISH_CATEGORIES, urgency_levels=URGENCY_LEVELS,
                title=title, category=category, description=description,
                city=city, contact=contact, urgency=urgency)

        wish_id = create_wish(title, category, description, city,
                              contact, urgency, session['user_id'])
        flash('Your wish has been posted! The community can now see it.', 'success')
        return redirect(url_for('sprint1_wishes.view_wish', wish_id=wish_id))

    return render_template('sprint1/create_wish.html',
        categories=WISH_CATEGORIES, urgency_levels=URGENCY_LEVELS)


@wishes_bp.route('/wishes/<int:wish_id>')
def view_wish(wish_id):
    from flask import current_app
    wish = get_wish_by_id(wish_id)
    if not wish:
        flash('Wish not found.', 'danger')
        return redirect(url_for('sprint1_wishes.wishes'))
    has_reported = False
    if current_app.config.get('SPRINT2') and session.get('user_id'):
        from models.report_model import has_reported as _hr
        has_reported = _hr(session['user_id'], 'wish', wish_id)
    return render_template('sprint1/view_wish.html', wish=wish, has_reported=has_reported)


@wishes_bp.route('/wishes/<int:wish_id>/fulfill', methods=['POST'])
@login_required
def fulfill(wish_id):
    if mark_fulfilled(wish_id, session['user_id']):
        flash('Wish marked as fulfilled. Thank you for sharing the good news!', 'success')
    else:
        flash('Could not update this wish.', 'danger')
    return redirect(url_for('sprint1_wishes.view_wish', wish_id=wish_id))


@wishes_bp.route('/wishes/<int:wish_id>/delete', methods=['POST'])
@login_required
def delete(wish_id):
    wish = get_wish_by_id(wish_id)
    if not wish:
        flash('Wish not found.', 'warning')
        return redirect(url_for('sprint1_wishes.wishes'))
    if wish['user_id'] != session['user_id'] and session.get('role') != 'admin':
        flash('You can only delete your own wishes.', 'danger')
        return redirect(url_for('sprint1_wishes.wishes'))
    delete_wish(wish_id)
    flash('Wish deleted.', 'success')
    return redirect(request.referrer or url_for('sprint1_wishes.wishes'))
