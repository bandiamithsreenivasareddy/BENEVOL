"""
Sprint 2 - Bookmarks Blueprint
Handles: Add/Remove Bookmarks, View Saved Items
"""
from flask import Blueprint, redirect, url_for, flash, session, render_template
from models.bookmark_model import add_bookmark, remove_bookmark, is_bookmarked, get_user_bookmarks
from models.listing_model import get_listing_by_id
from utils.security import login_required

bookmarks_bp = Blueprint('sprint2_bookmarks', __name__, template_folder='templates')


@bookmarks_bp.route('/bookmark/add/<int:listing_id>', methods=['POST'])
@login_required
def add(listing_id):
    listing = get_listing_by_id(listing_id)
    if not listing:
        flash('Listing not found.', 'warning')
        return redirect(url_for('sprint1_listings.browse'))

    if listing['owner_id'] == session['user_id']:
        flash('You cannot bookmark your own listing.', 'info')
        return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))

    if is_bookmarked(session['user_id'], listing_id):
        flash('Already bookmarked.', 'info')
    else:
        add_bookmark(session['user_id'], listing_id)
        flash('Listing bookmarked!', 'success')

    return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))


@bookmarks_bp.route('/bookmark/remove/<int:listing_id>', methods=['POST'])
@login_required
def remove(listing_id):
    remove_bookmark(session['user_id'], listing_id)
    flash('Bookmark removed.', 'info')
    referer = session.get('_bookmark_referer', url_for('sprint2_bookmarks.my_bookmarks'))
    return redirect(url_for('sprint2_bookmarks.my_bookmarks'))


@bookmarks_bp.route('/bookmarks')
@login_required
def my_bookmarks():
    bookmarks = get_user_bookmarks(session['user_id'])
    return render_template('sprint2/bookmarks.html', bookmarks=bookmarks)
