from flask import Flask
from services.cache import db, save_menu_to_cache, get_cached_menu


def test_cache_save_and_get():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

        test_data = {"restaurant_name": "Test", "menu_items": []}

        save_menu_to_cache("http://test.com", "2025-10-31", test_data)
        cached = get_cached_menu("http://test.com", "2025-10-31")

        assert cached is not None
        assert cached["restaurant_name"] == "Test"
