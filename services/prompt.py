from datetime import datetime
from zoneinfo import ZoneInfo


def current_time_prague():
    prague_tz = ZoneInfo("Europe/Prague")
    now = datetime.now(prague_tz)
    return now.strftime("%Y-%m-%d")


def current_weekDay():
    czech_days = {
        0: "Pondělí",
        1: "Úterý",
        2: "Středa",
        3: "Čtvrtek",
        4: "Pátek",
        5: "Sobota",
        6: "Neděle",
    }

    now = datetime.now(ZoneInfo("Europe/Prague"))
    day_name = czech_days[now.weekday()]
    return day_name


SYSTEM_PROMPT = (
    "You are a helpful assistant that extracts the daily lunch menu from the provided text. "
    "Extract the restaurant name from the page content or URL if visible. "
    "Return only a valid JSON object with the required keys and types. "
    "Include ONLY items valid for TODAY (based on the provided date/day context). "
    "Allergens must be an array of strings (use [] if not listed). "
    "IMPORTANT: Do not hallucinate. Your response must be based solely on the given text."
)

CATEGORY = ["polévka", "hlavní jídlo", "dezert", "ostatní"]


def user_prompt(url, context_for_llm):
    weekDay_cz = current_weekDay()
    date = current_time_prague()

    return f"""
    Page url: {url}
    Curent date: {date}
    Current weekday: {weekDay_cz}

    TASK:
    From the text below, extract ONLY today's lunch menu.
    If the page shows a weekly menu, select the section valid for Today: {weekDay_cz} {date}.
    Ignore static/permanent offers.
    For each item, pick exactly one category from the allowed taxonomy: {CATEGORY}.
    Return ONLY the JSON object.

    TEXT:
    {context_for_llm[:6000]}
    """
