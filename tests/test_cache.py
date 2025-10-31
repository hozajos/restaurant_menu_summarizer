from unittest.mock import patch
from app import app


def test_cache_prevents_duplicate_llm_calls():
    app.config["TESTING"] = True

    cached_data = {
        "restaurant_name": "Cached Restaurant",
        "date": "2025-10-31",
        "day_of_week": "pátek",
        "menu_items": [],
        "daily_menu": True
    }

    with patch('app.get_cached_menu', return_value=cached_data):
        with patch('app.extract_menu_llm') as mock_llm:
            client = app.test_client()

            response = client.post("/", data={"url": "http://test.cz"})

            assert response.status_code == 200
            assert response.json["restaurant_name"] == "Cached Restaurant"
            assert mock_llm.call_count == 0
