"""
Sprint 3 - Messages Blueprint
Handles: Send preset messages to listing owners, reply with preset replies, inbox
"""
from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from models.message_model import (
    send_message, reply_to_message, get_inbox, get_sent_messages,
    get_message_by_id, mark_as_read, PRESET_MESSAGES, PRESET_REPLIES
)
from utils.security import login_required

messages_bp = Blueprint('sprint3_messages', __name__, template_folder='templates')

VALID_TARGETS = ('listing', 'wish', 'campaign')


def _resolve_target(target_type, target_id):
    """Return (owner_id, back_url) for a target, or (None, None)."""
    if target_type == 'listing':
        from models.listing_model import get_listing_by_id
        it = get_listing_by_id(target_id)
        if it:
            return it['owner_id'], url_for('sprint1_listings.view_listing', listing_id=target_id)
    elif target_type == 'wish':
        from models.wish_model import get_wish_by_id
        it = get_wish_by_id(target_id)
        if it:
            return it['user_id'], url_for('sprint1_wishes.view_wish', wish_id=target_id)
    elif target_type == 'campaign':
        from models.donation_model import get_campaign_by_id
        it = get_campaign_by_id(target_id)
        if it:
            return it['user_id'], url_for('sprint1_donations.view_campaign', campaign_id=target_id)
    return None, None


@messages_bp.route('/messages')
@login_required
def inbox():
    tab = request.args.get('tab', 'received')
    received = get_inbox(session['user_id'])
    sent = get_sent_messages(session['user_id'])
    return render_template('sprint3/inbox.html',
        received=received, sent=sent, tab=tab,
        preset_replies=PRESET_REPLIES)


@messages_bp.route('/messages/send/<target_type>/<int:target_id>', methods=['POST'])
@login_required
def send(target_type, target_id):
    if target_type not in VALID_TARGETS:
        flash('Invalid message target.', 'danger')
        return redirect(url_for('sprint1_listings.browse'))

    owner_id, back_url = _resolve_target(target_type, target_id)
    if owner_id is None:
        flash('Item not found.', 'warning')
        return redirect(url_for('sprint1_listings.browse'))

    if owner_id == session['user_id']:
        flash('You cannot message yourself.', 'warning')
        return redirect(back_url)

    message_text = request.form.get('message_text', '').strip()

    # Validate: must be one of the preset messages
    if message_text not in PRESET_MESSAGES:
        flash('Please select a valid message.', 'danger')
        return redirect(back_url)

    if send_message(session['user_id'], owner_id, target_type, target_id, message_text):
        flash('Message sent to the owner!', 'success')
    else:
        flash('Failed to send message.', 'danger')

    return redirect(back_url)


@messages_bp.route('/messages/reply/<int:message_id>', methods=['POST'])
@login_required
def reply(message_id):
    msg = get_message_by_id(message_id)
    if not msg:
        flash('Message not found.', 'warning')
        return redirect(url_for('sprint3_messages.inbox'))

    # Only the receiver (listing owner) can reply
    if msg['receiver_id'] != session['user_id']:
        flash('You can only reply to messages sent to you.', 'danger')
        return redirect(url_for('sprint3_messages.inbox'))

    reply_text = request.form.get('reply_text', '').strip()

    # Validate: must be one of the preset replies
    if reply_text not in PRESET_REPLIES:
        flash('Please select a valid reply.', 'danger')
        return redirect(url_for('sprint3_messages.inbox'))

    if reply_to_message(message_id, reply_text):
        flash('Reply sent!', 'success')
    else:
        flash('Failed to send reply.', 'danger')

    return redirect(url_for('sprint3_messages.inbox'))


@messages_bp.route('/messages/<int:message_id>/read')
@login_required
def read_message(message_id):
    msg = get_message_by_id(message_id)
    if not msg:
        flash('Message not found.', 'warning')
        return redirect(url_for('sprint3_messages.inbox'))

    # Only sender or receiver can view
    if msg['sender_id'] != session['user_id'] and msg['receiver_id'] != session['user_id']:
        flash('Access denied.', 'danger')
        return redirect(url_for('sprint3_messages.inbox'))

    # Mark as read if receiver is viewing
    if msg['receiver_id'] == session['user_id'] and not msg['is_read']:
        mark_as_read(message_id)

    return render_template('sprint3/view_message.html', msg=msg, preset_replies=PRESET_REPLIES)
