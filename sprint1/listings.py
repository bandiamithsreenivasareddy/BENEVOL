"""
Sprint 1 - Listings Blueprint
Handles: Create, Edit, Delete, View, Browse Listings
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.listing_model import (
    create_listing, get_listing_by_id, update_listing,
    delete_listing, get_listings, get_categories, get_cities
)
from utils.security import login_required
from utils.helpers import save_upload, CATEGORIES, CONDITIONS

listings_bp = Blueprint('sprint1_listings', __name__, template_folder='templates')


@listings_bp.route('/')
def home():
    listings, _, _ = get_listings(page=1, per_page=6)
    from models.donation_model import get_campaigns
    from models.wish_model import get_wishes
    campaigns, _, _ = get_campaigns(page=1, per_page=3)
    wishes, _, _ = get_wishes(page=1, per_page=3)
    return render_template('sprint1/home.html',
        listings=listings, categories=CATEGORIES,
        campaigns=campaigns, wishes=wishes)


@listings_bp.route('/browse')
def browse():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    sort = request.args.get('sort', 'newest')

    listings, total, total_pages = get_listings(
        page=page, search=search, category=category, city=city, sort=sort
    )
    categories = get_categories()
    cities = get_cities()

    return render_template('sprint1/browse.html',
        listings=listings, total=total, page=page, total_pages=total_pages,
        search=search, category=category, city=city, sort=sort,
        categories=categories, cities=cities, all_categories=CATEGORIES
    )


@listings_bp.route('/listing/<int:listing_id>')
def view_listing(listing_id):
    listing = get_listing_by_id(listing_id)
    if not listing or listing['status'] == 'soft_deleted':
        flash('Listing not found.', 'warning')
        return redirect(url_for('sprint1_listings.browse'))
    return render_template('sprint1/view_listing.html', listing=listing)


@listings_bp.route('/listing/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        city = request.form.get('city', '').strip()
        location = request.form.get('location', '').strip()
        condition = request.form.get('condition', 'Good').strip()
        contact_number = request.form.get('contact_number', '').strip()

        errors = []
        if not title or len(title) < 3:
            errors.append('Title must be at least 3 characters.')
        if not description:
            errors.append('Description is required.')
        if not category:
            errors.append('Category is required.')
        if not city:
            errors.append('City is required.')

        image_path = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_path = save_upload(file)

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('sprint1/create_listing.html',
                categories=CATEGORIES, conditions=CONDITIONS,
                title=title, description=description, category=category,
                city=city, condition=condition, location=location, contact_number=contact_number)

        listing_id = create_listing(title, description, category, city, condition, image_path, session['user_id'], location, contact_number)
        if listing_id:
            # Log activity if sprint2 is enabled
            try:
                from feature_flags import resolve_flags
                _, s2, _ = resolve_flags()
                if s2:
                    from models.activity_model import log_activity
                    log_activity(session['user_id'], 'create_listing', f'Created listing: {title}')
            except Exception:
                pass
            flash('Listing created successfully!', 'success')
            return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))
        else:
            flash('Failed to create listing.', 'danger')

    return render_template('sprint1/create_listing.html', categories=CATEGORIES, conditions=CONDITIONS)


@listings_bp.route('/listing/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(listing_id):
    listing = get_listing_by_id(listing_id)
    if not listing:
        flash('Listing not found.', 'warning')
        return redirect(url_for('sprint1_listings.browse'))
    if listing['owner_id'] != session['user_id'] and session.get('role') != 'admin':
        flash('You can only edit your own listings.', 'danger')
        return redirect(url_for('sprint1_listings.browse'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        city = request.form.get('city', '').strip()
        location = request.form.get('location', '').strip()
        condition = request.form.get('condition', 'Good').strip()
        contact_number = request.form.get('contact_number', '').strip()

        updates = {'title': title, 'description': description,
                   'category': category, 'city': city, 'condition': condition,
                   'location': location, 'contact_number': contact_number}

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_path = save_upload(file)
                if image_path:
                    updates['image_path'] = image_path

        if update_listing(listing_id, **updates):
            flash('Listing updated successfully!', 'success')
            return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))
        else:
            flash('Failed to update listing.', 'danger')

    return render_template('sprint1/edit_listing.html',
        listing=listing, categories=CATEGORIES, conditions=CONDITIONS)


@listings_bp.route('/listing/<int:listing_id>/delete', methods=['POST'])
@login_required
def delete(listing_id):
    listing = get_listing_by_id(listing_id)
    if not listing:
        flash('Listing not found.', 'warning')
        return redirect(url_for('sprint1_listings.browse'))
    if listing['owner_id'] != session['user_id'] and session.get('role') != 'admin':
        flash('You can only delete your own listings.', 'danger')
        return redirect(url_for('sprint1_listings.browse'))

    if delete_listing(listing_id):
        # Log activity if sprint2 is enabled
        try:
            from feature_flags import resolve_flags
            _, s2, _ = resolve_flags()
            if s2:
                from models.activity_model import log_activity
                log_activity(session['user_id'], 'delete_listing', f"Deleted listing: {listing['title']}")
        except Exception:
            pass
        flash('Listing deleted.', 'success')
    else:
        flash('Failed to delete listing.', 'danger')

    return redirect(url_for('sprint1_listings.browse'))


@listings_bp.route('/dashboard')
@login_required
def dashboard():
    uid = session['user_id']
    is_admin = session.get('role') == 'admin'

    my_listings, total, _ = get_listings(owner_id=uid, per_page=100, status='active')

    from models.wish_model import get_user_wishes, get_all_wishes
    from models.donation_model import get_user_campaigns, get_all_campaigns
    my_wishes = get_user_wishes(uid)
    my_campaigns = get_user_campaigns(uid)

    # Admin oversight: everything across the platform
    all_listings, all_wishes, all_campaigns = [], [], []
    listings_total = 0
    if is_admin:
        all_listings, listings_total, _ = get_listings(per_page=500, status='active')
        all_wishes = get_all_wishes()
        all_campaigns = get_all_campaigns()

    return render_template('sprint1/dashboard.html',
        listings=my_listings, total=total,
        wishes=my_wishes, campaigns=my_campaigns,
        is_admin=is_admin,
        all_listings=all_listings, listings_total=listings_total,
        all_wishes=all_wishes, all_campaigns=all_campaigns)
