from app import app
from services.cache import db


def test_missing_url():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        client = app.test_client()

        response = client.post("/", data={})

        assert response.status_code == 400
        assert b"MISSING_URL" in response.data
