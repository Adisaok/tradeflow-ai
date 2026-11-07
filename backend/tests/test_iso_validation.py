import pytest
from pydantic import ValidationError

from app.schemas.business import BusinessCreate
from app.schemas.vendor import VendorCreate, VendorUpdate


@pytest.mark.parametrize(
    "country_code, expected",
    [
        ("ng", "NG"),
        ("NG", "NG"),
        ("us", "US"),
        ("gb", "GB"),
        ("st", "ST"),
    ],
)
def test_valid_business_country_codes(country_code, expected):
    business = BusinessCreate(
        legal_name="Test Business",
        country_code=country_code,
        base_currency="NGN",
    )
    assert business.country_code == expected


@pytest.mark.parametrize("country_code", ["XX", "NGA", "123", ""])
def test_invalid_business_country_codes(country_code):
    with pytest.raises(ValidationError):
        BusinessCreate(
            legal_name="Test Business",
            country_code=country_code,
            base_currency="NGN",
        )


@pytest.mark.parametrize(
    "currency_code, expected",
    [
        ("ngn", "NGN"),
        ("usd", "USD"),
        ("eur", "EUR"),
        ("gbp", "GBP"),
    ],
)
def test_valid_business_currency_codes(currency_code, expected):
    business = BusinessCreate(
        legal_name="Test Business",
        country_code="NG",
        base_currency=currency_code,
    )
    assert business.base_currency == expected


@pytest.mark.parametrize("currency_code", ["XYZ", "STR", "US", "123", ""])
def test_invalid_business_currency_codes(currency_code):
    with pytest.raises(ValidationError):
        BusinessCreate(
            legal_name="Test Business",
            country_code="NG",
            base_currency=currency_code,
        )


def test_vendor_codes_are_normalized():
    vendor = VendorCreate(
        name="Test Vendor",
        country_code="us",
        preferred_currency="usd",
    )

    assert vendor.country_code == "US"
    assert vendor.preferred_currency == "USD"


@pytest.mark.parametrize(
    "country_code, currency_code",
    [
        ("XX", "USD"),
        ("US", "XYZ"),
    ],
)
def test_invalid_vendor_codes_are_rejected(country_code, currency_code):
    with pytest.raises(ValidationError):
        VendorCreate(
            name="Test Vendor",
            country_code=country_code,
            preferred_currency=currency_code,
        )


def test_vendor_update_rejects_invalid_country():
    with pytest.raises(ValidationError):
        VendorUpdate(country_code="XX")


def test_vendor_update_rejects_invalid_currency():
    with pytest.raises(ValidationError):
        VendorUpdate(preferred_currency="XYZ")


def test_vendor_update_accepts_valid_partial_update():
    update = VendorUpdate(preferred_currency="eur")

    assert update.preferred_currency == "EUR"
    assert update.model_dump(exclude_unset=True) == {
        "preferred_currency": "EUR"
    }


def test_vendor_update_allows_omitted_iso_fields():
    update = VendorUpdate(notes="Updated vendor information")

    assert update.model_dump(exclude_unset=True) == {
        "notes": "Updated vendor information"
    }
