import openai
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from exceptions import LlmApiError
from services.tools import normalize_price


load_dotenv()
OPENAI_API = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API:
    raise ValueError("Missing API key")

llm = OpenAI(api_key=OPENAI_API)


# schema pro llm structured output ne pro db
class MenuItem(BaseModel):
    category: str
    name: str
    price: int
    allergens: Optional[list[str]] = None
    weight: Optional[str] = None


class Menu(BaseModel):
    restaurant_name: Optional[str] = None
    # date: date
    # day_of_week: str - llm nevyplnuje, doplneno z backendu
    menu_items: list[MenuItem]
    daily_menu: bool


def extract_menu_llm(system_prompt, user_prompt, model, temperature):
    try:
        response = llm.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=Menu,
            temperature=temperature,
        )

        return response.output_parsed

    except openai.APIError as e:
        raise LlmApiError(f"OpenAI API error: {e}")
    except openai.APITimeoutError as e:
        raise LlmApiError(f"OpenAI timeout: {e}")
    except openai.RateLimitError as e:
        raise LlmApiError(f"OpenAI rate limit exceeded: {e}")
