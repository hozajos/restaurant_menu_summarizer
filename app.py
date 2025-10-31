from flask import Flask, render_template, request, jsonify, redirect, Response
import os
from services.scraper import get_html_content
from exceptions import (
    ScrapeError,
    ScrapeTimeoutError,
    NetworkError,
    ContentNotFoundError,
    UpstreamServerError,
    LlmApiError,
)
import json
from services.llm import extract_menu_llm
from services.prompt import (
    current_time_prague,
    current_weekDay,
    SYSTEM_PROMPT,
    user_prompt,
)
from services.cache import db, get_cached_menu, save_menu_to_cache, cleanup_old_cache

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///menu_cache.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    cleanup_old_cache(current_time_prague())


@app.errorhandler(ContentNotFoundError)
def handle_404(e):
    return (
        jsonify({"ok": False, "error": {"code": "NOT_FOUND", "message": str(e)}}),
        404,
    )


@app.errorhandler(ScrapeTimeoutError)
def handle_504(e):
    return jsonify({"ok": False, "error": {"code": "TIMEOUT", "message": str(e)}}), 504


@app.errorhandler(UpstreamServerError)
def handle_502_upstream(e):
    return (
        jsonify({"ok": False, "error": {"code": "UPSTREAM_ERROR", "message": str(e)}}),
        502,
    )


@app.errorhandler(NetworkError)
def handle_502_net(e):
    return (
        jsonify({"ok": False, "error": {"code": "NETWORK_ERROR", "message": str(e)}}),
        502,
    )


@app.errorhandler(ScrapeError)
def handle_500(e):
    return (
        jsonify({"ok": False, "error": {"code": "SCRAPE_ERROR", "message": str(e)}}),
        500,
    )


@app.errorhandler(LlmApiError)
def handle_llm_error(e):
    return (
        jsonify({"ok": False, "error": {"code": "LLM_ERROR", "message": str(e)}}),
        500,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url or not url.strip():
            return (
                jsonify(
                    {
                        "ok": False,
                        "error": {
                            "code": "MISSING_URL",
                            "message": "URL parameter is required",
                        },
                    }
                ),
                400,
            )

        today_date = current_time_prague()
        cached_menu = get_cached_menu(url, today_date)

        if cached_menu:
            data = cached_menu
        else:
            scraped_data = get_html_content(url)
            scraped_text = scraped_data["text"]

            user_prompt_text = user_prompt(url, scraped_text)

            # call llm
            menu = extract_menu_llm(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt_text,
                model="gpt-4o-mini",
                temperature=0.0,
            )

            # convert each of the menu items to dict.
            menu_item_list = []
            for item in menu.menu_items:
                menu_item_list.append(item.model_dump())

            # structure the data
            data = {
                "restaurant_name": menu.restaurant_name,
                "date": today_date,
                "day_of_week": current_weekDay(),
                "menu_items": menu_item_list,
                "daily_menu": menu.daily_menu,
            }

            # Save to cache
            save_menu_to_cache(url, today_date, data)

        json.dumps(data, ensure_ascii=False)  # python dict -> to formatted JSON

        return Response(
            json.dumps(data, ensure_ascii=False, indent=2),
            mimetype="application/json; charset=utf-8",
        )

    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
