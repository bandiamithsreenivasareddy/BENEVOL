"""
Sprint 2 - Activity Logs Blueprint
Handles: View activity logs
"""
from flask import Blueprint, render_template, session
from models.activity_model import get_user_activity, get_all_activity
from utils.security import login_required, admin_required

activity_bp = Blueprint('sprint2_activity', __name__, template_folder='templates')


@activity_bp.route('/activity')
@login_required
def my_activity():
    logs = get_user_activity(session['user_id'], limit=50)
    return render_template('sprint2/activity.html', logs=logs)


@activity_bp.route('/admin/activity')
@admin_required
def all_activity():
    logs = get_all_activity(limit=100)
    return render_template('sprint2/admin_activity.html', logs=logs)
