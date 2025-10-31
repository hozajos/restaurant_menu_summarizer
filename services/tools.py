import re


def normalize_price(price_string):
    """
    Normalize price from various formats to integer.

    Examples:
    "145,-" - 145
    "145 Kč" - 145
    "145,50" - 146 (rounds up)
    "145.50" - 146
    """

    cleaned = re.sub(
        r"[Kč\s-]", "", price_string
    )  # Remove currency symbols, dashes, spaces

    cleaned = cleaned.replace(",", ".")  # Replace comma with dot for decimal

    # Convert to float first, then round to int
    try:
        return round(float(cleaned))
    except ValueError:
        return 0


PRICE_NORMALIZATION_TOOL = {
    "type": "function",
    "function": {
        "name": "normalize_price",
        "description": "Parse and normalize price from various formats (example: '145,-', '145 Kč', '145,50') to integer",
        "parameters": {
            "type": "object",
            "properties": {
                "price_string": {
                    "type": "string",
                    "description": "The price string to normalize (example:'145,-', '145 Kč')",
                }
            },
            "required": ["price_string"],
        },
    },
}
