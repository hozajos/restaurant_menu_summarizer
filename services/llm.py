import openai
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
import os
import json
from dotenv import load_dotenv
from exceptions import LlmApiError
from services.tools import normalize_price, PRICE_NORMALIZATION_TOOL


load_dotenv()
OPENAI_API = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API:
    raise ValueError("Missing API key")

llm = OpenAI(api_key=OPENAI_API)


# schema for llm structured not for db
class MenuItem(BaseModel):
    category: str
    name: str
    price: int
    allergens: Optional[list[str]] = None
    weight: Optional[str] = None


class Menu(BaseModel):
    restaurant_name: Optional[str] = None
    # date: date
    # day_of_week: str - dates will be filled form backend logic not by llm
    menu_items: list[MenuItem]
    daily_menu: bool


def extract_menu_llm(system_prompt, user_prompt, model, temperature):
    try:
        tool_map = {"normalize_price": normalize_price}

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # 1. call with tools
        initial_response = llm.chat.completions.create(
            model=model,
            messages=messages,
            tools=[PRICE_NORMALIZATION_TOOL],
            tool_choice="auto",
            temperature=temperature,
        )

        response_message = initial_response.choices[0].message
        tool_calls = response_message.tool_calls

        tool_results_text = []
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                if function_name in tool_map:
                    # Execute Python function
                    function_args = json.loads(tool_call.function.arguments)
                    result = tool_map[function_name](**function_args)
                    tool_results_text.append(f"Tool {function_name} returned: {result}")

        parse_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if tool_results_text:
            parse_messages.append(
                {
                    "role": "assistant",
                    "content": "I called tools and got these results: "
                    + "; ".join(tool_results_text)
                    + ". Now extracting menu..",
                }
            )

        # 2. call with structured output (responses.parse)
        final_response = llm.responses.parse(
            model=model,
            input=parse_messages,
            text_format=Menu,
            temperature=temperature,
        )

        return final_response.output_parsed

    except openai.APIError as e:
        raise LlmApiError(f"OpenAI API error: {e}")
    except openai.APITimeoutError as e:
        raise LlmApiError(f"OpenAI timeout: {e}")
    except openai.RateLimitError as e:
        raise LlmApiError(f"OpenAI rate limit exceeded: {e}")
