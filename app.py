import os
from flask import Flask
from markupsafe import Markup, escape
from config import Config
from database import init_db, seed_demo_data
from feature_flags import resolve_flags


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.template_filter('nl2br')
    def nl2br(value):
        """HTML-escape user text, then convert real newlines to <br> tags.
        Escaping happens on a plain str via str.replace (not Jinja's
        autoescape-aware `replace` filter) so the inserted <br> tags are
        never re-escaped themselves."""
        if not value:
            return ''
        safe_text = str(escape(value))
        return Markup(safe_text.replace('\n', '<br>'))

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    sprint1, sprint2, sprint3 = resolve_flags()    #change later
   # sprint1, sprint2, sprint3 = True, True, False  # For testing purposes, enable all sprints

    app.config['SPRINT1'] = sprint1
    app.config['SPRINT2'] = sprint2
    app.config['SPRINT3'] = sprint3

    init_db()
    seed_demo_data()

    @app.before_request
    def log_pageview():
        from flask import request, session
        # Only count real page loads: GET requests, skip static files and
        # the JSON API (those aren't "pages" someone browsed to).
        if request.method != 'GET':
            return
        if request.endpoint in (None, 'static') or (request.endpoint or '').startswith('sprint3_api.'):
            return
        from models.pageview_model import log_pageview as _log
        _log(request.path, session.get('user_id'))

    if sprint1:
        from sprint1.auth import auth_bp
        from sprint1.listings import listings_bp
        from sprint1.donations import donations_bp
        from sprint1.wishes import wishes_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(listings_bp)
        app.register_blueprint(donations_bp)
        app.register_blueprint(wishes_bp)
        print("[APP] Sprint 1 loaded: Auth, Listings, Search, Donations, Wishes")

    if sprint2:
        from sprint2.bookmarks import bookmarks_bp
        from sprint2.ratings import ratings_bp
        from sprint2.reports import reports_bp
        from sprint2.activity_logs import activity_bp
        app.register_blueprint(bookmarks_bp)
        app.register_blueprint(ratings_bp)
        app.register_blueprint(reports_bp)
        app.register_blueprint(activity_bp)
        print("[APP] Sprint 2 loaded: Bookmarks, Ratings, Reports, Activity Logs")

    if sprint3:
        from sprint3.analytics import analytics_bp
        from sprint3.api import api_bp
        from sprint3.messages import messages_bp
        app.register_blueprint(analytics_bp)
        app.register_blueprint(api_bp)
        app.register_blueprint(messages_bp)
        print("[APP] Sprint 3 loaded: Analytics, REST API, Messages")

    @app.context_processor
    def inject_sprint_flags():
        ctx = {
            'config': {
                'SPRINT1': sprint1,
                'SPRINT2': sprint2,
                'SPRINT3': sprint3,
                'GA_MEASUREMENT_ID': app.config.get('GA_MEASUREMENT_ID', ''),
                'CLARITY_PROJECT_ID': app.config.get('CLARITY_PROJECT_ID', ''),
            }
        }

        from flask import request, session

        if sprint2 and session.get('user_id'):
            if request.endpoint == 'sprint1_listings.view_listing':
                listing_id = request.view_args.get('listing_id')
                if listing_id:
                    from models.bookmark_model import is_bookmarked
                    from models.report_model import has_reported
                    ctx['is_bookmarked'] = is_bookmarked(session['user_id'], listing_id)
                    ctx['has_reported'] = has_reported(session['user_id'], 'listing', listing_id)

            if request.endpoint == 'sprint1_auth.profile':
                from models.rating_model import get_average_rating
                from models.bookmark_model import get_user_bookmarks
                avg, cnt = get_average_rating(session['user_id'])
                ctx['avg_rating'] = avg
                ctx['rating_count'] = cnt
                ctx['bookmark_count'] = len(get_user_bookmarks(session['user_id']))

            if request.endpoint == 'sprint1_listings.dashboard':
                from models.rating_model import get_average_rating
                from models.bookmark_model import get_user_bookmarks
                avg, cnt = get_average_rating(session['user_id'])
                ctx['avg_rating'] = avg
                ctx['bookmark_count'] = len(get_user_bookmarks(session['user_id']))

            if request.endpoint == 'sprint1_auth.public_profile':
                user_id = request.view_args.get('user_id')
                if user_id:
                    from models.rating_model import get_average_rating, get_user_rating, get_ratings_for_user
                    avg, cnt = get_average_rating(user_id)
                    ctx['avg_rating'] = avg
                    ctx['rating_count'] = cnt
                    ctx['ratings'] = get_ratings_for_user(user_id)
                    ctx['my_rating'] = get_user_rating(session['user_id'], user_id)

        if sprint3 and session.get('user_id'):
            from models.message_model import count_unread, PRESET_MESSAGES
            ctx['unread_count'] = count_unread(session['user_id'])
            ctx['preset_messages'] = PRESET_MESSAGES

        return ctx

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n" + "=" * 50)
    print(" BENEVOL - Community Sharing Platform")
    print(" http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
