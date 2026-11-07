import pycountry

from pydantic import field_validator


def normalize_country_code(value: str) -> str:
    """Normalize and validate an ISO 3166-1 alpha-2 country code."""
    if not isinstance(value, str):
        raise ValueError("Country code must be a string")

    code = value.strip().upper()

    if len(code) != 2:
        raise ValueError("Country code must contain exactly 2 characters")

    if pycountry.countries.get(alpha_2=code) is None:
        raise ValueError(f"Invalid ISO 3166-1 alpha-2 country code: {code}")

    return code


def normalize_currency_code(value: str) -> str:
    """Normalize and validate an ISO 4217 currency code."""
    if not isinstance(value, str):
        raise ValueError("Currency code must be a string")

    code = value.strip().upper()

    if len(code) != 3:
        raise ValueError("Currency code must contain exactly 3 characters")

    currency = pycountry.currencies.get(alpha_3=code)

    if currency is None:
        raise ValueError(f"Invalid ISO 4217 currency code: {code}")

    return code
