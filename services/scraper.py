import requests
from bs4 import BeautifulSoup
from exceptions import (
    ScrapeError,
    ScrapeTimeoutError,
    NetworkError,
    ContentNotFoundError,
    UpstreamServerError,
)

HEADERS = {"User-Agent": "MenuSummarizer (https://github.com/hozajos)"}

TIMEOUT = (5, 15)
MAX_CONTENT_LEN = 2_000_000


def check_html(response):
    content_type = response.headers.get("Content-Type", "")
    content_len = response.headers.get("Content-Length")
    if "text/html" not in content_type.lower():
        raise ContentNotFoundError(
            f"Expected content type is HTML but got: {content_type}"
        )
    if content_len and int(content_len) > MAX_CONTENT_LEN:  # nesmi byt none(type error)
        raise ScrapeError(f"Lenght of url content is too large: {content_len}")
    return content_type


def get_text(soup):
    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "head",
            "header",
            "footer",
            "form",
            "nav",
            "aside",
            "iframe",
            "svg",
            "img",
        ]
    ):
        tag.decompose()

    unwanted_selectors = [
        ".gallery",
        ".social",
        ".cookie",
        '[class*="toggle"]',
        '[id*="foto"]',
        '[id*="kontakt"]',
        '[id*="onas"]',
        '[class*="contact"]',
    ]

    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()

    text = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    filtered = [line for line in lines if len(line) > 2]

    return "\n".join(filtered)


def get_html_content(url):
    try:
        response = requests.get(
            url=url, timeout=TIMEOUT, allow_redirects=True, headers=HEADERS
        )
        response.raise_for_status()
        content_type = check_html(response)

        # print(response.text)

        soup = BeautifulSoup(response.text, "lxml")

        title = soup.title.get_text(strip=True) if soup.title else None
        cleaned_text = get_text(soup)
        print("page loaded successfully")
        print(cleaned_text)

        return {
            "url": str(response.url),
            "status": response.status_code,
            "content_type": content_type,
            "title": title,
            "text": cleaned_text,
        }

    except requests.exceptions.Timeout as e:
        raise ScrapeTimeoutError(f"Timeout fetching your url: {e}")

    except requests.exceptions.ConnectionError as e:
        raise NetworkError(f"Network issue error: {e}")

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else None
        if status == 404:
            raise ContentNotFoundError(f"Content of url cant be found error: {e}")
        elif status and 500 <= status <= 599:
            raise UpstreamServerError(f"Upstream server error {status}: {e}")
        else:
            raise ScrapeError(f"Error{status}: {e}")
    except Exception as e:
        raise ScrapeError(f"unexpected error: {e}")
