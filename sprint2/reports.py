"""
Sprint 2 - Reports Blueprint
Handles: Report listings/wishes/campaigns, Admin review reports
"""
from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from models.report_model import create_report, get_all_reports, update_report_status, has_reported
from models.listing_model import soft_delete_listing
from utils.security import login_required, admin_required

reports_bp = Blueprint('sprint2_reports', __name__, template_folder='templates')

VALID_TARGETS = ('listing', 'wish', 'campaign')


def _resolve_target(target_type, target_id):
    """Return (owner_id, back_url, title) for a target, or (None, None, None)."""
    if target_type == 'listing':
        from models.listing_model import get_listing_by_id
        it = get_listing_by_id(target_id)
        if it:
            return it['owner_id'], url_for('sprint1_listings.view_listing', listing_id=target_id), it['title']
    elif target_type == 'wish':
        from models.wish_model import get_wish_by_id
        it = get_wish_by_id(target_id)
        if it:
            return it['user_id'], url_for('sprint1_wishes.view_wish', wish_id=target_id), it['title']
    elif target_type == 'campaign':
        from models.donation_model import get_campaign_by_id
        it = get_campaign_by_id(target_id)
        if it:
            return it['user_id'], url_for('sprint1_donations.view_campaign', campaign_id=target_id), it['title']
    return None, None, None


@reports_bp.route('/report/<target_type>/<int:target_id>', methods=['POST'])
@login_required
def report_target(target_type, target_id):
    if target_type not in VALID_TARGETS:
        flash('Invalid report target.', 'danger')
        return redirect(url_for('sprint1_listings.browse'))

    owner_id, back_url, title = _resolve_target(target_type, target_id)
    if owner_id is None:
        flash('Item not found.', 'warning')
        return redirect(url_for('sprint1_listings.browse'))

    if owner_id == session['user_id']:
        flash('You cannot report your own item.', 'warning')
        return redirect(back_url)

    if has_reported(session['user_id'], target_type, target_id):
        flash('You have already reported this.', 'info')
        return redirect(back_url)

    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Please provide a reason for the report.', 'danger')
        return redirect(back_url)

    if create_report(session['user_id'], target_type, target_id, reason):
        try:
            from models.activity_model import log_activity
            log_activity(session['user_id'], 'report', f'Reported {target_type}: {title}')
        except Exception:
            pass
        flash('Report submitted. An admin will review it.', 'success')
    else:
        flash('Failed to submit report.', 'danger')

    return redirect(back_url)


@reports_bp.route('/admin/reports')
@admin_required
def admin_reports():
    status_filter = request.args.get('status', 'pending')
    reports = get_all_reports(status=status_filter if status_filter != 'all' else None)
    return render_template('sprint2/admin_reports.html', reports=reports, status_filter=status_filter)


@reports_bp.route('/admin/report/<int:report_id>/review', methods=['POST'])
@admin_required
def review_report(report_id):
    action = request.form.get('action', '')
    target_type = request.form.get('target_type', 'listing')
    target_id = request.form.get('target_id', 0, type=int)

    if action == 'remove':
        if target_type == 'listing':
            soft_delete_listing(target_id)
        elif target_type == 'wish':
            from models.wish_model import delete_wish
            delete_wish(target_id)
        elif target_type == 'campaign':
            from models.donation_model import delete_campaign
            delete_campaign(target_id)
        update_report_status(report_id, 'reviewed')
        flash('Reported item removed and report marked as reviewed.', 'success')
    elif action == 'dismiss':
        update_report_status(report_id, 'dismissed')
        flash('Report dismissed.', 'info')
    else:
        flash('Invalid action.', 'danger')

    return redirect(url_for('sprint2_reports.admin_reports'))
