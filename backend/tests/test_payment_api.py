import pytest


async def create_business(client, name):
    response = await client.post(
        "/api/v1/businesses",
        json={
            "legal_name": name,
            "country_code": "NG",
            "base_currency": "NGN",
        },
    )
    assert response.status_code == 201
    return response.json()


async def create_vendor(client, business_id, name="Test Vendor"):
    response = await client.post(
        f"/api/v1/businesses/{business_id}/vendors",
        json={
            "name": name,
            "country_code": "US",
            "preferred_currency": "USD",
        },
    )
    assert response.status_code == 201
    return response.json()


async def create_payment(client, business_id, vendor_id, **overrides):
    payload = {
        "vendor_id": vendor_id,
        "source_amount": "100000.00",
        "destination_currency": "USD",
        "purpose": "Supplier invoice payment",
    }
    payload.update(overrides)

    return await client.post(
        f"/api/v1/businesses/{business_id}/payments",
        json=payload,
    )


@pytest.mark.asyncio
async def test_supported_currencies(client):
    business = await create_business(client, "Currency Test Limited")

    response = await client.get(
        f"/api/v1/businesses/{business['id']}/payments/supported-currencies"
    )

    assert response.status_code == 200

    data = response.json()
    currencies = {item["currency"] for item in data["rates"]}

    assert data["funding_currency"] == "NGN"
    assert currencies == {"USD", "GBP", "EUR", "CAD", "GHS"}
    assert data["rate_type"] == "illustrative_demo_rate"


@pytest.mark.asyncio
async def test_create_payment_calculates_amounts_correctly(client):
    business = await create_business(client, "Payment Test Limited")
    vendor = await create_vendor(client, business["id"])

    response = await create_payment(
        client, business["id"], vendor["id"]
    )

    assert response.status_code == 201

    payment = response.json()

    assert payment["source_currency"] == "NGN"
    assert payment["destination_currency"] == "USD"
    assert float(payment["source_amount"]) == 100000.00
    assert float(payment["exchange_rate"]) == 1500.00
    assert float(payment["destination_amount"]) == 66.67
    assert float(payment["fee_amount"]) == 1500.00
    assert float(payment["total_debit"]) == 101500.00
    assert payment["status"] == "pending_confirmation"
    assert payment["confirmed_at"] is None
    assert payment["reference"].startswith("TF-")


@pytest.mark.asyncio
async def test_unsupported_currency_is_rejected(client):
    business = await create_business(client, "Invalid Currency Limited")
    vendor = await create_vendor(client, business["id"])

    response = await create_payment(
        client,
        business["id"],
        vendor["id"],
        destination_currency="JPY",
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_zero_amount_is_rejected(client):
    business = await create_business(client, "Invalid Amount Limited")
    vendor = await create_vendor(client, business["id"])

    response = await create_payment(
        client,
        business["id"],
        vendor["id"],
        source_amount="0",
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_vendor_from_another_business_is_rejected(client):
    owner = await create_business(client, "Vendor Owner Limited")
    other = await create_business(client, "Other Business Limited")
    vendor = await create_vendor(client, owner["id"])

    response = await create_payment(
        client, other["id"], vendor["id"]
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Active vendor not found in this business"
    )


@pytest.mark.asyncio
async def test_simulated_payment_confirmation(client):
    business = await create_business(client, "Confirmation Test Limited")
    vendor = await create_vendor(client, business["id"])

    created = await create_payment(
        client, business["id"], vendor["id"]
    )
    payment_id = created.json()["id"]

    response = await client.post(
        f"/api/v1/businesses/{business['id']}/payments/{payment_id}/confirm",
        json={},
    )

    assert response.status_code == 200

    payment = response.json()

    assert payment["status"] == "simulated_success"
    assert payment["confirmed_at"] is not None


@pytest.mark.asyncio
async def test_payment_cannot_be_confirmed_twice(client):
    business = await create_business(client, "Duplicate Confirmation Limited")
    vendor = await create_vendor(client, business["id"])

    created = await create_payment(
        client, business["id"], vendor["id"]
    )
    payment_id = created.json()["id"]

    first = await client.post(
        f"/api/v1/businesses/{business['id']}/payments/{payment_id}/confirm",
        json={},
    )
    second = await client.post(
        f"/api/v1/businesses/{business['id']}/payments/{payment_id}/confirm",
        json={},
    )

    assert first.status_code == 200
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_payment_history_is_scoped_to_business(client):
    business_a = await create_business(client, "History Owner Limited")
    business_b = await create_business(client, "History Other Limited")

    vendor_a = await create_vendor(client, business_a["id"])

    created = await create_payment(
        client, business_a["id"], vendor_a["id"]
    )
    assert created.status_code == 201

    response_a = await client.get(
        f"/api/v1/businesses/{business_a['id']}/payments"
    )
    response_b = await client.get(
        f"/api/v1/businesses/{business_b['id']}/payments"
    )

    assert response_a.status_code == 200
    assert response_b.status_code == 200
    assert len(response_a.json()) == 1
    assert response_b.json() == []
