import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class MenuCache(db.Model):
    __tablename__ = "menu_cache"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    menu_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("url", "date", name="unique_url_date"),)


def get_cached_menu(url, date):
    cached = MenuCache.query.filter_by(url=url, date=date).first()

    if cached:
        return json.loads(cached.menu_json)
    return None


def save_menu_to_cache(url, date, menu_data):
    menu_json = json.dumps(menu_data, ensure_ascii=False)

    # Check if exists
    existing = MenuCache.query.filter_by(url=url, date=date).first()

    if existing:
        existing.menu_json = menu_json
        existing.created_at = datetime.utcnow()
    else:
        new_cache = MenuCache(url=url, date=date, menu_json=menu_json)
        db.session.add(new_cache)

    db.session.commit()


def cleanup_old_cache(current_date):
    deleted = MenuCache.query.filter(MenuCache.date < current_date).delete()
    db.session.commit()
    return deleted
