from flask import Blueprint, request, jsonify
from src.models.watchlist_model import db, Watchlist

watchlist_bp = Blueprint("watchlist", __name__)

@watchlist_bp.route("/test", methods=["GET"])
def test_watchlist():
    return {"message": "Watchlist route is working"}

@watchlist_bp.route("/", methods=["GET"])
def get_watchlist():
    try:
        user_id = request.args.get("user_id", "guest")
        items = Watchlist.query.filter_by(user_id=user_id).all()

        return jsonify([{
            "id": item.id,
            "ticker": item.ticker,
            "notes": item.notes,
            "priority": item.priority,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S") 
        } for item in items])
    except Exception as e:
        print("WATCHLIST ERROR:", e)
        return jsonify({"error": str(e)}), 500

@watchlist_bp.route("/", methods=["POST"])
def add_to_watchlist():
    data = request.get_json()

    try:
        user_id = data.get("user_id")
        ticker = data.get("ticker")
        notes = data.get("notes", "")
        priority = data.get("priority", 1)

        new_entry = Watchlist(user_id=user_id, ticker=ticker, notes=notes, priority=priority)
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Stock added to watchlist", "watchlist_id": new_entry.id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@watchlist_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_watchlist_item(item_id):
    item = Watchlist.query.get(item_id)
    if not item:
        return jsonify({"error": "Watchlist item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Watchlist item deleted", "watchlist_id": item_id})
