"""
Sprint 3 - Analytics Blueprint
Handles: Admin analytics dashboard with charts
"""
from flask import Blueprint, render_template, jsonify
from models.listing_model import count_listings, get_listings_per_category, get_listings_per_city, get_monthly_listings
from models.user_model import count_users
from models.report_model import count_reports
from models.activity_model import count_activities
from utils.security import admin_required

analytics_bp = Blueprint('sprint3_analytics', __name__, template_folder='templates')


@analytics_bp.route('/admin/analytics')
@admin_required
def analytics_dashboard():
    from models.wish_model import count_wishes
    from models.donation_model import count_campaigns

    stats = {
        'total_listings': count_listings(),
        'total_users': count_users(),
        'total_wishes': count_wishes(),
        'total_campaigns': count_campaigns(),
        'pending_reports': count_reports('pending'),
        'total_activities': count_activities(),
    }

    return render_template('sprint3/analytics.html', stats=stats)


@analytics_bp.route('/admin/analytics/data')
@admin_required
def analytics_data():
    """Return analytics data as JSON for Chart.js."""
    categories = get_listings_per_category()
    cities = get_listings_per_city()
    monthly = get_monthly_listings()

    return jsonify({
        'categories': {
            'labels': [r['category'] for r in categories],
            'data': [r['cnt'] for r in categories]
        },
        'cities': {
            'labels': [r['city'] for r in cities],
            'data': [r['cnt'] for r in cities]
        },
        'monthly': {
            'labels': [r['month'] for r in reversed(list(monthly))],
            'data': [r['cnt'] for r in reversed(list(monthly))]
        }
    })
