from app import app
from services.cache import db
from unittest.mock import patch, MagicMock


def test_missing_url():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        client = app.test_client()

        response = client.post("/", data={})

        assert response.status_code == 400
        assert b"MISSING_URL" in response.data


def test_full_menu_extraction_flow():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        client = app.test_client()

        mock_scraped_data = {
            "text": "Denní menu: Polévka 45 Kč, Kuřecí řízek 145 Kč",
            "url": "http://restaurant.cz/menu",
            "status": 200,
            "content_type": "text/html",
            "title": "Restaurant Menu"
        }

        mock_menu_item1 = MagicMock()
        mock_menu_item1.model_dump.return_value = {
            "category": "polévka",
            "name": "Hovězí polévka",
            "price": 45,
            "allergens": ["1", "3"],
            "weight": None
        }

        mock_menu_item2 = MagicMock()
        mock_menu_item2.model_dump.return_value = {
            "category": "hlavní jídlo",
            "name": "Kuřecí řízek s bramborovou kaší",
            "price": 145,
            "allergens": ["1", "3", "7"],
            "weight": "150g"
        }

        mock_menu = MagicMock()
        mock_menu.restaurant_name = "Restaurant Example"
        mock_menu.menu_items = [mock_menu_item1, mock_menu_item2]
        mock_menu.daily_menu = True

        with patch('app.get_html_content', return_value=mock_scraped_data):
            with patch('app.extract_menu_llm', return_value=mock_menu):

                response = client.post("/", data={"url": "http://restaurant.cz/menu"})

                assert response.status_code == 200

                json_data = response.json

                assert json_data["restaurant_name"] == "Restaurant Example"
                assert json_data["daily_menu"] == True
                assert "date" in json_data
                assert "day_of_week" in json_data
                assert len(json_data["menu_items"]) == 2

                assert json_data["menu_items"][0]["category"] == "polévka"
                assert json_data["menu_items"][0]["price"] == 45

                assert json_data["menu_items"][1]["category"] == "hlavní jídlo"
                assert json_data["menu_items"][1]["price"] == 145
                assert json_data["menu_items"][1]["weight"] == "150g"
