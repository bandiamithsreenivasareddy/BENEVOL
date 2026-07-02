"""
Sprint 3 - REST API Blueprint
Handles: JSON API endpoints for listings
"""
from flask import Blueprint, request, jsonify, session
from models.listing_model import get_listing_by_id, get_listings, create_listing, update_listing, delete_listing

api_bp = Blueprint('sprint3_api', __name__)


def api_auth_required(f):
    """Simple API auth check via session."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


@api_bp.route('/api/listings', methods=['GET'])
def api_get_listings():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    city = request.args.get('city', '')

    listings, total, total_pages = get_listings(
        page=page, search=search, category=category, city=city
    )

    return jsonify({
        'listings': [dict(row) for row in listings],
        'total': total,
        'page': page,
        'total_pages': total_pages
    })


@api_bp.route('/api/listing/<int:listing_id>', methods=['GET'])
def api_get_listing(listing_id):
    listing = get_listing_by_id(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    return jsonify(dict(listing))


@api_bp.route('/api/create', methods=['POST'])
@api_auth_required
def api_create_listing():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    required = ['title', 'description', 'category', 'city']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    listing_id = create_listing(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        city=data['city'],
        condition=data.get('condition', 'Good'),
        image_path=data.get('image_path', ''),
        owner_id=session['user_id']
    )

    if listing_id:
        return jsonify({'id': listing_id, 'message': 'Listing created'}), 201
    return jsonify({'error': 'Failed to create listing'}), 500


@api_bp.route('/api/update/<int:listing_id>', methods=['PUT'])
@api_auth_required
def api_update_listing(listing_id):
    listing = get_listing_by_id(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    if listing['owner_id'] != session['user_id'] and session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    allowed = {k: v for k, v in data.items() if k in ('title', 'description', 'category', 'city', 'condition')}
    if update_listing(listing_id, **allowed):
        return jsonify({'message': 'Listing updated'})
    return jsonify({'error': 'Failed to update listing'}), 500


@api_bp.route('/api/listing/<int:listing_id>', methods=['DELETE'])
@api_auth_required
def api_delete_listing(listing_id):
    listing = get_listing_by_id(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    if listing['owner_id'] != session['user_id'] and session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    if delete_listing(listing_id):
        return jsonify({'message': 'Listing deleted'})
    return jsonify({'error': 'Failed to delete listing'}), 500
