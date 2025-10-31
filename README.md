# Menu Summarizer

Flask aplikace pro extrakci denního menu z webových stránek restaurací pomocí LLM.

## Jak spustit projekt

1. Vytvoř virtual environment:

python -m venv venv
source venv/bin/activate


2. Nainstaluj dependencies:

pip install -r requirements.txt


3. Nastav environment variables:

Do .env přidej svůj OpenAI API klíč:
OPENAI_API_KEY=sk-proj-...


4. Spusť aplikaci:

python app.py


5. Otevři v prohlížeči: http://localhost:3000

## Jak spustit testy

pytest tests/

Nebo s detaily:
pytest -v tests/

## Úvahy o řešení

Pro testování jsem použil URL: https://bistroprotiproudu.cz/menu

Zvolil jsem vlastní scraper (BeautifulSoup) jako levnější a rychlejší variantu místo LLM built-in search. Scraped text není moc očištěný, to je záměrné - chtěl jsem aby scraper fungoval pro více různých stránek bez nutnosti přizpůsobování konkrétní struktuře. Do budoucna by šlo přidat LLM search jako fallback v případech, kdy scraper nebude stačit - například když stránka nebude mít dostatek informací v HTML nebo když bude obsah v PDF místo HTML.

Pro LLM API jsem použil OpenAI gpt-4o-mini s kombinací function calling a structured outputs. Zajímavý problém bylo, že mi s OpenAI nešlo dělat function calling a structured output v jednom volání. Musel jsem udělat 2 LLM cally - první chat.completions.create pro tool calling (normalizace cen), druhý responses.parse pro strukturovanou response podle Pydantic modelu (viz dokumentace: https://platform.openai.com/docs/guides/structured-outputs). Výsledky z tools předávám jako text do druhého volání.

Caching jsem implementoval pomocí SQLite a Flask-SQLAlchemy. Cache klíč je URL + datum, protože menu se mění denně. Při startu aplikace se automaticky mažou staré záznamy. Druhý request na stejnou URL vrací data okamžitě z cache bez nového LLM volání.