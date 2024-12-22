import sqlite3

from flask import Blueprint, jsonify, render_template, request
from models.feed_model import get_all_offers, DATABASE
from services.feed_service import fetch_feed, parse_and_store_feed

feed_blueprint = Blueprint('feed', __name__)

@feed_blueprint.route('/fetch-feed')
def fetch_and_store():
    feed_data = fetch_feed()
    if feed_data:
        new_offers = parse_and_store_feed(feed_data)
        return jsonify({"message": "Фід успішно завантажено та збережено", "new_offers": new_offers})
    return jsonify({"error": "Не вдалося завантажити фід"}), 500

@feed_blueprint.route('/offers')
def get_offers():
    offers = get_all_offers()
    return jsonify([{
        "id": offer[0],
        "name": offer[1],
        "price": offer[2],
        "vendor": offer[3],
        "quantity_in_stock": offer[4],
        "picture": offer[5],
        "timestamp": offer[6]
    } for offer in offers])


@feed_blueprint.route('/dashboard')
def dashboard():
    search = request.args.get('search', None)
    from models.feed_model import get_all_offers
    offers_raw = get_all_offers(search=search)

    offers = [
        {
            "picture": row[5],
            "name": row[1],
            "price": row[2],
            "quantity_in_stock": row[4],
            "vendor": row[3],
            "timestamp": row[6],
        }
        for row in offers_raw
    ]

    return render_template('dashboard.html', offers=offers)



@feed_blueprint.route('/changes')
def changes():
    from models.feed_model import get_filtered_changes
    field = request.args.get('field', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    search = request.args.get('search', '')

    changes = get_filtered_changes(field, start_date, end_date, search)
    return render_template('changes.html', changes=changes)


from models.feed_model import init_db
init_db()
