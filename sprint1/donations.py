"""Sprint 1 - Donations Blueprint"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.donation_model import (
    create_campaign, get_campaigns, get_campaign_by_id,
    get_user_campaigns, get_featured_benevol_campaign, delete_campaign,
    DONATION_CATEGORIES
)
from utils.security import login_required
from utils.helpers import save_upload

donations_bp = Blueprint('sprint1_donations', __name__)


@donations_bp.route('/donate')
def donate():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    camp_type = request.args.get('type', '')
    campaigns, total, total_pages = get_campaigns(
        category=category, campaign_type=camp_type, page=page
    )
    featured = get_featured_benevol_campaign()
    return render_template('sprint1/donations.html',
        campaigns=campaigns, total=total, page=page, total_pages=total_pages,
        category=category, camp_type=camp_type,
        categories=DONATION_CATEGORIES, featured=featured)


@donations_bp.route('/donate/create', methods=['GET', 'POST'])
@login_required
def create_donation():
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        category    = request.form.get('category', '').strip()
        org_name    = request.form.get('org_name', '').strip()
        purpose     = request.form.get('purpose', '').strip()
        target_raw  = request.form.get('target_amount', '').strip()
        contact     = request.form.get('contact', '').strip()
        city        = request.form.get('city', '').strip()
        camp_type   = request.form.get('campaign_type', 'personal')

        if not all([title, category, purpose, target_raw, contact, city]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('sprint1/create_campaign.html',
                categories=DONATION_CATEGORIES,
                title=title, category=category, org_name=org_name,
                purpose=purpose, target_amount=target_raw,
                contact=contact, city=city)

        try:
            target_amount = float(target_raw)
            if target_amount <= 0:
                raise ValueError
        except ValueError:
            flash('Please enter a valid target amount greater than 0.', 'danger')
            return render_template('sprint1/create_campaign.html',
                categories=DONATION_CATEGORIES,
                title=title, category=category, org_name=org_name,
                purpose=purpose, target_amount=target_raw,
                contact=contact, city=city)

        if camp_type == 'benevol' and session.get('role') != 'admin':
            camp_type = 'personal'

        proof_path = save_upload(request.files.get('proof'))

        campaign_id = create_campaign(
            title, category, org_name, purpose, target_amount,
            proof_path, contact, city, camp_type, session['user_id']
        )
        flash('Your donation campaign has been created successfully!', 'success')
        return redirect(url_for('sprint1_donations.view_campaign', campaign_id=campaign_id))

    return render_template('sprint1/create_campaign.html', categories=DONATION_CATEGORIES)


@donations_bp.route('/donate/<int:campaign_id>')
def view_campaign(campaign_id):
    from flask import current_app
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        flash('Campaign not found.', 'danger')
        return redirect(url_for('sprint1_donations.donate'))
    has_reported = False
    if current_app.config.get('SPRINT2') and session.get('user_id'):
        from models.report_model import has_reported as _hr
        has_reported = _hr(session['user_id'], 'campaign', campaign_id)
    return render_template('sprint1/view_campaign.html', campaign=campaign, has_reported=has_reported)


@donations_bp.route('/donate/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_donation(campaign_id):
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        flash('Campaign not found.', 'warning')
        return redirect(url_for('sprint1_donations.donate'))
    if campaign['user_id'] != session['user_id'] and session.get('role') != 'admin':
        flash('You can only delete your own campaigns.', 'danger')
        return redirect(url_for('sprint1_donations.donate'))
    delete_campaign(campaign_id)
    flash('Campaign deleted.', 'success')
    return redirect(request.referrer or url_for('sprint1_donations.donate'))
